#!/usr/bin/env python
# coding=utf-8

import re

from Util.util import *
from Kube.template import *
from Util.log import Logger as logger
from Kube import render


class KubeInit:
    def __init__(self, conf):
        self.conf = conf

        self.init_config_file = os.path.join(conf.kube_init_path, "init.yaml")
        self.kube_network_plugin = os.path.join(
            conf.kube_init_path, "kube-{}.yaml".format(conf.kube_network_plugin_name)
        )

        self.kube_first_master_ipaddr = conf.master["servers"][0]
        self.kube_other_master_ipaddr = conf.master["servers"][1:]
        self.kube_node_ipaddr = conf.node["servers"]

        self.config_dir = os.path.join(self.conf.base_dir, "Files/configs")
        self.plugin_dir = os.path.join(self.conf.base_dir, "Files/plugin")
        self.script_dir = os.path.join(self.conf.base_dir, "Files/scripts")

    def init_docker_env(self):
        logger.get().info("初始化docker环境")
        ips = self.conf.all_ip
        init_script = os.path.join(self.script_dir, "init_env.sh")
        target = os.path.join(self.conf.kube_init_path, "init_env.sh")
        cmd = RUN_SHELL.format(FILE=target)
        logger.get().debug(cmd)
        for ip in ips:
            Copy(self.conf.ssh_user, ip, init_script, target)
            RunCmdHost(self.conf.ssh_user, ip, cmd)

    def init_master_node(self, ip=""):
        if ip == "":
            ip = self.kube_first_master_ipaddr
        logger.get().info("初始化父master节点，ip地址{}".format(ip))
        render.fill_kubeadm_init_config(self.conf)
        src = os.path.join(self.config_dir, "init.yaml")
        logger.get().info("渲染kubeadm 初始化文件: {}".format(src))
        dest = self.init_config_file
        Copy(self.conf.ssh_user, ip, src, dest)
        cmd = INIT_ADMIN.format(CONFIG_PATH=dest)
        logger.get().debug(cmd)
        RunCmdHost(self.conf.ssh_user, ip, cmd)

    def sync_kubernetes_config(self, ips):
        kube_config_dir = "/etc/kubernetes/pki/"
        for ip in ips:
            logger.get().info("分发k8s pki文件到 {}".format(ip))
            Copy(self.conf.ssh_user, ip, kube_config_dir, kube_config_dir, type="dir")

    def init_other_master_node(self):
        self.sync_kubernetes_config(self.kube_other_master_ipaddr)
        src = os.path.join(self.config_dir, "init.yaml")
        dest = self.init_config_file
        cmd = INIT_ADMIN.format(CONFIG_PATH=dest)
        logger.get().debug(cmd)
        for ip in self.kube_other_master_ipaddr:
            logger.get().info("初始化子master节点: {}".format(ip))
            Copy(self.conf.ssh_user, ip, src, dest)
            RunCmdHost(self.conf.ssh_user, ip, cmd)

    def init_network_plugin(self):
        logger.get().info("初始化网络插件flannel")
        render.fill_network_plugin(self.conf)
        cmd = DEPLOY_NETWORK_PLUGIN.format(PLUGIN_CONFIG=self.kube_network_plugin)
        src = os.path.join(self.plugin_dir, "kube-{}.yaml".format(self.conf.kube_network_plugin_name))
        dest = self.kube_network_plugin
        logger.get().debug(cmd)
        Copy(self.conf.ssh_user, self.kube_first_master_ipaddr, src, dest)
        RunCmdHost(self.conf.ssh_user, self.kube_first_master_ipaddr, cmd)

    def join_cluster(self):
        cmd = self.generic_admin_token()
        logger.get().debug(cmd)
        for ip in self.conf.node["servers"]:
            logger.get().info("node节点: {} 加入".format(ip))
            RunCmdHost(self.conf.ssh_user, ip, cmd)

    def generic_admin_token(self):
        logger.get().info("生成kubeadmin token")
        cmd = GENERIC_ADMIN_TOKEN.format(CONFIG_PATH=self.init_config_file)
        logger.get().debug(cmd)
        ret = RunCmdHostWithReturns(
            self.conf.ssh_user, self.kube_first_master_ipaddr, cmd
        )
        return re.findall(r"kubeadm.*", ret)[0]

    def cp_config(self):
        logger.get().info("生成kubectl config文件")
        RunCmdHost(self.conf.ssh_user, self.kube_first_master_ipaddr, "mkdir ~/.kube")
        RunCmdHost(
            self.conf.ssh_user,
            self.kube_first_master_ipaddr,
            "cp /etc/kubernetes/admin.conf ~/.kube/config",
        )

    def check_cluster_status(self):
        logger.get().info("查看node状态")
        RunCmdHost(
            self.conf.ssh_user, self.kube_first_master_ipaddr, "kubectl get node"
        )

    def check_network_pods_status(self):
        logger.get().info("查看网络插件状态")
        RunCmdHost(
            self.conf.ssh_user,
            self.kube_first_master_ipaddr,
            "kubectl get po -n kube-system | grep flannel",
        )

    def reset(self, ips):
        logger.get().info("重置k8s环境")
        RunCmdHost(self.conf.ssh_user, self.kube_first_master_ipaddr, "rm -fr ~/.kube")
        for ip in ips:
            RunCmdHost(self.conf.ssh_user, ip, "kubeadm reset -f")

    def remove_taint(self):
        cmd = "kubectl taint nodes {} node-role.kubernetes.io/master-"
        for i in range(len(self.kube_other_master_ipaddr)):
            node = "%s%02d" % (self.conf.node["server_name_prefix"], i + 2)
            logger.get().info("移除{}上的taint".format(node))
            cmd = cmd.format(node)
            logger.get().debug(cmd)
            RunCmdHost(self.conf.ssh_user, self.kube_first_master_ipaddr, cmd)

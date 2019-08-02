#!/bin/env python
# -*- encoding: utf-8 -*-
import os

from Kube.init import KubeInit
from Util.args import Args
from Util.log import Logger as logger
from Util.conf import Conf as conf
from Util import util

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
CONF_PATH = os.path.join(BASE_DIR, "config.yaml")

def main(params):
    if params.configFile:
        logger.get().debug("加载配置文件{}".format(params.configFile))
        conf.add_conf(params.configFile)
        conf.init()
    else:
        logger.get().debug("加载配置文件{}".format(CONF_PATH))
        conf.add_conf(CONF_PATH)
        conf.init()
    conf.set("base_dir", BASE_DIR)
    conf.set("all_ip", conf.master['servers'] + conf.node['servers'])

    kube = KubeInit(conf)


    if params.initAnsible:
        passwd = input("请输入ssh密码:")
        util.CreateNoPasswdLogin(conf.all_ip, conf.ssh_user, passwd, conf.ssh_port)
        util.CreateAnsibleInventory(conf)
        util.UpdateHosts(conf)


    if params.initEnv:
        if not os.path.isfile("/etc/ansible/hosts"):
            logger.get().error("ansibe host文件不存在")
            exit(1)
        kube.init_docker_env()

    if params.initMaster:
        kube.init_master_node()
        kube.cp_config()
        kube.check_cluster_status()
        kube.init_network_plugin()

    if params.initOthers:
        kube.init_other_master_node()
        kube.check_cluster_status()

    if params.Join:
        kube.join_cluster()

    if params.Reset:
        kube.reset(conf.all_ip)


if __name__ == "__main__":

    if not os.getenv("LOG_LEVEL"):
        logger.start("INFO")
    else:
        logger.start(os.getenv("LOG_LEVEL"))

    params, unparsed = Args.get().parse_known_args()
    # print(args)
    main(params)

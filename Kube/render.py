#!/usr/bin/env python
# coding=utf-8
import os

from Util.fill import FillConfigUtil


def fill_kubeadm_init_config(conf):
    template = os.path.join(conf.base_dir, "Templates/kubernetes/kubeadmin-init.yaml")
    target = os.path.join(conf.base_dir, "Files/configs/init.yaml")

    data = conf.all_property
    data["hosts"] = conf.master["servers"]
    data["hosts"].append(conf.apiserver_proxy_address)
    nodes = []
    for i in range(len(conf.master["servers"])):
        nodes.append("%s%02d" % (conf.master["server_name_prefix"], i + 1))
    data["hosts"] += nodes

    FillConfigUtil(template, target, data)


def fill_network_plugin(conf):
    template = os.path.join(
        conf.base_dir,
        "Templates/plugin/kube-{}.yaml".format(conf.kube_network_plugin_name)
    )
    target = os.path.join(
        conf.base_dir,
        "Files/plugin/kube-{}.yaml".format(conf.kube_network_plugin_name)
    )
    FillConfigUtil(template, target, conf.all_property)

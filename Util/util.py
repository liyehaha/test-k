#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function
from Util.log import Logger as logger
from Kube import template

import os

def Copy(user, host, src, dest, type="file"):
    create_dir_tmpl = template.ANSIBLE_CREATE_DIR
    #create_file_tmpl = 'ansible all -i "{HOST}," -u {USER} -m file -a "path={DEST} state=touch" '
    dest_dir = ""

    if type == "file":
        dest_dir = os.path.dirname(dest)
    elif type == "dir":
        dest_dir = dest
    # make sure remote dir is exist
    create_dir = create_dir_tmpl.format(
        USER=user,
        HOST=host,
        DEST=dest_dir
    )
    logger.get().debug(create_dir)
    os.system(create_dir)

    #if type == "file":
    #    create_file = create_file_tmpl.format(
    #        USER=user,
    #        HOST=host,
    #        DEST=dest
    #    )
    #    logger.get().debug(create_file)
    #    os.system(create_file)

    cmd_tmpl = 'ansible all -i "{HOST}," -u {USER} -m copy -a "src={SRC} dest={DEST}" '.format(
        USER=user,
        HOST=host,
        SRC=src,
        DEST=dest
    )
    logger.get().debug(cmd_tmpl)
    os.system(cmd_tmpl)

def RunCmdGroup(user, ansible_group, cmd):
    cmd_tmpl = template.ANSIBLE_RUN_SHELL_GROUP.format(
        GROUP=ansible_group,
        USER=user,
        CMD=cmd
    )
    logger.get().debug(cmd_tmpl)
    os.system(cmd_tmpl)

def RunCmdHost(user, host, cmd):
    cmd_tmpl = template.ANSIBLE_RUN_SHELL_HOST.format(
        HOST=host,
        USER=user,
        CMD=cmd
    )
    logger.get().debug(cmd_tmpl)
    os.system(cmd_tmpl)

def RunCmdHostWithReturns(user, host, cmd):
    cmd_tmpl = template.ANSIBLE_RUN_SHELL_HOST.format(
        HOST=host,
        USER=user,
        CMD=cmd
    )
    logger.get().debug(cmd_tmpl)
    return os.popen(cmd_tmpl).read()

def CreateNoPasswdLogin(ips, user, password, port=22):
    default_pub_key = "~/.ssh/id_rsa.pub"
    default_pvt_key = "~/.ssh/id_rsa"
    if not os.path.isfile(default_pub_key):
        os.system("ssh-keygen -f {} -P '' ".format(default_pvt_key))
    cmd_tmpl = template.CREATE_SSH_LOGIN
    for ip in ips:
        cmd = cmd_tmpl.format(
            ssh_password=password,
            ssh_key_pub=default_pub_key,
            ssh_port=port,
            ssh_user=user,
            host_ip=ip
        )
        logger.get().debug(cmd)
        os.system(cmd)

def UpdateHosts(conf):
    host_lines = ""
    for i in range(len(conf.master["servers"])):
        host_lines += template.HOST_LINE.format(
            IP=conf.master["servers"][i],
            HOST="%s%02d" % (conf.master["server_name_prefix"], i + 1)
        )
        cmd = template.SET_HOSTNAME.format(NAME="%s%02d" % (conf.master["server_name_prefix"], i + 1))
        RunCmdHost(conf.ssh_user, conf.master["servers"][i], cmd)
    for i in range(len(conf.node["servers"])):
        host_lines += template.HOST_LINE.format(
            IP=conf.node["servers"][i],
            HOST="%s%02d" % (conf.node["server_name_prefix"], i + 1)
        )
        cmd = template.SET_HOSTNAME.format(NAME="%s%02d" % (conf.node["server_name_prefix"], i + 1))
        RunCmdHost(conf.ssh_user, conf.node["servers"][i], cmd)
    logger.get().debug(host_lines)
    host_add_content = template.HOST_TMPL.format(
        HOSTS=host_lines
    )
    logger.get().debug(host_add_content)
    RunCmdGroup(conf.ssh_user, "all", "cp -f /etc/hosts /etc/hosts.bak$(date '+%Y%m%d%H%M%S')")
    def save_to_file(content, file_path):
        if os.path.isfile(file_path) or not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)

    save_to_file(host_add_content, "/tmp/addhost.sh")
    run_script = """ansible all -u {USER} -m script -b -a "{SCRIPT}" """.format(
        USER=conf.ssh_user,
        SCRIPT="/tmp/addhost.sh"
    )
    os.system(run_script)
    RunCmdGroup(conf.ssh_user, "all", "rm -f /tmp/addhost.sh")

def CreateAnsibleInventory(conf):

    master_host_lines = ""
    node_host_lines = ""
    inventory_content = ""
    for i in range(len(conf.master["servers"])):
        master_host_lines += template.ANSIBLE_PER_HOST.format(
            HOST_IP=conf.master["servers"][i],
            HOST_NAME="%s%02d" % (conf.master["server_name_prefix"], i + 1)
        )
    inventory_content += template.ANSIBLE_INVENTORY.format(
        GROUP_NAME='kube-master',
        ALL_HOST= master_host_lines
    )
    for i in range(len(conf.node["servers"])):
        node_host_lines += template.ANSIBLE_PER_HOST.format(
            HOST_IP=conf.node["servers"][i],
            HOST_NAME="%s%02d" % (conf.node["server_name_prefix"], i + 1)
        )
    inventory_content += template.ANSIBLE_INVENTORY.format(
        GROUP_NAME='kube-node',
        ALL_HOST= node_host_lines
    )
    logger.get().debug(inventory_content)
    if not os.path.exists("/etc/ansible"):
        os.makedirs("/etc/ansible")
    with open("/etc/ansible/hosts", "w") as f:
        try:
            f.write(inventory_content)
        finally:
            f.close()

    os.system('ansible all -u {} -m ping'.format(conf.ssh_user))
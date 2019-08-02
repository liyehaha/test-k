#!/usr/bin/env python
# coding=utf-8

SET_HOSTNAME = "hostnamectl set-hostname {NAME}"

INIT_ADMIN = "kubeadm init --config {CONFIG_PATH}"

GENERIC_ADMIN_TOKEN = "kubeadm token create --print-join-command --config {CONFIG_PATH}"

DEPLOY_NETWORK_PLUGIN = "kubectl apply -f {PLUGIN_CONFIG}"

RUN_SHELL = "/bin/bash {FILE}"

CREATE_SSH_LOGIN = """sshpass -p{ssh_password} ssh-copy-id -i {ssh_key_pub} -p{ssh_port} -o StrictHostKeyChecking=no {ssh_user}@{host_ip} """

ANSIBLE_PER_HOST = """
{HOST_NAME} ansible_ssh_host={HOST_IP} ansible_ssh_private_key_file='~/.ssh/id_rsa'
"""

ANSIBLE_INVENTORY = """[{GROUP_NAME}]
{ALL_HOST}
"""

ANSIBLE_CREATE_DIR = 'ansible all -i "{HOST}," -u {USER} -m file -a "path={DEST} state=directory" '

ANSIBLE_RUN_SHELL_GROUP = 'ansible {GROUP} -u {USER} -m shell -b -a "{CMD}"'
ANSIBLE_RUN_SHELL_HOST = 'ansible all -i "{HOST}," -u {USER} -m shell -b -a "{CMD}"'


HOST_LINE = """{IP} {HOST}
"""
HOST_TMPL = """cat <<EOF >>  /etc/hosts
{HOSTS}
EOF"""
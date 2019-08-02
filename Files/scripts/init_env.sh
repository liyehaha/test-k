#!/bin/bash

# 关闭防火墙
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# 关闭selinux
sudo setenforce 0
sudo cp -p /etc/selinux/config /etc/selinux/config.bak$(date '+%Y%m%d%H%M%S')
sudo sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config

# 关闭swap
sudo swapoff -a
unalias cp
if [[ ! -f "/etc/fstab.bak" ]]; then
    sudo cp -a /etc/fstab /etc/fstab.bak
else
    sudo cp -af /etc/fstab.bak /etc/fstab
fi
sed -i "s/\/dev\/mapper\/rhel-swap/\#\/dev\/mapper\/rhel-swap/g" /etc/fstab
sed -i "s/\/dev\/mapper\/centos-swap/\#\/dev\/mapper\/centos-swap/g" /etc/fstab
mount -a

# 设置内核参数
cat <<EOF >  /etc/sysctl.d/kc.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-arptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
vm.max_map_count = 655350
net.netfilter.nf_conntrack_max = 2097152
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.all.arp_announce = 2
net.ipv4.tcp_max_syn_backlog = 1024
EOF

sysctl --system

# 设置系统限制
cat <<EOF > /etc/security/limits.d/10-kc.conf
* hard nofile 655350
* soft nofile 655350
root hard nofile 655350
root soft nofile 655350
EOF

# 开启ipvs
cat > /etc/sysconfig/modules/ipvs.modules <<EOF
#!/bin/bash
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack_ipv4
EOF
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod | grep -e ip_vs -e nf_conntrack_ipv4


if [[ ! -d "/etc/yum.repos.d/backup" ]]; then
    sudo mkdir /etc/yum.repos.d/backup
fi
sudo mv /etc/yum.repos.d/* /etc/yum.repos.d/backup

sudo cat << EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

sudo wget http://mirrors.aliyun.com/repo/Centos-7.repo -O /etc/yum.repos.d/CentOS-Base.repo
sudo wget http://mirrors.aliyun.com/repo/epel-7.repo -O /etc/yum.repos.d/epel.repo
sudo wget https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo -O /etc/yum.repos.d/docker-ce.repo

sudo yum clean all
sudo yum makecache -y

yum install -y kubelet-1.13.0 kubeadm-1.13.0 kubectl-1.13.0 ipvsadm ipset docker-ce docker-compose kubernetes-cni-0.6.0 device-mapper-persistent-data lvm2 nfs-utils python-devel iotop htop httpie

#启动docker
systemctl enable docker && systemctl start docker

#设置kubelet开机自启动
systemctl enable kubelet

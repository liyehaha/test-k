# k8s集群自动化部署

### 功能
- 一键安装k8s集群
- 完全基于开源工具实现

### 特性
- 轻量级
- 可选的node和master节点数量
- 一键部署
 
### 安装运行依赖

需要一个代理代理到k8s master节点的6443端口

`yum -y install python36 pip36 ansible`

`pip3 install -r requirements.txt`


### 初始化集群

```shell
python3 deploy-k8s.py --init-env
python3 deploy-k8s.py --init-ansible
python3 deploy-k8s.py --init-master
python3 deploy-k8s.py --init-others
python3 deploy-k8s.py --join


# 帮助
python3 deploy-k8s.py --help
```

### TODO

- 初始化监控工具
- 初始化集群管理工具
- 自动代理配置
- 多网络插件适配
- 指定版本
# k8s集群自动化部署

### 功能
- 一键安装k8s集群
- 完全基于开源工具实现

### 特性
- 轻量级
- 可选的node和master节点数量
- 一键部署
 
### 安装运行依赖

`yum -y install python36 pip36`

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
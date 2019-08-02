initmaster:
	python3 deploy-k8s.py --init-master
	python3 deploy-k8s.py --init-others

join:
	python3 deploy-k8s.py --join

initenv:
	python3 deploy-k8s.py --init-env

initansible:
	python3 deploy-k8s.py --init-ansible

all: initansible initenv initmaster join
	@echo "init all"

help:
	@echo "一键部署kubernetes"
	@echo
	@echo " initmaster              - 初始化master节点"
	@echo " join                    - 加入node节点"
	@echo " initenv                 - 初始化docker环境"
	@echo " initansible             - 创建无密码登录"
	@echo " all                     - 从裸系统开始"
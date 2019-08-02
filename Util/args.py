#!/bin/env python
# -*- encoding: utf-8 -*-
import argparse

class Args(object):

    @classmethod
    def get(cls):
        cls.parser = argparse.ArgumentParser()

        cls.parser.add_argument(
            '-c',
            '--conf',
            dest="configFile",
            type=str,
            help="项目配置文件路径")

        cls.parser.add_argument(
            '--init-master',
            dest="initMaster",
            action="store_true",
            default=False,
            help="初始化k8s master父节点")

        cls.parser.add_argument(
            '--init-others',
            dest="initOthers",
            action="store_true",
            default=False,
            help="初始化k8s master子节点")

        cls.parser.add_argument(
            '--init-env',
            dest="initEnv",
            action="store_true",
            default=False,
            help="初始化docker环境")

        cls.parser.add_argument(
            '--init-ansible',
            dest="initAnsible",
            action="store_true",
            default=False,
            help="初始化ansible环境")

        cls.parser.add_argument(
            '--reset',
            dest="Reset",
            action="store_true",
            default=False,
            help="重置k8s集群")

        cls.parser.add_argument(
            '--join',
            dest="Join",
            action="store_true",
            default=False,
            help="加入node节点")

        return cls.parser
#!/bin/env python
# -*- encoding: utf-8 -*-
import os
import yaml
import re


class Conf(object):
    _conf_file = []
    all_property = {}

    @classmethod
    def add_conf(cls, conf):
        if os.path.isfile(conf):
            cls._conf_file.append(conf)
        elif os.path.isdir(conf):
            for i in os.listdir(conf):
                if re.match(r".*\.(yaml|yml)", i):
                    cls._conf_file.append(os.path.join(conf, i))

    @classmethod
    def init(cls):
        setattr(cls, "all_property", {})
        conf_dict = {}
        for c in cls._conf_file:
            if os.path.exists(c):
                conf_dict.update(yaml.load(open(c), Loader=yaml.Loader))
        for k, v in conf_dict.items():
            cls.set(k, v)

    @classmethod
    def set(cls, key, value):
        setattr(cls, key, value)
        cls.all_property[key] = value

    @classmethod
    def reset(cls):
        cls._conf_file = []
        cls.all_property = {}

    @classmethod
    def reload(cls, conf_file):
        cls.reset()
        cls.add_conf(conf_file)
        cls.init()

    @classmethod
    def debug(cls):
        return cls._conf_file


if __name__ == "__main__":
    Conf.add_conf("../config.yaml")
    Conf.init()
    print(Conf.debug())
    Conf.reset()
    print(Conf.all_property)
    Conf.add_conf("../config.yaml")
    Conf.init()
    print(Conf.all_property)
    Conf.set("a", 123)
    print(Conf.a)

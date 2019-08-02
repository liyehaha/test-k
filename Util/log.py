#!/bin/env python
# -*- encoding: utf-8 -*-
import logging


class Logger(object):
    _inst = None

    _level_dict = {
        'ERROR': logging.ERROR,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }

    _log_level_format = {
        'DEBUG': {
            'level': logging.DEBUG,
            'format': '[%(levelname)s] %(asctime)s, pid=%(process)d, src=%(filename)s:%(lineno)d, %(message)s'
        },
        'INFO': {
            'level': logging.INFO,
            'format': '[%(levelname)s] %(asctime)s, %(message)s'
        },
        'ERROR': {
            'level': logging.ERROR,
            'format': '[%(levelname)s] %(asctime)s, %(message)s'
        }
    }

    @classmethod
    def start(cls, level):
        if cls._inst is not None:
            return cls._inst
        if level in cls._log_level_format:
            fmt = cls._log_level_format[level]['format']
            log_level = cls._log_level_format[level]['level']
        else:
            fmt = cls._log_level_format['DEBUG']['format']
            log_level = cls._log_level_format['DEBUG']['level']

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M')
        console_handler.setFormatter(formatter)
        cls._inst = logging.getLogger('private-deploy')
        cls._inst.setLevel(log_level)
        cls._inst.addHandler(console_handler)

    @classmethod
    def get(cls):
        return cls._inst
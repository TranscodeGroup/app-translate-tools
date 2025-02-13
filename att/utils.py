#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


def p(*values):
    print(*values, sep=', ')


def h(*args, **kwargs):
    """仅仅用来写注释..."""
    pass


class Dict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __missing__(self, key):
        return None


class KeyValueConverter:
    def __init__(self, **kw):
        self.key2value = dict()
        self.value2key = dict()
        for (key, value) in kw.items():
            self.put(key, value)

    def put(self, key, value):
        self.key2value[key] = value
        self.value2key[value] = key

    def get_key(self, value, default=None):
        return self.value2key.get(value, default)

    def get_value(self, key, default=None):
        return self.key2value.get(key, default)


def find_outer_dir(name: str):
    """
    递归查找父目录中是否存在指定的目录名
    """
    cur_dir = os.getcwd()
    while cur_dir != os.path.dirname(cur_dir):
        cur_dir = os.path.dirname(cur_dir)
        target_path = os.path.join(cur_dir, name)
        if os.path.isdir(target_path):
            return target_path
    return name

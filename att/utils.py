#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

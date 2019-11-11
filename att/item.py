
from .utils import *

class Item(Dict):
    def __init__(self, *, key=None, ios_key=None, web_key=None, untranslatable=False, auto_translate=True, en='', zh='', th='', vi='', pt=''):
        super().__init__()
        self.key = key
        self.ios_key = ios_key
        self.web_key = web_key
        self.untranslatable = untranslatable  # 当前对该字段的处理在合并Item时, 貌似有问题...
        self.auto_translate = auto_translate  # 脚本的翻译功能会判断该字段
        self.en = en
        self.zh = zh
        self.th = th
        self.vi = vi
        self.pt = pt

    def all_lang_equals(self, other):
        return self.en == other.en and self.zh == other.zh and self.th == other.th and self.vi == other.vi and self.pt == other.pt


class Key:
    """
    >>> android_key = AndroidKey('key')
    >>> android_key2 = AndroidKey('key')
    >>> android_key == android_key2
    True
    >>> ios_key = iOSKey('key')
    >>> android_key == ios_key
    False
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, o: object) -> bool:
        return type(self) == type(o) and self.name == o.name

    def __hash__(self) -> int:
        return hash(self.name)

    __repr__ = __str__

    # 所谓'key_name'是指Item的三种key: key, ios_key, web_key
    @classmethod
    def key_name(cls): return 'key'


class AndroidKey(Key):
    def __init__(self, name):
        super().__init__(name)


class iOSKey(Key):
    @classmethod
    def key_name(cls): return 'ios_key'

    def __init__(self, name):
        super().__init__(name)


class WebKey(Key):
    @classmethod
    def key_name(cls): return 'web_key'

    def __init__(self, name):
        super().__init__(name)


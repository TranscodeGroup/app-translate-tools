
from .utils import *


class Item(dict):
    """
    - key/ios_key/auto_translate等字段放到自身的属性上
    - lang->text的映射放到dict中, 使用keys()可列出所有lang
    """

    def __init__(self, *, key=None, ios_key=None, web_key=None, flutter_key=None, untranslatable=False, auto_translate=True):
        super().__init__()
        self.key = key
        self.ios_key = ios_key
        self.web_key = web_key
        self.flutter_key = flutter_key
        self.untranslatable = untranslatable  # 当前对该字段的处理在合并Item时, 貌似有问题...
        self.auto_translate = auto_translate  # 脚本的翻译功能会判断该字段

    def __missing__(self, key):
        return None

    def all_lang_equals(self, other):
        """
        所有语言的翻译完全相等
        """
        if self.keys() != other.keys():
            return False
        for key in self.keys():
            if self[key] != other[key]:
                return False
        return True

    def all_lang_equals_for_present(self, other):
        """
        翻译了的部分语言的翻译都是相等的, 未翻译的不算
        """
        for lang, text in self.items():
            if other[lang] and other[lang] != text:
                return False
        return True

    def all_lang_equals_for_only_en_zh(self, other):
        """
        只比较en和zh
        """
        for lang in ('en', 'zh'):
            if self[lang] != other[lang]:
                return False
        return True


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

    def __eq__(self, o: object) -> bool:
        return type(self) == type(o) and self.name == o.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):  # 控制台打印专用
        return self.key_name() + ':' + self.name

    # 所谓'key_name'是指Item的四种key: key, ios_key, web_key, flutter_key
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


class FlutterKey(Key):
    @classmethod
    def key_name(cls): return 'flutter_key'

    def __init__(self, name):
        super().__init__(name)

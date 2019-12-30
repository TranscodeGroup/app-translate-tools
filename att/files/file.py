import typing
from ..item import *
import re


class File:
    def __init__(self, file, lang, is_main=True, *, keyClass: typing.Type[Key]):
        super().__init__()
        self.file = file
        self.lang = lang
        self.is_main = is_main
        self.keyClass = keyClass

    def add(self, key, value): pass

    def remove(self, key): pass

    def cover(self, items): pass

    def to_items(self, items): pass

    def to_file(self, file): pass

    def save(self):
        self.to_file(self.file)


# 除`\n`以外的`\`
# @text_newline_sep
REG_BACKSLASH = re.compile(r'\\(?!n)')


def convert_string_to_text(string: str) -> str:
    # string中存在转义:
    # \' -> '
    # \" -> "
    # \\ -> \
    # \n -> 不处理, item中用`\n`表示换行
    # @text_newline_sep
    return string.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def convert_text_to_string(text: str, replace_single_quote=True, replace_double_quote=True) -> str:
    # 同上, 反向转换
    r = re.sub(REG_BACKSLASH, '\\\\', text)
    if replace_single_quote:
        r = r.replace("'", "\\'")
    if replace_double_quote:
        r = r.replace('"', '\\"')
    return r

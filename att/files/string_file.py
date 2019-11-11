import re
from ..utils import *
from ..item import *
import os
from .file import *

class Line:
    @staticmethod
    def create(text):
        match = KeyValueLine.REG_KEY_VALUE.match(text)
        if match:
            return KeyValueLine(text, match.group('key'), match.group('value'))
        else:
            return Line(text)

    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text

    def __str__(self):
        return self.text()

    __repr__ = __str__


class KeyValueLine(Line):
    TEXT_FORMAT = '"{key}" = "{value}";\n'
    REG_KEY_VALUE = re.compile(r'"(?P<key>.*)"\s*=\s*"(?P<value>.*)";')

    def __init__(self, text, key, value):
        super().__init__(text)
        self.key = key
        self.value = value

    def text(self):
        return KeyValueLine.TEXT_FORMAT.format(key=self.key, value=self.value)

class StringsFile(File):
    @staticmethod
    def read(file):
        if not os.path.exists(file):
            return []
        lines = []
        with open(file, mode='r', encoding='utf-8') as f:
            for line in f:
                lines.append(Line.create(line))
        return lines

    def __init__(self, file, lang, is_main=True):
        super().__init__(file, lang, is_main, keyClass=iOSKey)
        self._lines = self.read(file)

    def add(self, key, value):
        self._lines.append(KeyValueLine('', str(key), value))

    def remove(self, key):
        count = 0
        # 使用tuple(), 直接计算filter()的结果, 防止迭代过程中移除元素
        for line in tuple(filter(lambda l: isinstance(l, KeyValueLine) and l.key == str(key), self._lines)):
            self._lines.remove(line)
            count = count + 1
        return count

    def cover(self, items):
        for line in filter(lambda l: isinstance(l, KeyValueLine), self._lines):
            key = self.keyClass(line.key)
            item = items[key]
            if item:
                old_text = line.value
                new_text = item[self.lang]
                if new_text is None:
                    # @item_lang_is_none
                    p('skip', '   [%(lang)s] %(key)s: new_text is None' % {'key': key, 'lang': self.lang})
                elif old_text != new_text:
                    line.value = new_text

    def to_items(self, items):
        for line in filter(lambda l: isinstance(l, KeyValueLine), self._lines):
            key = self.keyClass(line.key)
            item = items[key]
            if not item:
                item = Item(ios_key=key.name)
                items[key] = item
            if item[self.lang]:
                p('warn', '存在同名key: %(key)s [%(old_value)s=>%(new_value)s] (%(lang)s)' % {
                    'key': key,
                    'old_value': item[self.lang],
                    'new_value': line.value,
                    'lang': self.lang
                })
            item[self.lang] = line.value

    def to_file(self, file):
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode='w', encoding='utf-8', newline='\n') as f:
            for line in self._lines:
                f.writelines(line.text())

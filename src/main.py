#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import xml.dom.minidom as dom
import re
import io
from deprecated import deprecated
from utils import *
import gtranslate as gt
import typing
import os
import json
from collections import Iterable, Iterator
from functools import reduce

REMIND_WHEN_ESCAPE = True
REG_QUOTE_TEXT = re.compile(r'^"(?P<content>.*?)\s*"$')
REG_REF_STRING_TEXT = re.compile(r'@string/\w+')
COL_KEY = 'KEY'
COL_IOS_KEY = 'IOS_KEY'
COL_WEB_KEY = 'WEB_KEY'
COL_UNTRANSLATABLE = 'Untranslatable'
COL_ENGLISH = 'English'
COL_CHINESE = 'Chinese'
COL_THAI = 'Thai'
COL_VIET = 'Vietnamese'
TEXT_DEL = '__DEL__'  # 用于标识该item需要删除的特殊字符串


class NodeUtil:
    @staticmethod
    def get_text_node_in_string(node, log=False):
        children = node.childNodes
        if len(children) == 1 and children[0].nodeType in (dom.Node.TEXT_NODE, dom.Node.CDATA_SECTION_NODE):
            return children[0]
        else:
            if log:
                p('warn', 'cannot get text node: node=%(node)s, children_length=%(length)s' % {
                    'node': node.toxml(),
                    'length': len(node.childNodes),
                })
            return None

    @staticmethod
    def to_text(node: dom.Node) -> str:
        if node.nodeType == node.TEXT_NODE:
            return node.data
        else:
            return ''.join(map(lambda n: NodeUtil.to_text(n), node.childNodes))

    @staticmethod
    def child_elements_it(node):
        return filter(lambda n: n.nodeType == dom.Node.ELEMENT_NODE, node.childNodes)


class Dict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __missing__(self, key):
        return None


class Item(Dict):
    def __init__(self, *, key=None, ios_key=None, web_key=None, untranslatable=False, auto_translate=True, en='', zh='', th='', vi=''):
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


h('convert')


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


class JsonFile(File):
    @staticmethod
    def read(file):
        if not os.path.exists(file):
            return {}
        obj = {}
        with open(file, mode='r', encoding='utf-8') as f:
            obj = json.load(f, object_pairs_hook=Dict)
        return JsonFile.obj_to_dict(obj)

    @staticmethod
    def obj_to_dict(obj, key_prefix='', out_dict=None):
        if out_dict == None:
            out_dict = Dict()
        for k, v in obj.items():
            key = ('%s.%s' % (key_prefix, k)) if key_prefix else k
            if(isinstance(v, dict)):
                JsonFile.obj_to_dict(v, key, out_dict)
            else:
                out_dict[key] = v
        return out_dict

    @staticmethod
    def dict_to_obj(in_dict):
        out_obj = Dict()
        for k, v in in_dict.items():
            names = k.split('.')
            obj = out_obj
            for name in names[:-1]:
                temp_obj = obj[name]
                if not temp_obj:
                    temp_obj = Dict()
                    obj[name] = temp_obj
                obj = temp_obj
            obj[names[-1]] = v
        return out_obj

    def __init__(self, file, lang, is_main=True):
        super().__init__(file, lang, is_main, keyClass=WebKey)
        self._dict = self.read(file)

    def add(self, key, value):
        self._dict[str(key)] = value

    def remove(self, key):
        self._dict.pop(str(key), '')

    def cover(self, items):
        for k, v in self._dict.items():
            key = self.keyClass(k)
            item = items[key]
            if item:
                new_text = item[self.lang]
                if new_text != v:
                    self._dict[k] = new_text

    def to_items(self, items):
        for k, v in self._dict.items():
            key = self.keyClass(k)
            item = items[key]
            if not item:
                item = Item(web_key=key.name)
                items[key] = item
            item[self.lang] = v

    def to_file(self, file):
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode='w', encoding='utf-8', newline='\n') as f:
            json.dump(self.dict_to_obj(self._dict), f, indent=2, ensure_ascii=False)


class XmlFile(File):
    @staticmethod
    def read(file):
        if not os.path.exists(file):
            return dom.parseString('<resources>\n</resources>')
        root = dom.parse(file)
        resources_node = root.getElementsByTagName('resources')[0]
        # 展开<array>
        for node in filter(lambda n: n.tagName in ('string-array', 'array'),
                           NodeUtil.child_elements_it(resources_node)):
            base_key = node.getAttribute('name')
            for index, item_node in enumerate(node.getElementsByTagName('item')):
                text_node = NodeUtil.get_text_node_in_string(item_node, log=True)
                if text_node:
                    if not REG_REF_STRING_TEXT.match(text_node.data):
                        # <item>的内容没有引用到其他字符串时,
                        # 在xml中新建<string>, 并将<item>的内容指向新建的<string>
                        string_node = root.createElement('string')
                        string_node_name = '%s_%s' % (base_key, index)
                        string_node.setAttribute('name', string_node_name)
                        string_node.appendChild(text_node.cloneNode(1))
                        resources_node.insertBefore(string_node, node)
                        resources_node.insertBefore(root.createTextNode('\n    '), node)
                        text_node.data = '@string/%s' % string_node_name
                        p('info', '展开<array>: %s' % string_node.toxml())

        return root

    def __init__(self, file, lang, is_main=True):
        super().__init__(file, lang, is_main, keyClass=AndroidKey)
        self._dom = self.read(file)

    def add(self, key, value):
        resources_node = self._dom.getElementsByTagName('resources')[0]
        string_node = self._dom.createElement('string')
        string_node.setAttribute('name', str(key))
        string_node.appendChild(self._dom.createTextNode(value))
        resources_node.appendChild(self._dom.createTextNode('    '))
        resources_node.appendChild(string_node)
        resources_node.appendChild(self._dom.createTextNode('\n'))

    def remove(self, key):
        resources_node = self._dom.getElementsByTagName('resources')[0]
        count = 0
        # 使用tuple(), 直接计算filter()的结果, 防止迭代过程中移除元素
        for node in tuple(filter(lambda n: n.tagName == 'string' and n.getAttribute('name') == str(key),
                                 NodeUtil.child_elements_it(resources_node))):
            resources_node.removeChild(node)
            count = count + 1
        return count

    def cover(self, items):
        string_nodes = self._dom.getElementsByTagName('string')
        for node in string_nodes:
            key = self.keyClass(node.getAttribute('name'))
            text_node = NodeUtil.get_text_node_in_string(node, log=True)
            if text_node:
                item = items[key]
                if item:
                    old_text = text_node.data
                    new_text = item[self.lang]
                    # 双引号括住的字符串, 需要特殊处理
                    match = REG_QUOTE_TEXT.fullmatch(old_text)
                    if match and match.group('content') == new_text:
                        p('skip', old_text, '=>', new_text)
                    elif old_text == new_text:  # 文本相同, 不保存
                        pass
                    else:
                        # `'`和`\`需要转义
                        if "'" in old_text or '\\' in old_text \
                                or "'" in new_text or '\\' in new_text:
                            # 先替换`\`=>`\\`, 再替换`'`=>`\'`
                            new_text = new_text.replace('\\', '\\\\').replace("'", "\\'")
                            if new_text != old_text:
                                if REMIND_WHEN_ESCAPE:
                                    p('remind', '%s:\n%s\n%s' % (key, old_text, new_text))
                                    if input('是否修改该字符串:(y)') not in 'yY':  # ''/'y'/'Y'表示'是'
                                        continue  # 不保存
                                else:
                                    p('warn', key, old_text, '=>', new_text)
                            else:
                                continue  # 文本相同, 跳过保存
                        # 保存
                        text_node.data = new_text

    def to_items(self, items):
        string_nodes = self._dom.getElementsByTagName('string')
        for node in string_nodes:
            key = self.keyClass(node.getAttribute('name'))
            text_node = NodeUtil.get_text_node_in_string(node, log=True)
            if text_node:
                item = items[key]
                if not item:
                    item = Item(key=key.name,
                                untranslatable=node.getAttribute('translatable') == 'false',
                                auto_translate=not (node.getAttribute('translateAuto') == 'false'))
                    items[key] = item
                item[self.lang] = text_node.data

    def to_file(self, file):
        str_io = io.StringIO()
        str_io.write('<?xml version="1.0" encoding="utf-8"?>\n')
        for node in self._dom.childNodes:
            node.writexml(str_io)
        # strings.xml中可以存在`"`和`>`, 故需要转换一下
        content = str_io.getvalue().replace('&quot;', '"').replace('&gt;', '>')
        if not os.path.exists(file):  # 保证目录存在, 方便之后创建文件
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode='w', encoding='utf-8', newline='\n') as w:
            w.write(content)


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
                if old_text != new_text:
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


class FieldConverter:
    @staticmethod
    def create(file_name):
        if file_name.lower().endswith('.xlsx'):
            return XlsxFieldConverter()
        else:
            return FieldConverter()

    def to_text(self, t):
        """
        t为false时, 统一转换成空字符串
        空字符串保存成xls时, 为空单元格; 空单元格, 读取出来时, 为NaN; 故, 读取时也要做对应处理
        注意: NaN也是一个数字, NaN的特性是, 自身不等于自身Σ( ￣□￣||)
        >>> np.nan != np.nan
        True
        """
        return t or ''

    def from_text(self, t):
        return t if pd.notna(t) else ''

    def to_bool(self, b):
        """
        往xls中写入bool, 将显示为TRUE/FALSE; 读取TRUE/FALSE的单元格, 会得到bool_;
        """
        return bool(b)

    def from_bool(self, b):
        return b


class XlsxFieldConverter(FieldConverter):
    """
    pandas使用openpyxl读写xlsx文件, 但这东西貌似有bug
    往xlsx文件写入''或None时, xml中会自己填充一个非空字符串, 为了避免这种情况, 将写入的字符串替换成EMPTY_TEXT, 读取时也要做相应处理
    """
    EMPTY_TEXT = '　' * 3  # 这是个全角空格~~

    def to_text(self, t):
        return t or self.EMPTY_TEXT

    def from_text(self, t):
        return super().from_text(t) if t != self.EMPTY_TEXT else ''


class ItemsUtil:

    @classmethod
    def read_xls_to_items(cls, file):
        items = Dict()
        df = pd.read_excel(file)
        fc = FieldConverter.create(file)
        # df.fillna('', inplace=True) 将所有的NaN替换成''
        for i in range(len(df)):
            item = Item(
                key=fc.from_text(df[COL_KEY][i]),
                ios_key=fc.from_text(df[COL_IOS_KEY][i]) if df.get(COL_IOS_KEY) is not None else None,
                web_key=fc.from_text(df[COL_WEB_KEY][i]) if df.get(COL_WEB_KEY) is not None else None,
                untranslatable=fc.from_bool(df[COL_UNTRANSLATABLE][i]) if df.get(COL_UNTRANSLATABLE) is not None else False,
                en=fc.from_text(df[COL_ENGLISH][i]),
                zh=fc.from_text(df[COL_CHINESE][i]),
                th=fc.from_text(df[COL_THAI][i]),
                vi=fc.from_text(df[COL_VIET][i]),
            )
            if item.key:
                items[AndroidKey(item.key)] = item
            if item.ios_key:
                items[iOSKey(item.ios_key)] = item
            if item.web_key:
                items[WebKey(item.web_key)] = item

        return items

    @classmethod
    def write_items_to_xls(cls, file, items):
        all_columns = (COL_KEY, COL_IOS_KEY, COL_WEB_KEY, COL_UNTRANSLATABLE, COL_ENGLISH, COL_CHINESE, COL_THAI, COL_VIET)
        out_columns = (COL_KEY, COL_IOS_KEY, COL_WEB_KEY, COL_ENGLISH, COL_CHINESE, COL_THAI, COL_VIET)

        df = pd.DataFrame(columns=all_columns)
        fc = FieldConverter.create(file)
        sorted_items = sorted(items.values(), key=lambda i: i.en.lower())  # 按en排序
        for item in sorted_items:
            if not item.untranslatable:  # 只输出需要翻译的内容 @write_items_to_xls_only_translatable
                df.loc[len(df)] = (
                    fc.to_text(item.key),
                    fc.to_text(item.ios_key),
                    fc.to_text(item.web_key),
                    fc.to_bool(item.untranslatable),
                    fc.to_text(item.en),
                    fc.to_text(item.zh),
                    fc.to_text(item.th),
                    fc.to_text(item.vi),
                )
        df.to_excel(file, index=False, columns=out_columns, na_rep='')

    @classmethod
    def read_files_to_items(cls, files):
        items = Dict()
        for f in files:
            f.to_items(items)
        return items

    @classmethod
    def cover_items_to_files(cls, files, items):
        for f in files:
            f.cover(items)
            f.save()

    @classmethod
    def get_key_name_from_files(cls, files: typing.Tuple[File]):
        # 认为files的key_name都是相同的, 从第一个file中获取key_name
        return (files[0].keyClass if len(files) > 0 else AndroidKey).key_name()

    @classmethod
    def get_key_name_from_items(cls, items: typing.Dict[Key, Item]):
        # 认为items的key_name都是相同的, 从第一个item中获取key_name
        return (next(iter(items.keys())) if len(items) > 0 else AndroidKey).key_name()


def open_android_files_bus():
    return (
        XmlFile(r'..\bus\src\main\res\values\strings.xml', 'en'),
        XmlFile(r'..\bus\src\main\res\values-zh-rCN\strings.xml', 'zh'),
    )


def open_android_files_thirdparty():
    return (
        XmlFile(r'..\thirdparty\src\main\res\values\strings_code.xml', 'en'),
        XmlFile(r'..\thirdparty\src\main\res\values-zh-rCN\strings_code.xml', 'zh'),
        XmlFile(r'..\thirdparty\src\main\res\values-th-rTH\strings_code.xml', 'th'),
        XmlFile(r'..\thirdparty\src\main\res\values-vi\strings_code.xml', 'vi'),
    )


def open_android_files():
    return (
        # main
        XmlFile(r'..\app\src\main\res\values\strings.xml', 'en'),
        XmlFile(r'..\app\src\main\res\values-zh-rCN\strings.xml', 'zh'),
        XmlFile(r'..\app\src\main\res\values-th-rTH\strings.xml', 'th'),
        XmlFile(r'..\app\src\main\res\values-vi\strings.xml', 'vi'),
        # distar
        XmlFile(r'..\app\src\distar\res\values\strings-flavor.xml', 'en', is_main=False),  # 不是主file, 不会往里面新增行
        XmlFile(r'..\app\src\distar\res\values-zh-rCN\strings-flavor.xml', 'zh', is_main=False),
        XmlFile(r'..\app\src\distar\res\values-th-rTH\strings-flavor.xml', 'th', is_main=False),
        XmlFile(r'..\app\src\distar\res\values-vi\strings-flavor.xml', 'vi', is_main=False),
    )


def open_web_files():
    return (
        JsonFile(r'..\..\Tracker-Vue\src\locales\en.json', 'en'),
        JsonFile(r'..\..\Tracker-Vue\src\locales\zh.json', 'zh'),
        JsonFile(r'..\..\Tracker-Vue\src\locales\th.json', 'th'),
        JsonFile(r'..\..\Tracker-Vue\src\locales\vi.json', 'vi'),
    )


def open_ios_files():
    return (
        StringsFile(r'D:\GitHub\Tracker-iOS\SNProject\SNProject\Base.lproj\Localizable.strings', 'en'),
        StringsFile(r'D:\GitHub\Tracker-iOS\SNProject\SNProject\zh.lproj\Localizable.strings', 'zh'),
        StringsFile(r'D:\GitHub\Tracker-iOS\SNProject\SNProject\th.lproj\Localizable.strings', 'th'),
        StringsFile(r'D:\GitHub\Tracker-iOS\SNProject\SNProject\vi.lproj\Localizable.strings', 'vi'),
    )


def export_xls(out_xls, *files_tuple):
    def merge_items(base_items, new_items):
        items = Dict(base_items)
        key_name = ItemsUtil.get_key_name_from_items(new_items)  # 可能为: key/ios_key/web_key
        for key, item in new_items.items():
            for base_item in base_items.values():
                if not base_item[key_name] and item.zh == base_item.zh and item.en == base_item.en and item.th == base_item.th and item.vi == base_item.vi:
                    # base_item不存在[key_name]的情况下, 若所有语言的翻译都相同, 说明是同一个字符串, 给base_item添加[key_name]
                    base_item[key_name] = item[key_name]
                    break
            else:  # 没有找到三语相同的时, 需要添加item
                items[key] = item
        return items

    # ItemsUtil.write_items_to_xls(out_xls, merge_items(
    #     ItemsUtil.read_files_to_items(open_android_files()),
    #     ItemsUtil.read_files_to_items(open_ios_files()),
    # ))
    ItemsUtil.write_items_to_xls(out_xls, reduce(merge_items, map(ItemsUtil.read_files_to_items, files_tuple)))


def import_xls(in_xls, *files_tuple):
    def process_diff_cover(files, new_items):
        """
        只处理新旧items中key相同的部分
        """
        items = ItemsUtil.read_files_to_items(files)
        for key, item in items.items():  # 遍历items
            new_item = new_items[key]
            if new_item:  # 一个key, 存在对应的新/旧item
                for lang, file in map(lambda f: (f.lang, f), files):  # 遍历files (注意: 有可能存在多个file的lang相同的情况...)
                    if new_item[lang] == TEXT_DEL:
                        # 若key在某种语言下, 新值为TEXT_DEL, 且存在老值,
                        # 则删除对应的file中的条目
                        # 达到删除某个字段的目的
                        if item[lang]:
                            count = file.remove(key)
                            p('info', '- [%(lang)s] %(key)s: %(value)s *%(count)s' % {
                                'lang': lang,
                                'key': key,
                                'value': item[lang],
                                'count': count
                            })
                        else:
                            pass
                    elif not item[lang] and new_item[lang]:
                        # @add_empty_line_for_cover
                        # 若key在某种语言下, 之前没有值, 现在有了值, 这说明, 这个值是新增的
                        # file.cover(), 是通过查找file中已有的key来进行合并的, 并不能处理这种情况
                        # 所以, 我们需要给该语言的file新增一个key为key的空行,
                        # 之后执行file.cover()时, 就有了这个key, 可以正常合并
                        # 另外, 因为存在多个file的lang相同的情况, 故标记主file(file.is_main), 只往主file中新增行
                        if file.is_main:
                            file.add(key, '')
                        p('info' if file.is_main else 'skip', '+ [%(lang)s] %(key)s: %(value)s (in %(file)s)' % {
                            'lang': lang,
                            'key': key,
                            'value': new_item[lang],
                            'file': file.file,
                        })
                    else:
                        pass

    def process_diff_all(files: typing.Tuple[File, ...], new_items: typing.Dict[str, Item], item_key_name: str):
        """
        以new_items为准, 处理删除和新增

        :param files:
        :param new_items:
        :param item_key_name:  new_items的key使用的Item的哪个字段; 可选 'key', 'ios_key';
        :return:
        """
        items = ItemsUtil.read_files_to_items(files)
        if item_key_name:  # 过滤android或ios的item
            new_items = Dict((k, v) for k, v in new_items.items() if str(k) == v[item_key_name])
        lang_files = list(map(lambda f: (f.lang, f), files))  # (注意: 有可能存在多个file的lang相同的情况...)
        for key, item in items.items():  # 遍历items
            new_item = new_items[key]
            if new_item:  # 一个key, 存在对应的新/旧item
                for lang, file in lang_files:
                    if not item[lang] and new_item[lang]:  # 某种语言下, 之前没有翻译, 现在有翻译
                        # see: @add_empty_line_for_cover
                        if file.is_main:
                            file.add(key, '')
                            p('info', ' + [%(lang)s] %(key)s: %(value)s (in %(file)s)' % {
                                'lang': lang,
                                'key': key,
                                'value': new_item[lang],
                                'file': file.file,
                            })
            else:  # item存在, new_item不存在, 则需要删除
                if not item.untranslatable:  # see: @write_items_to_xls_only_translatable
                    for lang, file in lang_files:
                        file.remove(key)
                        p('info', '-- [%(lang)s] %(key)s: %(value)s (in %(file)s)' % {
                            'lang': lang,
                            'key': key,
                            'value': item[lang],
                            'file': file.file,
                        })

        for key, new_item in new_items.items():
            item = items[key]
            if not item:  # new_item存在, item不存在, 则需要新增
                for lang, file in lang_files:
                    if new_item[lang] and file.is_main:
                        file.add(key, '')  # see: @add_empty_line_for_cover
                        p('info', '++ [%(lang)s] %(key)s: %(value)s (in %(file)s)' % {
                            'lang': lang,
                            'key': key,
                            'value': new_item[lang],
                            'file': file.file,
                        })

    new_items = ItemsUtil.read_xls_to_items(in_xls)

    # android_files = open_android_files()
    # ios_files = open_ios_files()

    ## process_diff_cover(android_files, new_items)
    ## process_diff_cover(ios_files, new_items)

    # process_diff_all(android_files, new_items, 'key')
    # process_diff_all(ios_files, new_items, 'ios_key')

    # ItemsUtil.cover_items_to_files(android_files, new_items)
    # ItemsUtil.cover_items_to_files(ios_files, new_items)

    for files in files_tuple:
        process_diff_all(files, new_items, ItemsUtil.get_key_name_from_files(files))
        ItemsUtil.cover_items_to_files(files, new_items)


h('test')


def test_all():
    export_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())
    import_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())


def convert_lang(lang: str):
    if lang == 'zh':
        return 'zh-CN'
    return lang


PROXIES = {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'}


def translate(text, from_lang='auto', to_lang='auto'):
    return gt.translate(
        text, to_language=convert_lang(to_lang), language=convert_lang(from_lang),
        proxies=PROXIES,  # 代理
        verify=True,  # 设为False可以关闭证书校验, 方便调试
        timeout=5,  # 5秒超时
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
    )


def translate_files(files: typing.Tuple[File, ...]):
    def process_translate(files: typing.Tuple[File, ...], items: typing.Dict[str, Item]):
        main_lang_files = [(f.lang, f) for f in files if f.is_main]
        for key, item in ((k, v) for k, v in items.items() if not v.untranslatable and v.auto_translate):
            # 认为is_main的file, 每种语言下有且只有一个...
            has_translate_files = [(lang, f) for lang, f in main_lang_files if item[lang]]
            if len(has_translate_files) > 0 and len(has_translate_files) < len(main_lang_files):
                source = Dict(lang=has_translate_files[0][0], text=item[has_translate_files[0][0]])  # 将第一个有翻译的语言作为源语言
                for lang, file in main_lang_files:  # 因为存在将zh写在en的file里的情况, 故需要把所有的file都翻译一遍
                    try:
                        old_text = item[lang]
                        new_text = translate(source.text, 'auto', lang)  # 自动判断源语言
                        replace = True
                        if old_text and old_text != new_text:
                            if source.lang != lang:  # 当前的使用场景下, 大多会将zh写在en的file里, 这种情况下不提示...
                                p('remind', '(translate %s => %s)%s:\n%s\n%s' % (source.lang, lang, key, old_text, new_text))
                                replace = input('是否修改该字符串:(y)') in 'yY'
                        if replace:
                            item[lang] = new_text
                            p('info', 'translate %s => %s >> %s => %s' % (source.lang, lang, source.text, item[lang]))
                            if not old_text:  # 给file添加空行, see: @add_empty_line_for_cover
                                file.add(key, '')
                    except Exception as e:
                        p('warn', 'translate %s => %s >> %s =x %s' % (source.lang, lang, source.text, e))

    items = ItemsUtil.read_files_to_items(files)

    process_translate(files, items)

    ItemsUtil.cover_items_to_files(files, items)


def main():
    # translate_files(open_android_files_bus())
    # translate_files(open_android_files_thirdparty())
    translate_files(open_android_files())
    # translate_files(open_web_files())
    # translate_files(open_ios_files())

    # export_xls(r'tmp/tracker_v6.1.main.xls', open_android_files(), open_ios_files())
    # export_xls(r'tmp/tracker_v6.1.thirdparty.xls', open_android_files_thirdparty())
    # export_xls(r'tmp/tracker_v6.1.vue.xls', open_web_files())

    # import_xls(r'tmp/-App tracker_v5.main.xls', open_android_files(), open_ios_files())
    # import_xls(r'tmp/-App tracker_v5.thirdparty.xls', open_android_files_thirdparty())
    # import_xls(r'tmp/-App tracker_v5.vue.xls', open_web_files())

    # import_xls(r'tmp/tracker_vue_v3.xls', open_web_files())
    # import_xls(r'tmp/Tracker_v1.xls', open_android_files(), open_ios_files())

    # export_all(r'tmp/App中英泰对照翻译_v2.0.7.3.xls')
    # import_all(r'tmp/App中英泰对照翻译_v2.0.7.3.xls')
    pass


if __name__ == '__main__':
    main()
    # test_all()

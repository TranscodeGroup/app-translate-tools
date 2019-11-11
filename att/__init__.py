#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import io
from deprecated import deprecated
import typing
import os
import json
from collections.abc import Iterable, Iterator
from functools import reduce

from .item_util import ItemsUtil
from .translate import translate
from .files import *
from .utils import *


TEXT_DEL = '__DEL__'  # 用于标识该item需要删除的特殊字符串


__all__ = ['export_xls', 'import_xls', 'translate_files', 'XmlFile', 'JsonFile', 'StringsFile']


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

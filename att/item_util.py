from .utils import *
import pandas as pd
from .item import *
from .files import *
import typing

SORTED_BY_TEXT = False
CLEAR_UNTRANSLATE_LANG = False

COL_KEY = 'KEY'
COL_IOS_KEY = 'IOS_KEY'
COL_WEB_KEY = 'WEB_KEY'
COL_UNTRANSLATABLE = 'Untranslatable'
COLUMNS_DEFAULT = (COL_KEY, COL_IOS_KEY, COL_WEB_KEY, COL_UNTRANSLATABLE)

lang_column_converter = KeyValueConverter(
    zh='Chinese',
    en='English',
)


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
        # df.fillna('', inplace=True) # 将所有的NaN替换成''
        lang_columns = tuple(filter(lambda n: n not in COLUMNS_DEFAULT, df.columns))
        for i in range(len(df)):
            item = Item(
                key=fc.from_text(df[COL_KEY][i]),
                ios_key=fc.from_text(df[COL_IOS_KEY][i]) if df.get(COL_IOS_KEY) is not None else None,
                web_key=fc.from_text(df[COL_WEB_KEY][i]) if df.get(COL_WEB_KEY) is not None else None,
                untranslatable=fc.from_bool(df[COL_UNTRANSLATABLE][i]) if df.get(COL_UNTRANSLATABLE) is not None else False,
            )
            for column in lang_columns:
                lang = lang_column_converter.get_key(column, column)
                # @item_lang_is_none
                item[lang] = fc.from_text(df[column][i])
            if item.key:
                items[AndroidKey(item.key)] = item
            if item.ios_key:
                items[iOSKey(item.ios_key)] = item
            if item.web_key:
                items[WebKey(item.web_key)] = item

        return items

    @classmethod
    def write_items_to_xls(cls, file, items):
        df = pd.DataFrame(columns=COLUMNS_DEFAULT)
        fc = FieldConverter.create(file)
        item_list = []
        if SORTED_BY_TEXT:
            item_list = sorted(items.values(), key=lambda i: i['en'].lower())  # 按en排序
        else:
            item_list = items.values()
        for item in item_list:
            if not item.untranslatable:  # 只输出需要翻译的内容 @write_items_to_xls_only_translatable
                # 新列的index
                index = len(df)
                row = [
                    fc.to_text(item.key),
                    fc.to_text(item.ios_key),
                    fc.to_text(item.web_key),
                    fc.to_bool(item.untranslatable),
                ]
                # @item_lang_is_none
                # row的长度比df.columns小时, 添加会失败, 故补''
                for i in range(len(df.columns) - len(row)):
                    row.append('')
                df.loc[index] = row
                for lang, text in item.items():
                    column = lang_column_converter.get_value(lang, lang)
                    # 若语言对应的列不存在, 则添加一列, 默认值设为''
                    if df.get(column) is None:
                        df[column] = ''
                    df[column][index] = fc.to_text(text)

        out_columns = list(df.columns)
        out_columns.remove(COL_UNTRANSLATABLE)
        df.to_excel(file, index=False, columns=out_columns, na_rep='')

    @classmethod
    def read_files_to_items(cls, files):
        items = Dict()
        for f in files:
            f.to_items(items)

        if CLEAR_UNTRANSLATE_LANG:
            # 若翻译和en相同, 则认为这是未翻译的, 需要置为''
            for key, item in items.items():
                langs = list(item.keys())
                langs.remove('en')
                default_text = item['en']
                for lang in langs:
                    if item[lang] == default_text:
                        p('info', f'- untranslate [{lang}] {key}: {item[lang]}')
                        item[lang] = ''
        return items

    @classmethod
    def cover_items_to_files(cls, files, items):
        for f in files:
            f.cover(items)
            f.save()

    @classmethod
    def get_key_class_from_files(cls, files: typing.Tuple[File]):
        # 认为files的keyClass都是相同的, 从第一个file中获取keyClass
        return files[0].keyClass if len(files) > 0 else AndroidKey

    @classmethod
    def get_key_name_from_files(cls, files: typing.Tuple[File]):
        return cls.get_key_class_from_files(files).key_name()

    @classmethod
    def get_key_name_from_items(cls, items: typing.Dict[Key, Item]):
        # 认为items的key_name都是相同的, 从第一个item中获取key_name
        return (next(iter(items.keys())) if len(items) > 0 else AndroidKey).key_name()

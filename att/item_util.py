from .utils import *
import pandas as pd
from .item import *
from .files import *
import typing

COL_KEY = 'KEY'
COL_IOS_KEY = 'IOS_KEY'
COL_WEB_KEY = 'WEB_KEY'
COL_UNTRANSLATABLE = 'Untranslatable'
COL_ENGLISH = 'English'
COL_CHINESE = 'Chinese'
COL_THAI = 'Thai'
COL_VIET = 'Vietnamese'
COL_PORT = 'Portuguese'


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
                # @item_lang_is_none
                en=fc.from_text(df[COL_ENGLISH][i]) if df.get(COL_ENGLISH) is not None else None,
                zh=fc.from_text(df[COL_CHINESE][i]) if df.get(COL_CHINESE) is not None else None,
                th=fc.from_text(df[COL_THAI][i]) if df.get(COL_THAI) is not None else None,
                vi=fc.from_text(df[COL_VIET][i]) if df.get(COL_VIET) is not None else None,
                pt=fc.from_text(df[COL_PORT][i]) if df.get(COL_PORT) is not None else None,
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
        all_columns = (COL_KEY, COL_IOS_KEY, COL_WEB_KEY, COL_UNTRANSLATABLE, COL_ENGLISH, COL_CHINESE, COL_THAI, COL_VIET, COL_PORT)
        out_columns = (COL_KEY, COL_IOS_KEY, COL_WEB_KEY, COL_ENGLISH, COL_CHINESE, COL_THAI, COL_VIET, COL_PORT)

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
                    fc.to_text(item.pt),
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

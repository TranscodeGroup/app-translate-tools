from ..utils import *
import os
import json
from ..item import *
from .file import *


class JsonFile(File):
    @classmethod
    def read(cls, file):
        if not os.path.exists(file):
            p('warn', '%(file)s no exists.' % {'file': file})
            return {}
        obj = {}
        with open(file, mode='r', encoding='utf-8') as f:
            obj = json.load(f, object_pairs_hook=Dict)
        return cls.obj_to_dict(obj)

    @classmethod
    def obj_to_dict(cls, obj, key_prefix='', out_dict=None):
        if out_dict is None:
            out_dict = Dict()
        for k, v in obj.items():
            key = ('%s.%s' % (key_prefix, k)) if key_prefix else k
            if isinstance(v, dict):
                cls.obj_to_dict(v, key, out_dict)
            else:
                out_dict[key] = v
        return out_dict

    @classmethod
    def dict_to_obj(cls, in_dict):
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

    def __init__(self, file, lang, is_main=True, keyClass=WebKey):
        super().__init__(file, lang, is_main, keyClass=keyClass)
        self._dict = self.read(file)

    def _valid_entities(self):
        return self._dict.items()

    def add(self, key, value):
        self._dict[str(key)] = value

    def remove(self, key):
        self._dict.pop(str(key), '')

    def cover(self, items):
        for k, v in self._valid_entities():
            key = self.keyClass(k)
            item = items[key]
            if item:
                new_text = item[self.lang]
                if new_text is None:
                    # @item_lang_is_none
                    p('skip', '   [%(lang)s] %(key)s: new_text is None' % {'key': key, 'lang': self.lang})
                elif new_text != v:
                    self._dict[k] = new_text

    def to_items(self, items):
        for k, v in self._valid_entities():
            key = self.keyClass(k)
            item = items[key]
            if not item:
                kwargs = {self.keyClass.key_name(): key.name}
                item = Item(
                    untranslatable=self._is_untranslatable_by_key(k),
                    auto_translate=self._is_auto_translate_by_key(k),
                    **kwargs
                )
                items[key] = item
            item[self.lang] = v

    def _is_untranslatable_by_key(self, k):
        return False

    def _is_auto_translate_by_key(self, k):
        return True

    def to_file(self, file):
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode='w', encoding='utf-8', newline=None) as f:
            json.dump(self.dict_to_obj(self._dict), f, indent=2, ensure_ascii=False)

from .json_file import *


class ArbFile(JsonFile):
    @classmethod
    def dict_to_obj(cls, in_dict):
        return Dict(in_dict)

    @classmethod
    def obj_to_dict(cls, obj):
        return Dict(obj)

    def __init__(self, file, lang, is_main=True):
        super().__init__(file, lang, is_main, keyClass=FlutterKey)

    def _valid_entities(self):
        return filter(lambda it: not it[0].startswith('@'), self._dict.items())

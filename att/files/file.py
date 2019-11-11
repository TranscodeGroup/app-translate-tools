import typing
from ..item import *

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

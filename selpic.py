#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_android_files():
    return (
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values\strings.xml', 'en'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-zh-rCN\strings.xml', 'zh'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-zh-rTW\strings.xml', 'zh-TW'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ja\strings.xml', 'ja'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-de\strings.xml', 'de'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-es\strings.xml', 'es'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-fr\strings.xml', 'fr'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-it\strings.xml', 'it'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ko\strings.xml', 'ko'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ru\strings.xml', 'ru'),
    )


def open_ios_files():
    return (
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/en.lproj/Localizable.strings', 'en'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/zh-Hans.lproj/Localizable.strings', 'zh'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/zh-Hant-TW.lproj/Localizable.strings', 'zh-TW'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/ja.lproj/Localizable.strings', 'ja'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/de.lproj/Localizable.strings', 'de'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/es.lproj/Localizable.strings', 'es'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/fr.lproj/Localizable.strings', 'fr'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/it.lproj/Localizable.strings', 'it'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/ko.lproj/Localizable.strings', 'ko'),
        StringsFile('../@selpic/CXQPenMaJi/PenMaJi/ru.lproj/Localizable.strings', 'ru'),
    )


def main():
    # translate_files(open_android_files(), translate_all_lang=True)
    translate_files(open_android_files(), translate_all_lang=False)
    # translate_files(open_ios_files(), translate_all_lang=False)
    # export_xls('./tmp/2019-12-26.xls', open_android_files(), open_ios_files())
    # import_xls('./tmp/2019-12-26.xlsx', open_android_files(), open_ios_files())

    # export_xls('./tmp/print-2019-12-27.xls', open_ios_files(), open_android_files())
    # import_xls('./tmp/print-2019-12-27.xls', open_ios_files(), open_android_files())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_android_files():
    return (
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values\strings.xml', 'en'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-zh-rCN\strings.xml', 'zh'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-zh-rTW\strings.xml', 'zh-TW'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-de\strings.xml', 'de'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-es\strings.xml', 'es'),
        # XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-fr\strings.xml', 'fr'),
        # XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-it\strings.xml', 'it'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ja\strings.xml', 'ja'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ko\strings.xml', 'ko'),
        XmlFile('../@selpic/P660_printer/Printer/app/src/main/res/values-ru\strings.xml', 'ru'),
    )


def open_ios_files():
    return (
        StringsFile('../@selpic/printer-ios/strings/en.lproj/Localizable.strings', 'en'),
        StringsFile('../@selpic/printer-ios/strings/zh-Hans.lproj/Localizable.strings', 'zh'),
        StringsFile('../@selpic/printer-ios/strings/zh-Hant-TW.lproj/Localizable.strings', 'zh-TW'),
        StringsFile('../@selpic/printer-ios/strings/de.lproj/Localizable.strings', 'de'),
        StringsFile('../@selpic/printer-ios/strings/es.lproj/Localizable.strings', 'es'),
        StringsFile('../@selpic/printer-ios/strings/ja.lproj/Localizable.strings', 'ja'),
        StringsFile('../@selpic/printer-ios/strings/ko.lproj/Localizable.strings', 'ko'),
        StringsFile('../@selpic/printer-ios/strings/ru.lproj/Localizable.strings', 'ru'),
    )


def main():
    # translate_files(open_android_files(), translate_all_lang=True)
    # translate_files(open_ios_files(), translate_all_lang=False)
    export_xls('./tmp/2019-12-26.xls', open_android_files(), open_ios_files())
    import_xls('./tmp/2019-12-26.xls', open_android_files(), open_ios_files())



if __name__ == "__main__":
    main()

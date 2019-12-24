#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_android_files():
    return (
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values\strings.xml', 'en'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-zh-rCN\strings.xml', 'zh'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-zh-rTW\strings.xml', 'zh-TW'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-de\strings.xml', 'de'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-es\strings.xml', 'es'),
        # XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-fr\strings.xml', 'fr'),
        # XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-it\strings.xml', 'it'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-ja\strings.xml', 'ja'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-ko\strings.xml', 'ko'),
        XmlFile(r'..\@selpic\P660_printer\Printer\app\src\main\res\values-ru\strings.xml', 'ru'),
    )

def main():
    translate_files(open_android_files(), False)

if __name__ == "__main__":
    main()
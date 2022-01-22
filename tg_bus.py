#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_files():
    return (
        ArbFile('../@tg/flutter_distar_ex17/assets/languages/en-US.json', 'en'),
        ArbFile('../@tg/flutter_distar_ex17/assets/languages/th-TH.json', 'th'),
        ArbFile('../@tg/flutter_distar_ex17/assets/languages/zh-CN.json', 'zh'),
    )


def main():
    translate_files(open_files(), translate_all_lang=True)
    # import_xls('./tmp/urikar-2021-04-14-result.xls', open_files(), delete_no_exist_item=False)
    # export_xls('./tmp/tg-bug-2022-01-22.xls', open_files())
    # import_xls('./tmp/tg-bug-2022-01-22.xls', open_files())
    pass


if __name__ == "__main__":
    main()

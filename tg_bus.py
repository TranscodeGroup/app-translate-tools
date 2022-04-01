#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_files():
    return (
        ArbFile('../@tg/flutter_distar_ex17/lib/v2/resource/l10n/app_en.arb', 'en'),
        ArbFile('../@tg/flutter_distar_ex17/lib/v2/resource/l10n/app_th.arb', 'th'),
        ArbFile('../@tg/flutter_distar_ex17/lib/v2/resource/l10n/app_zh.arb', 'zh'),
    )


def main():
    translate_files(open_files(), translate_all_lang=True)
    # import_xls('./tmp/urikar-2021-04-14-result.xls', open_files(), delete_no_exist_item=False)
    # export_xls('./tmp/tg-bug-2022-01-22.xls', open_files())
    # import_xls('./tmp/tg-bug-2022-01-22.xls', open_files())
    pass


if __name__ == "__main__":
    main()

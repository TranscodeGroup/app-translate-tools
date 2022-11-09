#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_files():
    return (
        ArbFile('../@tg/tg_flutter/maintain/lib/resources/l10n/app_zh.arb', 'zh'),
        ArbFile('../@tg/tg_flutter/maintain/lib/resources/l10n/app_en.arb', 'en'),
        ArbFile('../@tg/tg_flutter/maintain/lib/resources/l10n/app_th.arb', 'th'),
    )


def main():
    translate_files(open_files(), translate_all_lang=True)
    # import_xls('./tmp/urikar-2021-04-14-result.xls', open_files(), delete_no_exist_item=False)
    # export_xls('./tmp/tg-mt-2022-01-22.xls', open_files())
    # import_xls('./tmp/tg-bmt-2022-01-22.xls', open_files())
    pass


if __name__ == "__main__":
    main()

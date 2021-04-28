#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *


def open_files():
    return (
        ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_en.arb', 'en'),
        ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_zh.arb', 'zh'),
        # ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_fr.arb', 'fr'),
        # ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_it.arb', 'it'),
        # ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_de.arb', 'de'),
        # ArbFile('../@selpic/selpic-flutter/selpic/lib/resource/l10n/app_es.arb', 'es'),
    )


def main():
    # translate_files(open_files(), translate_all_lang=True)
    # import_xls('./tmp/urikar-2021-04-14-result.xls', open_files(), delete_no_exist_item=False)
    export_xls('./tmp/urikar-2021-04-28.xls', open_files())
    import_xls('./tmp/urikar-2021-04-28.xls', open_files())
    pass


if __name__ == "__main__":
    main()

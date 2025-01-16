#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from att import *

tg = find_outer_dir('@tg')


def test_all():
    export_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())
    import_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())


def open_android_files_bus():
    return (
        XmlFile(f'{tg}/Tracker-Android/bus/src/main/res/values/strings.xml', 'en'),
        XmlFile(f'{tg}/Tracker-Android/bus/src/main/res/values-zh-rCN/strings.xml', 'zh'),
    )


def open_android_files_thirdparty():
    return (
        XmlFile(f'{tg}/Tracker-Android/thirdparty/src/main/res/values/strings_code.xml', 'en'),
        XmlFile(f'{tg}/Tracker-Android/thirdparty/src/main/res/values-zh-rCN/strings_code.xml', 'zh'),
        XmlFile(f'{tg}/Tracker-Android/thirdparty/src/main/res/values-th-rTH/strings_code.xml', 'th'),
        XmlFile(f'{tg}/Tracker-Android/thirdparty/src/main/res/values-vi/strings_code.xml', 'vi'),
        XmlFile(f'{tg}/Tracker-Android/thirdparty/src/main/res/values-pt/strings_code.xml', 'pt'),
    )


def open_android_files():
    return (
        # main
        XmlFile(f'{tg}/Tracker-Android/app/src/main/res/values/strings.xml', 'en'),
        XmlFile(f'{tg}/Tracker-Android/app/src/main/res/values-zh-rCN/strings.xml', 'zh'),
        XmlFile(f'{tg}/Tracker-Android/app/src/main/res/values-th-rTH/strings.xml', 'th'),
        XmlFile(f'{tg}/Tracker-Android/app/src/main/res/values-vi/strings.xml', 'vi'),
        XmlFile(f'{tg}/Tracker-Android/app/src/main/res/values-pt/strings.xml', 'pt'),
    )


def open_android_files_flavor(flavor: str):
    if flavor == 'tg':
        # tg的文件在main目录下
        flavor = 'main'
    return (
        XmlFile(f'{tg}/Tracker-Android/app/src/%(flavor)s/res/values/strings-flavor.xml' % {'flavor': flavor}, 'en', is_main=True),
        XmlFile(f'{tg}/Tracker-Android/app/src/%(flavor)s/res/values-zh-rCN/strings-flavor.xml' % {'flavor': flavor}, 'zh', is_main=True),
        XmlFile(f'{tg}/Tracker-Android/app/src/%(flavor)s/res/values-th-rTH/strings-flavor.xml' % {'flavor': flavor}, 'th', is_main=True),
        XmlFile(f'{tg}/Tracker-Android/app/src/%(flavor)s/res/values-vi/strings-flavor.xml' % {'flavor': flavor}, 'vi', is_main=True),
        XmlFile(f'{tg}/Tracker-Android/app/src/%(flavor)s/res/values-pt/strings-flavor.xml' % {'flavor': flavor}, 'pt', is_main=True),
    )


def open_web_files():
    return (
        JsonFile(f'{tg}/Tracker-Vue/src/locales/en.json', 'en'),
        JsonFile(f'{tg}/Tracker-Vue/src/locales/zh.json', 'zh'),
        JsonFile(f'{tg}/Tracker-Vue/src/locales/th.json', 'th'),
        JsonFile(f'{tg}/Tracker-Vue/src/locales/vi.json', 'vi'),
        JsonFile(f'{tg}/Tracker-Vue/src/locales/pt.json', 'pt'),
    )


def open_ios_files():
    return (
        StringsFile(f'{tg}/Tracker-iOS/SNProject/SNProject/Base.lproj/Localizable.strings', 'en'),
        StringsFile(f'{tg}/Tracker-iOS/SNProject/SNProject/zh.lproj/Localizable.strings', 'zh'),
        StringsFile(f'{tg}/Tracker-iOS/SNProject/SNProject/th.lproj/Localizable.strings', 'th'),
        StringsFile(f'{tg}/Tracker-iOS/SNProject/SNProject/vi.lproj/Localizable.strings', 'vi'),
        StringsFile(f'{tg}/Tracker-iOS/SNProject/SNProject/pt.lproj/Localizable.strings', 'pt'),
    )


def translate_all():
    # translate_files(open_android_files_bus())
    # translate_files(open_android_files_thirdparty(), False)
    translate_files(open_android_files(), True)
    # translate_files(open_web_files(), False)
    # translate_files(open_ios_files())
    # translate_files(open_android_files_flavor('tg'), False)
    # translate_files(open_android_files_flavor('distar'), False)
    # translate_files(open_android_files_flavor('geckram'), False)
    # translate_files(open_android_files_flavor('blaupunkt'), False)
    # translate_files(open_android_files_flavor('ists'), False)


def export_import_all():
    export_xls(r'tmp/20191122_tg_tracker.main.xls', open_android_files(), open_ios_files())
    export_xls(r'tmp/20191122_tg_tracker.tg.xls', open_android_files_flavor('tg'))
    export_xls(r'tmp/20191122_tg_tracker.distar.xls', open_android_files_flavor('distar'))
    export_xls(r'tmp/20191122_tg_tracker.geckram.xls', open_android_files_flavor('geckram'))
    export_xls(r'tmp/20191122_tg_tracker.blaupunkt.xls', open_android_files_flavor('blaupunkt'))
    export_xls(r'tmp/20191122_tg_tracker_vue.xls', open_web_files())
    export_xls(r'tmp/20191122_tg_thirdparty.xls', open_android_files_thirdparty())

    import_xls(r'tmp/20191122_tg_tracker.main.xls', open_android_files(), open_ios_files())
    import_xls(r'tmp/20191122_tg_tracker.tg.xls', open_android_files_flavor('tg'))
    import_xls(r'tmp/20191122_tg_tracker.distar.xls', open_android_files_flavor('distar'))
    import_xls(r'tmp/20191122_tg_tracker.geckram.xls', open_android_files_flavor('geckram'))
    import_xls(r'tmp/20191122_tg_tracker.blaupunkt.xls', open_android_files_flavor('blaupunkt'))
    import_xls(r'tmp/20191122_tg_tracker_vue.xls', open_web_files())
    import_xls(r'tmp/20191122_tg_thirdparty.xls', open_android_files_thirdparty())


def main():
    translate_all()
    # export_import_all()

    # import_xls(r'tmp/-App tracker_v5.main.xls', open_android_files(), open_ios_files())
    # import_xls(r'tmp/-App tracker_v5.thirdparty.xls', open_android_files_thirdparty())
    # import_xls(r'tmp/-App tracker_v5.vue.xls', open_web_files())

    # import_xls(r'tmp/tracker_vue_v3.xls', open_web_files())
    # import_xls(r'tmp/Tracker_v1.xls', open_android_files(), open_ios_files())

    # export_all(r'tmp/App中英泰对照翻译_v2.0.7.3.xls')
    # import_all(r'tmp/App中英泰对照翻译_v2.0.7.3.xls')
    pass


if __name__ == '__main__':
    main()
    # test_all()

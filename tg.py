from att import *

def test_all():
    export_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())
    import_xls(r'tmp/App中英泰对照翻译_test_v1.xls', open_android_files(), open_ios_files())

def open_android_files_bus():
    return (
        XmlFile(r'..\Tracker-Android\bus\src\main\res\values\strings.xml', 'en'),
        XmlFile(r'..\Tracker-Android\bus\src\main\res\values-zh-rCN\strings.xml', 'zh'),
    )


def open_android_files_thirdparty():
    return (
        XmlFile(r'..\Tracker-Android\thirdparty\src\main\res\values\strings_code.xml', 'en'),
        XmlFile(r'..\Tracker-Android\thirdparty\src\main\res\values-zh-rCN\strings_code.xml', 'zh'),
        XmlFile(r'..\Tracker-Android\thirdparty\src\main\res\values-th-rTH\strings_code.xml', 'th'),
        XmlFile(r'..\Tracker-Android\thirdparty\src\main\res\values-vi\strings_code.xml', 'vi'),
        XmlFile(r'..\Tracker-Android\thirdparty\src\main\res\values-pt\strings_code.xml', 'pt'),
    )


def open_android_files():
    return (
        # main
        XmlFile(r'..\Tracker-Android\app\src\main\res\values\strings.xml', 'en'),
        XmlFile(r'..\Tracker-Android\app\src\main\res\values-zh-rCN\strings.xml', 'zh'),
        XmlFile(r'..\Tracker-Android\app\src\main\res\values-th-rTH\strings.xml', 'th'),
        XmlFile(r'..\Tracker-Android\app\src\main\res\values-vi\strings.xml', 'vi'),
        XmlFile(r'..\Tracker-Android\app\src\main\res\values-pt\strings.xml', 'pt'),
        # distar
        XmlFile(r'..\Tracker-Android\app\src\distar\res\values\strings-flavor.xml', 'en', is_main=False),  # 不是主file, 不会往里面新增行
        XmlFile(r'..\Tracker-Android\app\src\distar\res\values-zh-rCN\strings-flavor.xml', 'zh', is_main=False),
        XmlFile(r'..\Tracker-Android\app\src\distar\res\values-th-rTH\strings-flavor.xml', 'th', is_main=False),
        XmlFile(r'..\Tracker-Android\app\src\distar\res\values-vi\strings-flavor.xml', 'vi', is_main=False),
        XmlFile(r'..\Tracker-Android\app\src\distar\res\values-pt\strings-flavor.xml', 'pt', is_main=False),
    )


def open_web_files():
    return (
        JsonFile(r'..\Tracker-Vue\src\locales\en.json', 'en'),
        JsonFile(r'..\Tracker-Vue\src\locales\zh.json', 'zh'),
        JsonFile(r'..\Tracker-Vue\src\locales\th.json', 'th'),
        JsonFile(r'..\Tracker-Vue\src\locales\vi.json', 'vi'),
        JsonFile(r'..\Tracker-Vue\src\locales\pt.json', 'pt'),
    )


def open_ios_files():
    return (
        StringsFile(r'..\Tracker-iOS\SNProject\SNProject\Base.lproj\Localizable.strings', 'en'),
        StringsFile(r'..\Tracker-iOS\SNProject\SNProject\zh.lproj\Localizable.strings', 'zh'),
        StringsFile(r'..\Tracker-iOS\SNProject\SNProject\th.lproj\Localizable.strings', 'th'),
        StringsFile(r'..\Tracker-iOS\SNProject\SNProject\vi.lproj\Localizable.strings', 'vi'),
        StringsFile(r'..\Tracker-iOS\SNProject\SNProject\pt.lproj\Localizable.strings', 'pt'),
    )


def main():
    # translate_files(open_android_files_bus())
    translate_files(open_android_files_thirdparty(), False)
    translate_files(open_android_files(), False)
    translate_files(open_web_files(), False)
    # translate_files(open_ios_files())

    # export_xls(r'tmp/tracker_v6.1.main.xls', open_android_files(), open_ios_files())
    # export_xls(r'tmp/tracker_v6.1.thirdparty.xls', open_android_files_thirdparty())
    # export_xls(r'tmp/tracker_v6.1.vue.xls', open_web_files())

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

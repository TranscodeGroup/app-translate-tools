import re
import os
if __name__ == "__main__":
    import gtranslate as gt
else:
    from . import gtranslate as gt

__all__ = ['translate']


def convert_lang(lang: str):
    if lang == 'zh':
        return 'zh-CN'
    return lang


# PROXIES = {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'}


def convert_placeholder(text: str) -> str:
    """
    转换形如`%1$s`的占位符成`SSAAA`
    """
    def repl(m: re.Match):
        index = int(m.group('index'))
        type_: str = m.group('type')
        if ord(type_) <= ord('z') and ord(type_) >= ord('a'):
            type_ = type_.upper() * 2
        return type_ + chr(ord('A') + index - 1) * 4

    return re.sub(r'%(?P<index>\d+)\$(?P<type>[a-zA-Z])', repl, text)


def invert_placeholder(text: str) -> str:
    """
    反转
    """
    def repl(m: re.Match):
        index: int = ord(m.group('index')[0])-ord('A') + 1
        type_: str = m.group('type')
        if len(type_) == 2:
            type_ = type_[0].lower()
        return '%{index}${type}'.format(index=index, type=type_)

    return re.sub(r'(?P<type>([A-Z])\2?)(?P<index>([A-Z])\4{3})', repl, text)


def translate(text, from_lang='auto', to_lang='auto'):
    # gt不支持多行文本, 故须手动拆行
    # @text_newline_sep
    texts = convert_placeholder(text).replace('\\n', '\n').splitlines()
    results = []
    for t in texts:
        results.append(gt.translate(
            t, to_language=convert_lang(to_lang), language=convert_lang(from_lang),
            # proxies=PROXIES,  # 代理, 不在代码中写死代理， 通过环境变量中设置$https_proxy替代
            verify=True,  # 设为False可以关闭证书校验, 方便调试
            timeout=5,  # 5秒超时
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                # 从 https://translate.google.com/m 复制cookie, 保存到环境变量中
                'cookie': os.environ.get('app_translate_tools_cookie', None)
            }
        ))
    # 当前使用`\n`来分隔行
    # @text_newline_sep
    return invert_placeholder('\\n'.join(results))


if __name__ == "__main__":
    print(translate('fuck %1$s', to_lang='zh-CN'))
    print(translate('STARTING UP DEVICE', to_lang='it'))
    print(translate('i\\nlove\\nyou\nend', to_lang='zh-CN'))

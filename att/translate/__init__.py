from . import gtranslate as gt

__all__ = ['translate']


def convert_lang(lang: str):
    if lang == 'zh':
        return 'zh-CN'
    return lang


PROXIES = {'http': 'http://127.0.0.1:1080', 'https': 'http://127.0.0.1:1080'}


def translate(text, from_lang='auto', to_lang='auto'):
    return gt.translate(
        text, to_language=convert_lang(to_lang), language=convert_lang(from_lang),
        proxies=PROXIES,  # 代理
        verify=True,  # 设为False可以关闭证书校验, 方便调试
        timeout=5,  # 5秒超时
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
    )

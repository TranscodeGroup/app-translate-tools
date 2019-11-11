import os
import io
import xml.dom.minidom as dom
import re
from ..item import *
from .file import *

REMIND_WHEN_ESCAPE = True
REG_QUOTE_TEXT = re.compile(r'^"(?P<content>.*?)\s*"$')
REG_REF_STRING_TEXT = re.compile(r'@string/\w+')


class XmlFile(File):
    @staticmethod
    def read(file):
        if not os.path.exists(file):
            return dom.parseString('<resources>\n</resources>')
        root = dom.parse(file)
        resources_node = root.getElementsByTagName('resources')[0]
        # 展开<array>
        for node in filter(lambda n: n.tagName in ('string-array', 'array'),
                           NodeUtil.child_elements_it(resources_node)):
            base_key = node.getAttribute('name')
            for index, item_node in enumerate(node.getElementsByTagName('item')):
                text_node = NodeUtil.get_text_node_in_string(item_node, log=True)
                if text_node:
                    if not REG_REF_STRING_TEXT.match(text_node.data):
                        # <item>的内容没有引用到其他字符串时,
                        # 在xml中新建<string>, 并将<item>的内容指向新建的<string>
                        string_node = root.createElement('string')
                        string_node_name = '%s_%s' % (base_key, index)
                        string_node.setAttribute('name', string_node_name)
                        string_node.appendChild(text_node.cloneNode(1))
                        resources_node.insertBefore(string_node, node)
                        resources_node.insertBefore(root.createTextNode('\n    '), node)
                        text_node.data = '@string/%s' % string_node_name
                        p('info', '展开<array>: %s' % string_node.toxml())

        return root

    def __init__(self, file, lang, is_main=True):
        super().__init__(file, lang, is_main, keyClass=AndroidKey)
        self._dom = self.read(file)

    def add(self, key, value):
        resources_node = self._dom.getElementsByTagName('resources')[0]
        string_node = self._dom.createElement('string')
        string_node.setAttribute('name', str(key))
        string_node.appendChild(self._dom.createTextNode(value))
        resources_node.appendChild(self._dom.createTextNode('    '))
        resources_node.appendChild(string_node)
        resources_node.appendChild(self._dom.createTextNode('\n'))

    def remove(self, key):
        resources_node = self._dom.getElementsByTagName('resources')[0]
        count = 0
        # 使用tuple(), 直接计算filter()的结果, 防止迭代过程中移除元素
        for node in tuple(filter(lambda n: n.tagName == 'string' and n.getAttribute('name') == str(key),
                                 NodeUtil.child_elements_it(resources_node))):
            resources_node.removeChild(node)
            count = count + 1
        return count

    def cover(self, items):
        string_nodes = self._dom.getElementsByTagName('string')
        for node in string_nodes:
            key = self.keyClass(node.getAttribute('name'))
            text_node = NodeUtil.get_text_node_in_string(node, log=True)
            if text_node:
                item = items[key]
                if item:
                    old_text = text_node.data
                    new_text = item[self.lang]
                    # 双引号括住的字符串, 需要特殊处理
                    match = REG_QUOTE_TEXT.fullmatch(old_text)
                    if new_text is None:
                        # @item_lang_is_none: 当items缺少某种语言的翻译时, 会是None, 需要跳过
                        p('skip', '   [%(lang)s] %(key)s: new_text is None' % {'key': key, 'lang': self.lang})
                    elif match and match.group('content') == new_text:
                        p('skip', old_text, '=>', new_text)
                    elif old_text == new_text:  # 文本相同, 不保存
                        pass
                    else:
                        # `'`和`\`需要转义
                        if "'" in old_text or '\\' in old_text \
                                or "'" in new_text or '\\' in new_text:
                            # 先替换`\`=>`\\`, 再替换`'`=>`\'`
                            new_text = new_text.replace('\\', '\\\\').replace("'", "\\'")
                            if new_text != old_text:
                                if REMIND_WHEN_ESCAPE:
                                    p('remind', '%s:\n%s\n%s' % (key, old_text, new_text))
                                    if input('是否修改该字符串:(y)') not in 'yY':  # ''/'y'/'Y'表示'是'
                                        continue  # 不保存
                                else:
                                    p('warn', key, old_text, '=>', new_text)
                            else:
                                continue  # 文本相同, 跳过保存
                        # 保存
                        text_node.data = new_text

    def to_items(self, items):
        string_nodes = self._dom.getElementsByTagName('string')
        for node in string_nodes:
            key = self.keyClass(node.getAttribute('name'))
            text_node = NodeUtil.get_text_node_in_string(node, log=True)
            if text_node:
                item = items[key]
                if not item:
                    item = Item(key=key.name,
                                untranslatable=node.getAttribute('translatable') == 'false',
                                auto_translate=not (node.getAttribute('translateAuto') == 'false'))
                    items[key] = item
                item[self.lang] = text_node.data

    def to_file(self, file):
        str_io = io.StringIO()
        str_io.write('<?xml version="1.0" encoding="utf-8"?>\n')
        for node in self._dom.childNodes:
            node.writexml(str_io)
        # strings.xml中可以存在`"`和`>`, 故需要转换一下
        content = str_io.getvalue().replace('&quot;', '"').replace('&gt;', '>')
        if not os.path.exists(file):  # 保证目录存在, 方便之后创建文件
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, mode='w', encoding='utf-8', newline='\n') as w:
            w.write(content)


class NodeUtil:
    @staticmethod
    def get_text_node_in_string(node, log=False):
        children = node.childNodes
        if len(children) == 1 and children[0].nodeType in (dom.Node.TEXT_NODE, dom.Node.CDATA_SECTION_NODE):
            return children[0]
        else:
            if log:
                p('warn', 'cannot get text node: node=%(node)s, children_length=%(length)s' % {
                    'node': node.toxml(),
                    'length': len(node.childNodes),
                })
            return None

    @staticmethod
    def to_text(node: dom.Node) -> str:
        if node.nodeType == node.TEXT_NODE:
            return node.data
        else:
            return ''.join(map(lambda n: NodeUtil.to_text(n), node.childNodes))

    @staticmethod
    def child_elements_it(node):
        return filter(lambda n: n.nodeType == dom.Node.ELEMENT_NODE, node.childNodes)

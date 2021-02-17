import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote


FORMULA_BASE_URL = 'http://latex.codecogs.com/gif.latex?{}'


class Tag:
    CENTERED_TEXT = 'centered_text'
    TEXT_HEADER = 'text_header'  # 'texto 01', 'texto 02', ...; left aligned
    TITLE = 'title'  # generic title, centered
    PORQUE = 'porque'
    PQ = 'pq'  # placeholder for the actual "PORQUE" text

    PARAGRAPH = 'paragraph'  # generic paragraphs, formatting is not relevant
    TEXT = 'text'  # text that should maintain its formatting (e.g. poems)
    LINK = 'link'
    FORMULA = 'formula'

    SOURCE = 'source'
    CODE = 'code'
    LIST = 'list'
    CAPTION = 'caption'

    QUESTION = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answer_options'

    ITALIC = 'i'
    BOLD = 'b'

    IMAGE = 'image'
    TABLE = 'table'  # placed around img tags for tables, may be useful later on

    # no hotkey bindings
    FIRST = 'first'  # first sentence inside <porque> tag
    SECOND = 'second'  # second sentence inside <porque> tag
    ITEM = 'item'  # for both questions and answers


class HTMLTag:
    def __init__(self, tag, style=None, generic_attributes=None):
        self.tag = tag
        self.style = style
        self.generic_attributes = generic_attributes or {}


XML_TO_HTML_TAG_MAPPING = {
    Tag.CENTERED_TEXT: HTMLTag('p', style='text-align: center'),
    Tag.TEXT_HEADER: HTMLTag('h1', style='text-align: left'),
    Tag.TITLE: HTMLTag('h1', style='text-align: center'),
    Tag.PORQUE: HTMLTag('div'),
    Tag.PQ: HTMLTag('p', style='text-align: center; font-style: bold; font-size: 20'),

    Tag.PARAGRAPH: HTMLTag('p'),
    Tag.TEXT: HTMLTag('pre'),

    # both have special handling
    Tag.LINK: HTMLTag('a'),
    Tag.FORMULA: HTMLTag('img'),

    Tag.IMAGE: HTMLTag('img', style='display: block; margin-left: auto; margin-right: auto; width: 80%;'),
    Tag.TABLE: HTMLTag('div'),
    Tag.CAPTION: HTMLTag('p', style='font-style: bold'),

    Tag.SOURCE: HTMLTag('p', style='font-style: italic'),
    Tag.CODE: HTMLTag(
        'code',
        style='font-family: monospace; white-space: pre;'
    ),
    Tag.LIST: HTMLTag('ul'),
    Tag.QUESTION: HTMLTag('p', style='font-size: 24'),

    Tag.QUESTION_OPTIONS: HTMLTag('ol', generic_attributes={'type': 'I'}),
    Tag.ANSWER_OPTIONS: HTMLTag('ol', generic_attributes={'type': 'A'}),

    Tag.FIRST: HTMLTag('p', style='text-align: center'),
    Tag.SECOND: HTMLTag('p', style='text-align: center'),
    Tag.ITEM: HTMLTag('li'),
}


def xml_to_html(xml_string):
    root = ET.fromstring(f"<root>{xml_string}</root>")
    for xml_tag, html_tag in XML_TO_HTML_TAG_MAPPING.items():
        for child in root.iter():
            elements = child.findall(xml_tag) or []
            for el in elements:
                el.tag = html_tag.tag

                if xml_tag == Tag.LINK:
                    el.text = el.text.replace(' ', '').replace('\r', '').replace('\n', '')
                    html_tag.generic_attributes = {
                        'href': el.text,
                    }

                if xml_tag == Tag.FORMULA:
                    html_tag.generic_attributes = {
                        'src': FORMULA_BASE_URL.format(el.text),
                        'alt': el.text,
                    }
                    el.text = ''

                if xml_tag == Tag.PQ:
                    el.text = 'PORQUE'

                el.set('class', xml_tag.replace('_', '-'))
                # styles are also set on css file
                if html_tag.style is not None:
                    el.set('style', f"{html_tag.style}")

                for attr, val in html_tag.generic_attributes.items():
                    el.set(attr, val)

    html = ET.tostring(root, encoding='unicode')

    indented = html.replace('\n', f"\n{' '*8}").replace('<root>', '').replace('</root>', '')
    return f"""
<html>
    <body>
        {indented}
    </body>
</html>
    """.strip()


if __name__ == '__main__':
  root_path = Path('.')
  for d in root_path.rglob('*[0-9].xml'):
    if str(d).startswith('venv'):
      continue
    xml = d.read_text(encoding='utf8')
    html = xml_to_html(xml)
    html_path = Path(f"{str(d).rstrip('.xml')}.html")
    if not html_path.exists():
      html_path.write_text(html, encoding='utf8')

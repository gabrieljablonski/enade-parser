import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

from xml_tags import Tag

DEFAULT_STYLE_SHEET_PATH = '../../quiz.css'

RELOAD_SCRIPT = """
<script>
    setInterval(function(){{
        window.open('file:///{file_path}', "_self")
    }}, {reload_interval});
</script>
"""

RELOAD_INTERVAL = 5000
FORMULA_BASE_URL = 'http://latex.codecogs.com/gif.latex?{}'


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


def xml_to_html(xml_string, file_path='', style_sheet_path=DEFAULT_STYLE_SHEET_PATH, include_reload_script=True):
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

    file_path = str(Path(file_path).absolute()).replace('\\','/')

    html = ET.tostring(root, encoding='unicode')

    reload_script = RELOAD_SCRIPT.format(
        file_path=quote(file_path, safe=':/'),
        reload_interval=RELOAD_INTERVAL
    ) if file_path and include_reload_script else ''

    indented = html.replace('\n', f"\n{' '*8}").replace('<root>', '').replace('</root>', '')
    return f"""
<html>
    <head>
        <link rel="stylesheet" href="{style_sheet_path}">
        {reload_script}
    </head>
    <body>
        {indented}
    </body>
</html>
    """

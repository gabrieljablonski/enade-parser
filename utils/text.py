import re
from pyperclip import copy, paste
from time import sleep
from html import escape

from utils.hotkeys import send_hotkey, Key
from xml_tags import Tag


DEFAULT_INDENT_LEVEL = 4
CRLF = '\r\n'


def sanitize(text):
    """
    removes white text around each line from `text`
    """
    return CRLF.join(map(str.strip, text.strip().split('\n')))


def modify_selected_text(modify, *args, **kwargs):
    send_hotkey(Key.CTRL, Key.C)
    sleep(.1)
    text = paste()
    new_text = modify(text, *args, **kwargs)
    if text.strip() != new_text:
        copy(new_text)
        sleep(.1)
        send_hotkey(Key.CTRL, Key.V)
        sleep(.1)
        return new_text


def indent_text(text, indent_level=DEFAULT_INDENT_LEVEL):
    ind = ' ' * indent_level
    lines = map(str.rstrip, text.split('\n'))
    return f"{ind}{f'{CRLF}{ind}'.join(lines)}"


def dedent_text(text, indent_level=DEFAULT_INDENT_LEVEL):
    ind = ' ' * indent_level
    out_lines = []
    for line in text.split('\n'):
        if line.startswith(ind):
            line = line[len(ind):]
        out_lines.append(line)
    return '\n'.join(out_lines)


def _auto_tag_link(text):
    match = re.match(r'([\s\S]*)(<(?:http|www)[\s\S]*?>)([\s\S]*)', text)
    if match is not None:
        b, link, a = match.groups()
        link = surround_with(link, tag=Tag.LINK, pad_nl=False, first_level_call=False)
        text = f"{b}{link}{a}"
    return text


def surround_with(text, tag, pad_nl=True, indent_level=DEFAULT_INDENT_LEVEL, first_level_call=True):
    """
        surrounds text with provided tag in XML style
        surround_with("text", "tag") -> "<tag>text</tag>"
    """
    text = text.strip()
    if tag == Tag.LINK:
        if not text.startswith('<') and not text.endswith('>'):
            print('Selected text is invalid. It should be: `<link>`')
            return text
        text = escape(text[1:-1])
    elif first_level_call:
        text = _auto_tag_link(text)

    if tag in (Tag.CODE, Tag.FORMULA):
        text = escape(text)

    if tag == Tag.PARAGRAPH and first_level_call:
        text = CRLF.join(s.strip() for s in text.split(CRLF))
        items = text.split(2 * CRLF)
        text = CRLF.join(surround_with(item, Tag.PARAGRAPH, first_level_call=False) for item in items)
        return text

    if tag == Tag.LIST:
        if '•' in text:
            items = filter(str.strip, text.split('•'))
        else:
            text = CRLF.join(s.strip() for s in text.split(CRLF))
            items = text.split(2*CRLF)
        text = CRLF.join(surround_with(item, Tag.ITEM) for item in items)

    if tag == Tag.PORQUE:
        match = re.match(r'([\s\S]*)PORQUE([\s\S]*)', text)
        if match is None:
            msg = f"""
                Failed to match options. Format should be:
                ```
                First sentence
                PORQUE
                Second sentence
                ```
                Each sentence may contain new lines within it.
            """
            print(sanitize(msg))
            return text
        first, second = match.groups()
        text = (
            f"{surround_with(first, tag=Tag.FIRST)}{CRLF}"
            f"<{Tag.PQ}/>{CRLF}"
            f"{surround_with(second, tag=Tag.SECOND)}"
        )

    if tag == Tag.QUESTION_OPTIONS and first_level_call:
        pattern = (
            r'^([\s\S]*?\n)?'
            r'I\. ([\s\S]*)\n'
            r'II\. ([\s\S]*)\n'
            r'III\. ([\s\S]*?)'
            r'(?:\nIV\. ([\s\S]*?))?'
            r'(?:\nV\. ([\s\S]*?))?'
            r'(?:\nVI\. ([\s\S]*?))?$'
        )
        match = re.match(pattern, sanitize(text))
        if match is None:
            msg = f"""
                Failed to match options. Format should be:
                ```
                I. option 1
                II. option 2
                III. option 3
                ...
                
                may contain from 3 to 6 options
                ```
                Each option may contain new lines within it.
            """
            print(sanitize(msg))
            return text
        paragraph, *options = match.groups()
        text = CRLF.join(
            surround_with(option, tag=Tag.ITEM)
            for option in options if option is not None
        )
        if paragraph:
            paragraph = surround_with(paragraph, tag=Tag.PARAGRAPH)
            question_options = surround_with(text, tag=Tag.QUESTION_OPTIONS, first_level_call=False)
            return f"{paragraph}{CRLF}{question_options}"

    
    if tag == Tag.ANSWER_OPTIONS and first_level_call:
        pattern = (
            r'^([\s\S]*?\n)?'
            r'\(?A\)? ([\s\S]*?)[\s]+' 
            r'\(?B\)? ([\s\S]*?)[\s]+' 
            r'\(?C\)? ([\s\S]*?)[\s]+'
            r'\(?D\)? ([\s\S]*?)[\s]+'
            r'\(?E\)? ([\s\S]*?)$'
        )
        match = re.match(pattern, sanitize(text))
        if match is None:
            msg = f"""
                Failed to match options. Format should be:
                ```
                A option 1
                B option 2
                C option 3
                D option 4
                
                or
                
                A) option 1
                B) option 2
                C) option 3
                D) option 4
                ```
                Each option may contain new lines within it.
            """
            print(sanitize(msg))
            return text
        question, *options = match.groups()
        text = CRLF.join(
            surround_with(option, tag=Tag.ITEM)
            for option in options if option is not None
        )
        if question:
            question = surround_with(question, tag=Tag.QUESTION)
            answer_options = surround_with(text, tag=Tag.ANSWER_OPTIONS, first_level_call=False)
            return f"{question}{CRLF}{answer_options}"

    padding = CRLF if pad_nl else ''
    content = text if not padding else indent_text(text, indent_level)
    return f"""<{tag}>{padding}{content}{padding}</{tag}>"""


def remove_tag(text):
    """
        removes outmost pair of opening and closing tags
        remove_tag("<tag>text</tag>") -> "text"
    """
    text = text.strip()
    match = re.match(r'^<(\w*)>([\s\S]*)</(\w*)>$', text)
    if match is None:
        print(f"No match when trying to remove tags in {repr(text)}")
        return text
    tag_open, out_text, tag_close = match.groups()
    if tag_open != tag_close:
        print(f"Opening tag is different from closing tag in {repr(text)}")
        return text
    return dedent_text(out_text).strip()

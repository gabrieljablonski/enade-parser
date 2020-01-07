import re
from pyperclip import copy, paste

from utils.hotkeys import send_hotkey, Key
from xml_tag_mapping import Tag


DEFAULT_INDENT_LEVEL = 4
CRLF = '\r\n'


def sanitize(text):
    """
    removes white text around each line from `text`
    """
    return CRLF.join(map(str.strip, text.strip().split('\n')))


def modify_selected_text(modify, *args, **kwargs):
    send_hotkey(Key.CTRL, Key.C)
    text = paste()
    new_text = modify(text, *args, **kwargs)
    if text.strip() != new_text:
        copy(new_text)
        send_hotkey(Key.CTRL, Key.V)


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


def surround_with(text, tag, pad_nl=True, indent_level=DEFAULT_INDENT_LEVEL):
    """
        surrounds text with provided tag in XML style
        surround_with("text", "tag") -> "<tag>text</tag>"
    """
    text = text.strip()
    if tag == Tag.LINK:
        if not text.startswith('<') and not text.endswith('/>'):
            print('Selected text is invalid. It should be: `<link/>')
            return text
        text = text[1:-2]

    if tag in (Tag.QUESTION_OPTIONS, Tag.ANSWER_OPTIONS):
        if tag == Tag.QUESTION_OPTIONS:
            fmt = """
                I. option 1
                II. option 2
                III. option 3
                ...
            """
            pattern = r'^I\. ([\s\S]*)\nII\. ([\s\S]*)\nIII\. ([\s\S]*?)(?:\nIV\. ([\s\S]*?))?(?:\nV\. ([\s\S]*?))?$'
        else:
            fmt = """
                A option 1
                B option 2
                C option 3

                D option 4
                
                or
                
                A) option 1
                B) option 2
                C) option 3
                D) option 4
            """
            pattern = r'^\(?A\)? ([\s\S]*)[\s]+\(?B\)? ([\s\S]*)[\s]+\(?C\)? ([\s\S]*)[\s]+\(?D\)? ([\s\S]*)[\s]+\(?E\)? ([\s\S]*)$'
        options = re.match(pattern, sanitize(text))
        if options is None:
            msg = f"""
                Failed to match options. Format should be:
                ```
                {fmt.strip()}
                ```
                Each option may contain new lines within it.
            """
            print(sanitize(msg))
            return text
        text = CRLF.join(
            surround_with(option, tag=Tag.OPTION)
            for option in options.groups() if option is not None
        )

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

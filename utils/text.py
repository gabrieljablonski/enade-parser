import re
from pyperclip import copy, paste

from hotkeys import send_hotkey, Key
from xml_tags import Tag


DEFAULT_INDENT_LEVEL = 4


def modify_selected_text(modify, *args, **kwargs):
    send_hotkey(Key.CTRL, Key.C)
    text = paste()
    new_text = modify(text, *args, **kwargs)
    copy(new_text)
    send_hotkey(Key.CTRL, Key.V)


def indent_text(txt, indent_level=DEFAULT_INDENT_LEVEL):
    ind = ' ' * indent_level
    lines = txt.split('\n')
    return f"{ind}{ind.join(lines)}"


def dedent_text(txt, indent_level=DEFAULT_INDENT_LEVEL):
    ind = ' ' * indent_level
    out_lines = []
    for line in txt.split('\n'):
        if line.startswith(ind):
            line = line[len(ind):]
        out_lines.append(line)
    return '\n'.join(out_lines)


def surround_with(txt, tag, pad_nl=True, indent_level=DEFAULT_INDENT_LEVEL):
    """
        surrounds text with provided tag in XML style
        surround_with("txt", "tag") -> "<tag>txt</tag>"
    """
    txt = txt.strip()
    if tag == Tag.LINK:
        if not txt.startswith('<') and not txt.endswith('/>'):
            print('Selected text is invalid. It should be: `<link/>')
            return txt
        txt = txt[1:-2]
    padding = '\n' if pad_nl else ''
    content = txt if not padding else indent_text(txt, indent_level)
    return f"""<{tag}>{padding}{content}{padding}</{tag}>"""


def remove_tag(txt):
    """
        removes outmost pair of opening and closing tags
        remove_tag("<tag>txt</tag>") -> "txt"
    """
    txt = txt.strip()
    match = re.match(r'^<(\w*)>([\s\S]*)</(\w*)>$', txt)
    if match is None:
        print(f"No match when removing tags in {repr(txt)}")
        return txt
    tag_open, out_text, tag_close = match.groups()
    if tag_open != tag_close:
        print(f"Opening tag is different from closing tag in {repr(txt)}")
        return txt
    return dedent_text(out_text).strip()

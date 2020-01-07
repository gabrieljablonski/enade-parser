from hotkeys import Key, join_hotkeys


class Tag:
    HEADER = 'header'  # centered
    TXT_HEADER = 'text_header'  # left aligned
    PORQUE = 'porque'
    PARAGRAPH = 'paragraph'
    LINK = 'link'

    IMG_SOURCE = 'img_src'
    TXT_SOURCE = 'txt_src'

    QUESTION_BODY = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answers'

    ITALIC = 'i'
    BOLD = 'b'


BASE_MAPPING = {
    Key.Z: Tag.HEADER,
    Key.X: Tag.PORQUE,
    Key.V: Tag.TXT_HEADER,
    Key.A: Tag.PARAGRAPH,
    Key.S: Tag.QUESTION_BODY,
    Key.F: Tag.ANSWER_OPTIONS,
    Key.G: Tag.TXT_SOURCE,
    Key.H: Tag.QUESTION_OPTIONS,
    Key.J: Tag.IMG_SOURCE,
    Key.L: Tag.LINK,

    Key.I: Tag.ITALIC,
    Key.B: Tag.BOLD,
}

TAG_HOTKEY_PREFIX = Key.CTRL, Key.ALT
TAG_MAPPING = {
    join_hotkeys(*TAG_HOTKEY_PREFIX, k): v
    for k, v in BASE_MAPPING.items()
}
REMOVE_TAG = join_hotkeys(*TAG_HOTKEY_PREFIX, Key.R)

NO_PADDING = Tag.ITALIC, Tag.BOLD, Tag.LINK

from hotkeys import Key


class Tag:
    CENTERED_HEADER = 'header'
    PORQUE = 'porque'
    TXT_HEADER = 'text_header'  # left aligned
    PARAGRAPH = 'paragraph'

    IMG_SOURCE = 'img_src'
    TXT_SOURCE = 'txt_src'

    QUESTION_BODY = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answers'


TAG_PREFIX = 'ctrl+alt'
BASE_MAPPING = {
    Key.A: Tag.CENTERED_HEADER,
    Key.S: Tag.PORQUE,
    Key.D: Tag.TXT_HEADER,
    Key.F: Tag.PARAGRAPH,
    Key.G: Tag.IMG_SOURCE,
    Key.H: Tag.TXT_SOURCE,
    Key.J: Tag.QUESTION_BODY,
    Key.K: Tag.QUESTION_OPTIONS,
    Key.L: Tag.ANSWER_OPTIONS,
}

TAG_MAPPING = {
    f"{TAG_PREFIX}+{k}": v
    for k, v in BASE_MAPPING.items()
}

REMOVE_TAG = f"{TAG_PREFIX}+{Key.R}"

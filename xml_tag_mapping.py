from utils.hotkeys import Key, join_hotkeys


class Tag:
    TXT_HEADER = 'text_header'  # 'texto 01', 'texto 02', ...; left aligned
    TITLE = 'title'  # generic title, centered
    PORQUE = 'porque'

    PARAGRAPH = 'paragraph'  # generic paragraph, formatting is not relevant
    TEXT = 'text'  # text that should maintain its formatting (e.g. poems)
    LINK = 'link'
    FORMULA = 'formula'

    IMG_SOURCE = 'img_src'
    TXT_SOURCE = 'txt_src'

    QUESTION_BODY = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answers'

    ITALIC = 'i'
    BOLD = 'b'

    # not hotkey bindings
    FIRST = 'first'  # first sentence inside <porque> tag
    SECOND = 'second'  # second sentence inside <porque> tag
    OPTION = 'option'  # for both questions and answers


BASE_MAPPING = {
    Key.X: Tag.PORQUE,
    Key.V: Tag.TXT_HEADER,
    Key.A: Tag.PARAGRAPH,
    Key.S: Tag.TXT_SOURCE,
    Key.F: Tag.FORMULA,
    Key.G: Tag.QUESTION_BODY,
    Key.H: Tag.QUESTION_OPTIONS,
    Key.J: Tag.IMG_SOURCE,
    Key.K: Tag.ANSWER_OPTIONS,
    Key.L: Tag.LINK,
    Key.T: Tag.TITLE,
    Key.Y: Tag.TEXT,

    Key.I: Tag.ITALIC,
    Key.B: Tag.BOLD,
}

TAG_HOTKEY_PREFIX = Key.CTRL, Key.ALT
TAG_MAPPING = {}
REVERSE_MAPPING = {}

for k, v in BASE_MAPPING.items():
    hk = join_hotkeys(*TAG_HOTKEY_PREFIX, k)
    TAG_MAPPING[hk] = v
    REVERSE_MAPPING[v] = [hk]

HK_REMOVE_TAG = join_hotkeys(*TAG_HOTKEY_PREFIX, Key.R)

NO_PADDING = Tag.ITALIC, Tag.BOLD, Tag.LINK, Tag.FORMULA

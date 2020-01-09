from utils.hotkeys import Key, join_hotkeys


class Tag:
    TXT_HEADER = 'text_header'  # 'texto 01', 'texto 02', ...; left aligned
    TITLE = 'title'  # generic title, centered
    PORQUE = 'porque'

    TEXT_BLOCK = 'text_block'  # generic paragraphs, formatting is not relevant
    TEXT = 'text'  # text that should maintain its formatting (e.g. poems)
    LINK = 'link'
    FORMULA = 'formula'

    SOURCE = 'source'
    LIST = 'list'

    QUESTION_BODY = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answers'

    ITALIC = 'i'
    BOLD = 'b'

    # not hotkey bindings
    FIRST = 'first'  # first sentence inside <porque> tag
    SECOND = 'second'  # second sentence inside <porque> tag
    ITEM = 'item'  # for both questions and answers
    PARAGRAPH = 'paragraph'  # text block element


BASE_MAPPING = {
    Key.X: Tag.PORQUE,
    Key.V: Tag.TXT_HEADER,
    Key.A: Tag.TEXT_BLOCK,
    Key.S: Tag.SOURCE,
    Key.F: Tag.FORMULA,
    Key.G: Tag.QUESTION_BODY,
    Key.H: Tag.QUESTION_OPTIONS,
    Key.K: Tag.ANSWER_OPTIONS,
    Key.L: Tag.LINK,
    Key.T: Tag.TITLE,
    Key.Y: Tag.TEXT,
    Key.O: Tag.LIST,

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

NO_PADDING = Tag.ITALIC, Tag.BOLD, Tag.LINK, Tag.FORMULA, Tag.TXT_HEADER

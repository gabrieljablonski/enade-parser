from utils.hotkeys import Key, join_hotkeys
from xml_tags import Tag


HK_CAPTURE_IMAGE = Key.CTRL, Key.SPACE
HK_CAPTURE_OCR = Key.CTRL, Key.ALT, Key.ENTER
HK_TOGGLE_KEYBOARD = Key.CTRL, Key.SHIFT, Key.ALT
HK_CANCEL = Key.ESC
HK_CONFIRM = Key.ENTER


BASE_MAPPING = {
    Key.X: Tag.PORQUE,
    Key.V: Tag.TEXT_HEADER,
    Key.M: Tag.CAPTION,

    Key.A: Tag.TEXT_BLOCK,
    Key.S: Tag.SOURCE,
    Key.F: Tag.FORMULA,
    Key.G: Tag.QUESTION,
    Key.H: Tag.QUESTION_OPTIONS,
    Key.K: Tag.ANSWER_OPTIONS,
    Key.L: Tag.LINK,

    Key.T: Tag.TITLE,
    Key.Y: Tag.TEXT,
    Key.O: Tag.LIST,
    Key.P: Tag.TABLE,

    Key.I: Tag.ITALIC,
    Key.B: Tag.BOLD,
}

TAG_HOTKEY_PREFIX = Key.CTRL, Key.ALT
TAG_MAPPING = {}
REVERSE_TAG_MAPPING = {}

for k, v in BASE_MAPPING.items():
    hk = join_hotkeys(*TAG_HOTKEY_PREFIX, k)
    TAG_MAPPING[hk] = v
    REVERSE_TAG_MAPPING[v] = [hk]

HK_REMOVE_TAG = join_hotkeys(*TAG_HOTKEY_PREFIX, Key.R)

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


# tags are placed `<tag>text</tag>` instead of `<tag>\ntext\n</tag>`
NO_PADDING = Tag.ITALIC, Tag.BOLD, Tag.LINK, Tag.FORMULA, Tag.TEXT_HEADER
# won't trigger the append to file function, even in auto mode
NO_AUTO_SAVE = (
    Tag.ITALIC, 
    Tag.BOLD, 
    Tag.LINK, 
    Tag.FORMULA, 
    Tag.TABLE,
)

class Tag:
    TEXT_HEADER = 'text_header'  # 'texto 01', 'texto 02', ...; left aligned
    TITLE = 'title'  # generic title, centered
    PORQUE = 'porque'

    TEXT_BLOCK = 'text_block'  # generic paragraphs, formatting is not relevant
    TEXT = 'text'  # text that should maintain its formatting (e.g. poems)
    LINK = 'link'
    FORMULA = 'formula'

    SOURCE = 'source'
    LIST = 'list'
    CAPTION = 'caption'

    QUESTION_BODY = 'question'
    QUESTION_OPTIONS = 'question_options'
    ANSWER_OPTIONS = 'answers'

    ITALIC = 'i'
    BOLD = 'b'

    TABLE = 'table'  # placed around img tags for tables, may be useful later on

    # no hotkey bindings
    FIRST = 'first'  # first sentence inside <porque> tag
    SECOND = 'second'  # second sentence inside <porque> tag
    ITEM = 'item'  # for both questions and answers
    PARAGRAPH = 'paragraph'  # text block element


# tags are placed `<tag>text</tag>` instead of `<tag>\ntext\n</tag>`
NO_PADDING = Tag.ITALIC, Tag.BOLD, Tag.LINK, Tag.FORMULA, Tag.TEXT_HEADER

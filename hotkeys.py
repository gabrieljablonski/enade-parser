from string import ascii_uppercase


class Key:
    CTRL = 'ctrl'
    SPACE = 'space'
    ALT = 'alt'

    CTRL_SPACE = f"{CTRL}+{SPACE}"

    def __init__(self):
        for c in ascii_uppercase:
            self.__dict__[c] = c.lower()


Key = Key()

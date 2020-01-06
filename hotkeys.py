from string import ascii_uppercase
import keyboard as kb
from time import sleep


class Key:
    CTRL = 'ctrl'
    SPACE = 'space'
    SHIFT = 'shift'
    ALT = 'alt'
    PRNT_SCRN = 'print screen'

    def __init__(self):
        for c in ascii_uppercase:
            self.__dict__[c] = c.lower()


Key = Key()


def _join_hotkeys(*hotkeys):
    return '+'.join(hotkeys)


def _join_hotkeys_decorator(f):
    """
    allows the function to be called as either
        f(hk1, hk2, ...)
    or
        f('hk1+hk2+...')
    """
    def new_f(*hotkeys):
        return f(_join_hotkeys(*hotkeys))
    return new_f


@_join_hotkeys_decorator
def is_pressed(hotkey):
    pressed = kb.is_pressed(hotkey)
    if pressed:
        kb.release(hotkey)
    return pressed


@_join_hotkeys_decorator
def send_hotkey(hotkey):
    kb.press_and_release(hotkey)
    sleep(.05)

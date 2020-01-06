import keyboard as kb
import cv2
import pytesseract
import numpy as np
import re
from PIL import ImageGrab
from pyperclip import copy, paste
from time import time, sleep

from xml_tags import TAG_MAPPING, REMOVE_TAG


# REMINDER TO DOWNLOAD `por.traineddata`
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def is_pressed(hotkey):
    global last_action
    pressed = kb.is_pressed(hotkey)
    if pressed:
        last_action = now
        kb.release(hotkey)
    return pressed


def modify_selected_text(modify, *args, **kwargs):
    send_hotkey('ctrl+c')
    text = paste()
    new_text = modify(text, *args, **kwargs)
    copy(new_text)
    send_hotkey('ctrl+v')


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


def indent_text(txt, indent_level=2):
    ind = ' ' * indent_level
    lines = txt.split('\n')
    return f"{ind}{ind.join(lines)}"


def dedent_text(txt, indent_level=2):
    ind = ' ' * indent_level
    out_lines = []
    for line in txt.split('\n'):
        if line.startswith(ind):
            line = line[len(ind):]
        out_lines.append(line)
    return '\n'.join(out_lines)


def surround_with(txt, tag, pad_nl=True, indent_level=2):
    """
        surrounds text with provided tag in XML style
        surround_with("txt", "tag") -> "<tag>txt</tag>"
    """
    txt = txt.strip()
    padding = '\n' if pad_nl else ''
    content = txt if not padding else indent_text(txt, indent_level)
    return f"""<{tag}>{padding}{content}{padding}</{tag}>"""


def crop(img, roi):
    return img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]


def send_hotkey(hotkey):
    kb.press_and_release(hotkey)
    sleep(.05)


def capture_picture():
    send_hotkey('alt+print screen')
    img = ImageGrab.grabclipboard()

    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    roi = cv2.selectROI('select', image)
    crop_image = crop(image, roi)

    gray = cv2.bitwise_not(cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY))
    roi = cv2.boundingRect(gray)

    final_image = crop(crop_image, roi)
    cv2.imshow('img', final_image)

    txt = pytesseract.image_to_string(gray, lang='por')
    print(txt)


keyboard_grab_activated = True
last_action = time()
action_delay = 1.
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        cv2.destroyAllWindows()
        exit()
    now = time()
    if now - last_action > action_delay:
        if is_pressed('ctrl+shift'):
            keyboard_grab_activated = not keyboard_grab_activated
            print(f"keyboard {'de' if not keyboard_grab_activated else ''}activated")

        if not keyboard_grab_activated:
            continue

        if is_pressed('space'):
            capture_picture()

        for hk, tag in TAG_MAPPING.items():
            if is_pressed(hk):
                modify_selected_text(surround_with, tag=tag)

        if is_pressed(REMOVE_TAG):
            modify_selected_text(remove_tag)

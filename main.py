import cv2
from time import time

from hotkeys import is_pressed, Key
from xml_tags import TAG_MAPPING, REMOVE_TAG
from utils.text import modify_selected_text, surround_with, remove_tag
from utils.image import capture_picture


ACTION_DELAY = 1.


def main():
    keyboard_grab_activated = True
    last_action = time()
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            cv2.destroyAllWindows()
            exit()
        now = time()
        hotkey_pressed = False
        if now - last_action > ACTION_DELAY:
            if is_pressed(Key.CTRL, Key.SHIFT):
                hotkey_pressed = True
                keyboard_grab_activated = not keyboard_grab_activated
                print(f"keyboard {'de' if not keyboard_grab_activated else ''}activated")

            if not keyboard_grab_activated:
                continue

            if is_pressed(Key.SPACE):
                hotkey_pressed = True
                cv2.imshow('image', capture_picture())

            for hk, tag in TAG_MAPPING.items():
                if is_pressed(hk):
                    hotkey_pressed = True
                    modify_selected_text(surround_with, tag=tag)

            if is_pressed(REMOVE_TAG):
                hotkey_pressed = True
                modify_selected_text(remove_tag)


if __name__ == '__main__':
    main()

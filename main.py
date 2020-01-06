import cv2
from time import time, sleep

from hotkeys import is_pressed, Key
from xml_tags import TAG_MAPPING, REMOVE_TAG, NO_PADDING
from utils.text import modify_selected_text, surround_with, remove_tag
from utils.image import capture_picture, WIN_NAME_CAPTURE, WIN_NAME_CROP


ACTION_DELAY = 1.

# BadDrawable:
# sudo nano /etc/environment
# QT_X11_NO_MITSHM=1


def check_image_operations(image_open, hotkey_pressed):
    if image_open:
        pressed = False
        if is_pressed(Key.ESC):
            pressed = True
            print('Cancelling image capture.')
        elif is_pressed(Key.ENTER):
            pressed = True
            print('Saving image.')
        if pressed:
            cv2.destroyWindow(WIN_NAME_CAPTURE)
            image_open = False

    if is_pressed(Key.CTRL, Key.SPACE):
        hotkey_pressed = True
        if image_open:
            print('Finish the operation with the last image first.')
        else:
            print("Capturing image.")
            img = capture_picture()
            cv2.destroyWindow(WIN_NAME_CROP)
            if img is None:
                print('Canceled image capture.')
            else:
                cv2.imshow(WIN_NAME_CAPTURE, img)
                image_open = True

    return image_open, hotkey_pressed


def check_tag_operations(hotkey_pressed):
    for hk, tag in TAG_MAPPING.items():
        if is_pressed(hk):
            print(f"Inserting {tag}.")
            hotkey_pressed = True
            pad = tag not in NO_PADDING
            modify_selected_text(surround_with, tag=tag, pad_nl=pad)

    if is_pressed(REMOVE_TAG):
        print(f"Removed tag.")
        hotkey_pressed = True
        modify_selected_text(remove_tag)

    return hotkey_pressed


def main():
    image_open = False
    keyboard_grab_activated = True
    last_action = time()

    while True:
        _ = cv2.waitKey(1) & 0xFF
        now = time()
        hotkey_pressed = False
        if now - last_action > ACTION_DELAY:
            if is_pressed(Key.CTRL, Key.SHIFT):
                hotkey_pressed = True
                keyboard_grab_activated = not keyboard_grab_activated
                print(f"keyboard {'de' if not keyboard_grab_activated else ''}activated")

            if keyboard_grab_activated:
                image_open, hotkey_pressed = check_image_operations(image_open, hotkey_pressed)
                hotkey_pressed = check_tag_operations(hotkey_pressed)
            if hotkey_pressed:
                last_action = time()


if __name__ == '__main__':
    main()

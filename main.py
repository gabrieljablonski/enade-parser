import cv2
from time import time, sleep

from utils.text import modify_selected_text, surround_with, remove_tag, copy
from utils.image import capture_image, WIN_NAME_CAPTURE, WIN_NAME_CROP
from utils.ocr import get_text_in_image
from hotkeys import is_pressed, Key
from xml_tags import TAG_MAPPING, REMOVE_TAG, NO_PADDING


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
            print('Capturing image.')
            img = capture_image()
            if img is None:
                print('Canceled image capture.')
            else:
                cv2.imshow(WIN_NAME_CAPTURE, img)
                image_open = True

    return image_open, hotkey_pressed


def check_tag_operations(hotkey_pressed):
    for hk, tag in TAG_MAPPING.items():
        if is_pressed(hk):
            hotkey_pressed = True
            print(f"Inserting `{tag}` tag.")
            pad_nl = tag not in NO_PADDING
            modify_selected_text(surround_with, tag=tag, pad_nl=pad_nl)
            break

    if is_pressed(REMOVE_TAG):
        hotkey_pressed = True
        print('Removed tag.')
        modify_selected_text(remove_tag)

    return hotkey_pressed


def check_ocr_operations(hotkey_pressed):
    if is_pressed(Key.CTRL, Key.ALT, Key.SPACE):
        hotkey_pressed = True
        print('Capturing image for text extraction.')
        img = capture_image(grayscale=True)
        if img is None:
            print('Canceled image capture.')
            return hotkey_pressed

        txt = get_text_in_image(img)
        copy(txt)
        print(f"Copied text to clipboard: {repr(txt)}")

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
                hotkey_pressed = check_ocr_operations(hotkey_pressed)
            if hotkey_pressed:
                last_action = time()


if __name__ == '__main__':
    main()

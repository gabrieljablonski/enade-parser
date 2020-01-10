import os
import re
import glob
import cv2
from time import time, sleep
from unidecode import unidecode
from pathlib import Path
from threading import Thread

from tkinter.filedialog import askopenfilename
from tkinter import Tk
Tk().withdraw()
del Tk

from utils.text import modify_selected_text, surround_with, remove_tag, copy
from utils.image import capture_image, WIN_NAME_CAPTURE
from utils.ocr import set_tesseract_path, get_text_in_image
from utils.hotkeys import is_pressed, Key, join_hotkeys
from utils.static_vars import static_vars

from xml_tags import NO_PADDING
from hotkey_mapping import (
    TAG_MAPPING, HK_REMOVE_TAG, HK_TOGGLE_KEYBOARD, HK_CONFIRM, HK_CANCEL, HK_CAPTURE_OCR, HK_CAPTURE_IMAGE
)
from convert_xml_to_html import xml_to_html, RELOAD_INTERVAL

# BadDrawable:
# sudo nano /etc/environment
# QT_X11_NO_MITSHM=1

ACTION_DELAY = 1.

CURRENT_QUESTION_FILE_NAME = 'current_question.xml'
CURRENT_QUESTION_HTML = CURRENT_QUESTION_FILE_NAME.replace('xml', 'html')

IMAGES_DIR_NAME = 'images'


@static_vars(image=None)
def check_image_operations(image_open, hotkey_pressed):
    if image_open:
        pressed = False
        if is_pressed(HK_CANCEL):
            pressed = True
            print('Cancelling image capture.')
        elif is_pressed(HK_CONFIRM):
            try:
                out_path = save_image(check_image_operations.image).replace('\\', '/')

                tag = f'<img src="{out_path}" />'
                copy(tag)
                print(f"Copied tag to clipboard: {repr(tag)}")

                pressed = True
            except Exception as e:
                print(f"Failed to save image: {e}")
        if pressed:
            cv2.destroyWindow(WIN_NAME_CAPTURE)
            image_open = False

    if is_pressed(HK_CAPTURE_IMAGE):
        hotkey_pressed = True
        if image_open:
            print('Finish the operation with the last image first.')
        else:
            print('Capturing image.')
            img = capture_image()
            check_image_operations.image = img
            if img is None:
                print('Canceled image capture.')
            else:
                print(f"Showing captured image. "
                      f"Press `{HK_CANCEL.upper()}` to cancel or `{HK_CONFIRM.upper()}` to confirm.")
                cv2.imshow(WIN_NAME_CAPTURE, img)
                image_open = True

    return image_open, hotkey_pressed


def check_tag_operations(hotkey_pressed):
    for hk, tag in TAG_MAPPING.items():
        if is_pressed(hk):
            hotkey_pressed = True
            # print(f"Inserting `{tag}` tag.")
            pad_nl = tag not in NO_PADDING
            modify_selected_text(surround_with, tag=tag, pad_nl=pad_nl)
            break

    if is_pressed(HK_REMOVE_TAG):
        hotkey_pressed = True
        print('Removed tag.')
        modify_selected_text(remove_tag)

    return hotkey_pressed


def check_ocr_operations(hotkey_pressed):
    if is_pressed(HK_CAPTURE_OCR):
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


def save_image(image):
    prefix = get_output_file_path_prefix()
    images = glob.glob(f"{IMAGES_DIR_NAME}/*_{menu.current_question}_*.png")

    if not images:
        index = 0
    else:
        images.sort()
        last_image = images[-1]
        match = re.match(r'.*(\d+)\.png$', last_image)
        index = int(match.group(1)) + 1

    out_path = Path(f"{prefix}_{menu.question_type}_{menu.current_question}_{index}.png")
    out_path = str(Path(IMAGES_DIR_NAME).joinpath(out_path))
    cv2.imwrite(out_path, image)
    print(f"Image saved as {out_path}")
    return out_path


def save_question():
    prefix = get_output_file_path_prefix()
    out_path = Path(f"{prefix}_{menu.question_type}_{menu.current_question}.xml")
    if out_path.exists():
        print(f"File {out_path} already exists. Are you sure you want to override it? (Y/N)")
        if not prompt_yn():
            raise OSError(f"File {out_path} already exists")
        os.remove(out_path)

    print(f"Saving question as: {out_path}")
    try:
        with open(CURRENT_QUESTION_FILE_NAME, encoding='utf8') as f:
            xml = f.read()
        xml = f"<html>{xml}</html>"
        html_path = str(out_path).replace('xml', 'html')
        html = xml_to_html(xml)
        with open(html_path, 'w', encoding='utf8') as out:
            out.write(html)
    except Exception as e:
        print(f"Failed to save HTML: {e}")
    try:
        os.rename(CURRENT_QUESTION_FILE_NAME, out_path)
    except OSError as e:
        raise OSError(f"failed to rename file {CURRENT_QUESTION_FILE_NAME} to {out_path}: {e}")


def prompt_yn():
    while True:
        opt = input('>> ')
        if opt.lower() in ('y', 'n'):
            return opt == 'y'


def get_subject_year():
    while True:
        print('Type out the subject and year in the format: <subject>, <year>')
        inp = input('>> ').split(',')
        inp = list(map(str.strip, inp))
        if len(inp) != 2 or not inp[0] or not inp[1]:
            print('Invalid format.')
            continue
        subject, year = inp
        print(
            f"-Subject: {subject}\n"
            f"-Year: {year}\n"
            f"Is this correct? (Y/N)"
        )
        if prompt_yn():
            return subject, year


def open_current_question_file():
    open(CURRENT_QUESTION_FILE_NAME, 'a').close()
    os.system(CURRENT_QUESTION_FILE_NAME)


def get_output_file_path_prefix():
    s = '_'.join(filter(str.strip, menu.subject.replace('-', '').split()))
    return f"{unidecode(s.lower())}_{menu.year}"


@static_vars(subject='', year='', current_question=1, question_type='d')
def menu():
    while True:
        if not menu.subject:
            print('Select the file to be analyzed.')
            file_name = askopenfilename()
            manual = True
            if file_name:
                subject, year = map(str.strip, os.path.split(file_name)[1].split('_')[0:2])
                print(
                    f"Info from file `{file_name}`\n"
                    f"-Subject: {subject}\n"
                    f"-Year: {year}\n"
                    f"Is this correct? (Y/N)"
                )
                manual = not prompt_yn()
            if manual:
                subject, year = get_subject_year()

            menu.subject, menu.year = subject, year
            base_path = f"{subject} {year}"
            Path(base_path).joinpath(Path(IMAGES_DIR_NAME)).mkdir(parents=True, exist_ok=True)
            os.chdir(base_path)
        else:
            qt = 'discursive' if menu.question_type == 'd' else 'multiple choice'
            options = {
                1: 'Enable keyboard grab.',
                2: f"Change current question number (current is {menu.current_question}).",
                3: f"Change current question type (current is {qt}).",
                4: 'Change subject/year.',
                5: 'Save current question.',
                6: 'Open HTML preview.',
                0: 'Exit.'
            }
            print('Choose an option:')
            for o, txt in options.items():
                print(f"-{o}: {txt}")
            while True:
                inp = input('>> ')
                try:
                    opt = int(inp)
                    if opt not in options:
                        raise ValueError
                    break
                except ValueError:
                    print('Invalid option')

            if opt == 0:
                exit()

            if opt == 1:
                print(f"Enabling keyboard grab, use {join_hotkeys(HK_TOGGLE_KEYBOARD).upper()} to disable it.")
                open_current_question_file()
                return

            if opt == 2:
                print('Insert new question number:')
                while True:
                    inp = input('>> ')
                    try:
                        question_number = int(inp)
                        if question_number < 1:
                            raise ValueError
                        menu.current_question = question_number
                        break
                    except ValueError:
                        print('Invalid question number.')

            if opt == 3:
                print('Is the question multiple choice or discursive? (M/d)')
                while True:
                    inp = input('>> ')
                    if not inp or inp.lower() in ('m', 'd'):
                        menu.question_type = inp.lower() or 'm'
                        break

            if opt == 4:
                os.chdir('..')
                menu.subject, menu.year, menu.active_dir, menu.images_dir, menu.current_question = '', '', '', '', 1
                continue

            if opt == 5:
                prefix = get_output_file_path_prefix()
                try:
                    save_question()
                except OSError as e:
                    print(e)
                else:
                    menu.current_question += 1
                finally:
                    continue

            if opt == 6:
                os.system(CURRENT_QUESTION_HTML)


def update_html_file():
    html_opened = False

    def wait_for_xml_file():
        while True:
            if not os.path.exists(CURRENT_QUESTION_FILE_NAME):
                sleep(1)
                continue
            break

    while True:
        try:
            with open(CURRENT_QUESTION_FILE_NAME, encoding='utf8') as f:
                xml = f.read()
            if not xml and html_opened:
                continue
        except FileNotFoundError:
            wait_for_xml_file()
            continue
        else:
            xml = (
                f"<html><h1>Question Number: {menu.current_question}</h1><br/>\n"
                f"{xml}\n"
                f"</html>\n"
            )
            try:
                html = xml_to_html(xml, CURRENT_QUESTION_HTML)
            except:
                continue
            else:
                try:
                    with open(CURRENT_QUESTION_HTML, 'w', encoding='utf8') as f:
                        f.write(html)
                except Exception as e:
                    print(f"Failed to save HTML preview: {e}")
                if not html_opened:
                    os.system(CURRENT_QUESTION_HTML)
                    html_opened = True
        finally:
            sleep(0.5*RELOAD_INTERVAL/1000)


def main():
    image_open = False
    keyboard_grab_activated = False
    last_action = time()

    Thread(target=update_html_file, daemon=True).start()

    while True:
        _ = cv2.waitKey(1) & 0xFF
        now = time()
        if not keyboard_grab_activated:
            menu()
            keyboard_grab_activated = True

        hotkey_pressed = False
        if now - last_action > ACTION_DELAY:
            if is_pressed(HK_TOGGLE_KEYBOARD):
                hotkey_pressed = True
                keyboard_grab_activated = False
                print(f"Keyboard deactivated")

            if keyboard_grab_activated:
                image_open, hotkey_pressed = check_image_operations(image_open, hotkey_pressed)
                hotkey_pressed = check_tag_operations(hotkey_pressed)
                hotkey_pressed = check_ocr_operations(hotkey_pressed)
            if hotkey_pressed:
                last_action = time()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Enade parser.')
    parser.add_argument('--tesseract-path', default='', type=str, help='path to the tesseract binary')
    args = parser.parse_args()

    set_tesseract_path(args.tesseract_path)

    main()

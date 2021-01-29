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
from utils.hotkeys import is_pressed, Key, join_hotkeys, kb
from utils.static_vars import static_vars

from xml_tags import Tag, NO_PADDING, NO_AUTO_SAVE
from hotkey_mapping import (
    TAG_MAPPING, HK_REMOVE_TAG, HK_TOGGLE_MODE, HK_CONFIRM, HK_CANCEL, HK_CAPTURE_OCR, HK_CAPTURE_IMAGE, HK_BACK_TO_MENU
)
from convert_xml_to_html import xml_to_html, RELOAD_INTERVAL

# BadDrawable:
# sudo nano /etc/environment
# QT_X11_NO_MITSHM=1

ACTION_DELAY = .5

CURRENT_QUESTION_FILE_NAME = 'current_question.xml'
CURRENT_QUESTION_HTML = CURRENT_QUESTION_FILE_NAME.replace('xml', 'html')

IMAGES_DIR_NAME = 'images'


def append_to_current_question(text):
    text = text.replace('\r\n', '\n')
    with open(CURRENT_QUESTION_FILE_NAME, 'a', encoding='utf8') as out:
        out.write(f"{text}\n")


@static_vars(image=None)
def check_image_operations(image_open, hotkey_pressed, mode):
    if image_open:
        pressed = False
        if is_pressed(HK_CANCEL):
            pressed = True
            print('Cancelling image capture.')
        elif is_pressed(HK_CONFIRM):
            try:
                out_path = save_image(check_image_operations.image).replace('\\', '/')
                img_tag = f'<{Tag.IMAGE} src="{out_path}" />'
                copy(img_tag)
                print(f"Copied tag to clipboard: {repr(img_tag)}")
                if mode == 'auto':
                    append_to_current_question(img_tag)
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


def check_tag_operations(hotkey_pressed, mode):
    for hk, tag in TAG_MAPPING.items():
        if is_pressed(hk):
            hotkey_pressed = True
            # print(f"Inserting `{tag}` tag.")
            pad_nl = tag not in NO_PADDING
            text = modify_selected_text(surround_with, tag=tag, pad_nl=pad_nl)
            if text and mode == 'auto' and tag not in NO_AUTO_SAVE:
                append_to_current_question(text)
            break

    if is_pressed(HK_REMOVE_TAG):
        hotkey_pressed = True
        print('Removed tag.')
        modify_selected_text(remove_tag)

    return hotkey_pressed


def check_ocr_operations(hotkey_pressed, mode):
    if is_pressed(HK_CAPTURE_OCR):
        hotkey_pressed = True
        print('Capturing image for text extraction.')
        img = capture_image(grayscale=True)
        if img is None:
            print('Canceled image capture.')
            return hotkey_pressed

        text = get_text_in_image(img)
        copy(text)
        print(f"Copied text to clipboard: {repr(text)}")
        if mode == 'auto':
            append_to_current_question(text)

    return hotkey_pressed


def save_image(image):
    prefix = get_output_file_path_prefix()
    images = glob.glob(f"{IMAGES_DIR_NAME}/*_{menu.question_type}_{menu.current_question}_*.png")

    if not images:
        index = 0
    else:
        images.sort()
        last_image = images[-1]
        match = re.match(r'.*(\d+)\.png$', last_image)
        index = int(match.group(1)) + 1

    out_path = str(Path(IMAGES_DIR_NAME, f"{prefix}_{menu.question_type}_{menu.current_question}_{index}.png"))
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
        html_path = str(out_path).replace('xml', 'html')
        html = xml_to_html(xml, include_reload_script=False)
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
            return opt.lower() == 'y'


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


@static_vars(subject='', year='', current_question=1, question_type='d', mode='')
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
            base_path = Path('parsed', f"{subject} {year}")
            base_path.joinpath(Path(IMAGES_DIR_NAME)).mkdir(parents=True, exist_ok=True)
            os.chdir(str(base_path))
        else:
            qt = 'discursive' if menu.question_type == 'd' else 'multiple choice'
            EXIT = 'Exit.'
            AUTO_MODE = 'Activate auto mode.'
            MANUAL_MODE = 'Activate manual mode.'
            CHANGE_QUESTION_NUMBER = f"Change current question number (current is {menu.current_question})."
            CHANGE_QUESTION_TYPE = f"Change current question type (current is {qt})."
            CHANGE_SUBJECT_YEAR = 'Change subject/year.'
            SAVE_CURRENT_QUESTION = 'Save current question.'
            OPEN_HTML_PREVIEW = 'Open HTML preview.'
            options = (
                EXIT,
                AUTO_MODE,
                MANUAL_MODE,
                CHANGE_QUESTION_NUMBER,
                CHANGE_QUESTION_TYPE,
                CHANGE_SUBJECT_YEAR,
                SAVE_CURRENT_QUESTION,
                OPEN_HTML_PREVIEW,
            )
            print('\n-----------\nChoose an option:')
            for i, txt in enumerate(options):
                print(f"-{i}: {txt}")
            while True:
                inp = input('>> ')
                try:
                    opt = int(inp)
                    if opt < 0:
                        raise ValueError
                    opt = options[opt]
                    break
                except (ValueError, IndexError):
                    print('Invalid option')

            if opt == EXIT:
                exit()

            if opt in (MANUAL_MODE, AUTO_MODE):
                open_current_question_file()
                menu.mode = 'manual' if opt == MANUAL_MODE else 'auto'
                return

            if opt == CHANGE_QUESTION_NUMBER:
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

            if opt == CHANGE_QUESTION_TYPE:
                print('Is the question multiple choice or discursive? (M/d)')
                while True:
                    inp = input('>> ')
                    if not inp or inp.lower() in ('m', 'd'):
                        menu.question_type = inp.lower() or 'm'
                        break

            if opt == CHANGE_SUBJECT_YEAR:
                os.chdir('..')
                menu.subject, menu.year, menu.active_dir = '', '', ''
                menu.images_dir, menu.current_question, menu.question_type, menu.mode = '', 1, 'd', ''
                continue

            if opt == SAVE_CURRENT_QUESTION:
                try:
                    save_question()
                except OSError as e:
                    print("Failed to save the question. Have you already saved it?")
                else:
                    menu.current_question += 1
                finally:
                    continue

            if opt == OPEN_HTML_PREVIEW:
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
            qt = (
                'Multiple Choice' 
                if menu.question_type == 'm' 
                else 'Discursive'
            )
            xml = (
                f"<h1>{qt} Question Number: {menu.current_question}</h1><br/>\n"
                f"{xml}\n"
            )
            try:
                html = xml_to_html(xml, file_path=CURRENT_QUESTION_HTML)
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

    toggle_mode = join_hotkeys(HK_TOGGLE_MODE).upper()
    back_to_menu = join_hotkeys(HK_BACK_TO_MENU).upper()

    while True:
        _ = cv2.waitKey(1) & 0xFF
        now = time()
        if not keyboard_grab_activated:
            menu()
            print(f"Enabling {menu.mode} mode, use {toggle_mode} to toggle between manual and auto mode.")
            print(f"Use {back_to_menu} to go back to menu.")
            keyboard_grab_activated = True

        hotkey_pressed = False
        if now - last_action > ACTION_DELAY:
            if is_pressed(HK_TOGGLE_MODE):
                hotkey_pressed = True
                menu.mode = 'auto' if menu.mode == 'manual' else 'manual'
                print(f"Enabled {menu.mode} mode. Press {back_to_menu} to go back to menu.")

            if is_pressed(HK_BACK_TO_MENU):
                hotkey_pressed = True
                keyboard_grab_activated = False

            if keyboard_grab_activated:
                image_open, hotkey_pressed = check_image_operations(image_open, hotkey_pressed, menu.mode)
                hotkey_pressed = check_tag_operations(hotkey_pressed, menu.mode)
                hotkey_pressed = check_ocr_operations(hotkey_pressed, menu.mode)
            if hotkey_pressed:
                last_action = time()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Enade parser.')
    parser.add_argument('--tesseract-path', default='', type=str, help='path to the tesseract binary')
    args = parser.parse_args()

    set_tesseract_path(args.tesseract_path)

    main()

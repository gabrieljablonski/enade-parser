import numpy as np
from pyautogui import screenshot
import keyboard
import cv2
import clipboard
import time
import simplejson as json
from shutil import move
import os
from html import escape
from unidecode import unidecode
import re


def dump_dict(dic):
    return json.dumps(dic, indent=4).encode('utf-8').decode('unicode_escape')


index = {}
index_path = 'index.json'
new_index = True


if os.path.exists(index_path):
    with open(index_path, 'r') as fp:
        data = fp.read()
        if data:
            new_index = False
            index = json.loads(data)
            print(f"Next is either {index['questions']['choice_count']+1} multiple choice or "
                  f"{index['questions']['discursive_count']+1} discursive")
if new_index:
    index = {
        'subject': input('Subject:\n>>'),
        'year': input('Year:\n>>'),
        'questions': {
            'discursive_count': 0,
            'choice_count': 0,
            'choice_answer_values': []
        },
        'image_count': 0
    }
    with open(index_path, 'w+') as fp:
        fp.write(dump_dict(index))

file_prefix = unidecode(f"{index['subject'].replace(' ', '_')}_{index['year']}")

for sub in ('images', 'multiple_choice', 'discursive'):
    if not os.path.exists(sub):
        os.mkdir(sub)

pic_roi = 50, 100, 850, 900
if input('Select region for screen capture? (y/N)\n>>') == 'y':
    try:
        pic_roi = cv2.selectROI('select', cv2.cvtColor(np.array(screenshot()), cv2.COLOR_RGB2BGR))
        print(f"Selected region: {pic_roi}")
        cv2.destroyWindow('select')
    except:
        pass
else:
    print(f"Using default region {pic_roi}")

image_count = index['image_count']
image_prefix = f"{file_prefix}_img"
choice_prefix = f"{file_prefix}_choice"
discursive_prefix = f"{file_prefix}_discursive"
is_discursive = True

question_path = 'question.html'

with open(question_path, 'w'):
    pass

clipboard.copy('')
last_content = ''
tag_is_open = False
mode = 'txt'
submode = 'normal'
show_mode = True

last_action = time.time()  # delay to avoid unintentional repeated actions
keyboard_grab_activated = False

# question_path = 'question.html'
#
# answers = None
# with open(question_path, 'w') as fp:
#     pass


def change_mode(new_mode):
    global mode, last_action, show_mode
    last_action = time.time()
    mode = new_mode
    show_mode = True


def change_submode(new_mode):
    global submode, last_action, show_mode
    last_action = time.time()
    submode = new_mode
    show_mode = True


def write_to_question(content):
    try:
        with open(question_path, 'a+') as f:
            f.write(content)
    except UnicodeEncodeError as e:
        print(f"{e}\n\n")
        print('Error encoding character. Try using inline picture instead.')
    else:
        print(f"Written content:\n"
              f"{content}")


def open_tag(tag, cls):  # for adding inline content
    write_to_question(f"<{tag} class='{cls}'>")


def close_tag(tag):
    write_to_question(f"</{tag}>\n")


def write_content(content, esc=True):
    if esc:
        content = escape(content)
    write_to_question(content)


def write_header(cls, content):
    to_write = f"<h1 class='{cls}'>{escape(content)}</h1>\n"
    write_to_question(to_write)


def write_paragraph(cls, content):
    to_write = f"<p class='{cls}'>{escape(content)}</p>\n"
    to_write = to_write.replace('◦', '°')
    write_to_question(to_write)


def write_picture(in_line=False):
    image_path = os.path.join('images', f"{image_prefix}_{image_count - 1}.png")
    to_write = f"<img alt='{index['subject']} Prova {index['year']} - Figura {image_count}' " \
               f"src='{image_path}'>"
    if not in_line:
        to_write = f"{to_write}\n"

    write_to_question(to_write)


def write_answers(answers):
    year = int(index['year'])
    pattern = ''
    if year < 2008:
        # (\w) Answer body
        pattern = r'\(A\) ([\s\S]*)\(B\) ([\s\S]*)\(C\) ([\s\S]*)\(D\) ([\s\S]*)\(E\) ([\s\S]*)'
    elif year == 2009:
        # A) Answer body
        pattern = r'A\) ([\s\S]*)B\) ([\s\S]*)C\) ([\s\S]*)D\) ([\s\S]*)E\) ([\s\S]*)'
    elif year == 2008 or year > 2009:
        # A Answer body
        pattern = r'A ([\s\S]*)B ([\s\S]*)C ([\s\S]*)D ([\s\S]*)E ([\s\S]*)'

    answers = re.findall(pattern, answers)

    to_write = "<ol id='answers' type='A'>\n"

    for answer in answers[0]:
        answer = answer.replace('\r\n', ' ').strip()
        to_write = f"{to_write}\t<li>{answer}</li>\n"
    to_write = f"{to_write}</ol>\n"

    write_to_question(to_write)


def write_question():
    global last_action, is_discursive
    last_action = time.time()

    # rename `question.html`
    if is_discursive:
        q_number = index['questions']['discursive_count']
        new_question_path = os.path.join('discursive', f"{discursive_prefix}_{q_number}.html")
        index['questions']['discursive_count'] += 1
        print(f"Saving discursive question number {q_number + 1}.")
    else:
        q_number = index['questions']['choice_count']
        new_question_path = os.path.join('multiple_choice', f"{choice_prefix}_{q_number}.html")
        index['questions']['choice_count'] += 1
        print(f"Saved multiple choice question number {q_number + 1}.")

    print(f"Next is either {index['questions']['choice_count'] + 1} multiple choice or "
          f"{index['questions']['discursive_count'] + 1} discursive")

    index['image_count'] = image_count
    with open(index_path, 'w') as f:
        f.write(dump_dict(index))

    is_discursive = True

    move(question_path, new_question_path)

    with open(question_path, 'w'):
        pass


def crop(img, roi):
    return img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]


def capture_picture():
    global image_count
    image = crop(cv2.cvtColor(np.array(screenshot()), cv2.COLOR_RGB2BGR), pic_roi)

    roi = cv2.selectROI('select', image)
    image = crop(image, roi)

    gray = cv2.bitwise_not(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    roi = cv2.boundingRect(gray)

    final = crop(image, roi)
    img_path = os.path.join('images', f"{image_prefix}_{image_count}.png")
    cv2.imwrite(img_path, final)
    print(f"Created image: {img_path}")
    image_count += 1

    cv2.destroyAllWindows()


def write_index():
    if not os.path.exists(file_prefix):
        os.mkdir(file_prefix)

    dst_path = os.path.join(file_prefix, f"{file_prefix}_{index_path}")
    move(index_path, dst_path)

    for sub in ('images', 'multiple_choice', 'discursive'):
        move(sub, file_prefix)

    print(f"Finished parsing {file_prefix}")


while True:
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        cv2.destroyAllWindows()

    if time.time() - last_action > 0.25:
        # pause keyboard grab
        if keyboard.is_pressed('ctrl+shift'):
            last_action = time.time()
            keyboard_grab_activated = not keyboard_grab_activated
            show_mode = True

        if not keyboard_grab_activated:
            continue

        if keyboard.is_pressed('ctrl+z'):
            last_action = time.time()

            for i in range(index['image_count'], image_count):
                path = os.path.join('images', f"{image_prefix}_{i}.png")
                os.remove(path)
            image_count = index['image_count']
            is_discursive = True
            with open(question_path, 'w') as fp:
                pass
            print('reset')

            change_mode('txt')

        # capture image
        if keyboard.is_pressed('ctrl+space'):
            if mode == 'answers_img':
                to_write = "<ol id='answers' type='A'>\n"

                try:
                    for i in range(5):  # TODO: make generic in case of # of answers diff from 5
                        print(f"Select picture for answer {chr(65+i)}...")
                        capture_picture()

                        image_path = os.path.join('images', f"{image_prefix}_{image_count-1}.png")
                        to_write = f"{to_write}" \
                                   f"\t<li>" \
                                   f"<img alt='{index['subject']} Prova {index['year']} - Figura {image_count}'" \
                                   f"src='{image_path}'>" \
                                   f"</li>\n"
                        time.sleep(0.3)
                except:
                    cv2.destroyAllWindows()
                    print('Answer pictures capture cancelled')
                else:
                    to_write = f"{to_write}</ol>"
                    write_content(to_write, esc=False)
            else:
                in_line = mode == 'text_il'
                try:
                    print('Select picture...')
                    capture_picture()
                except:
                    cv2.destroyAllWindows()
                    print('Picture capture cancelled')
                else:
                    if in_line and not tag_is_open:
                        open_tag('p', 'txt')
                        tag_is_open = True
                    write_picture(in_line)
            if mode != 'text_il':
                change_mode('txt')
            else:
                show_mode = True

        old_mode = mode
        if keyboard.is_pressed('w'):
            change_mode('header_left')

        if keyboard.is_pressed('e'):
            change_mode('header_center')

        if keyboard.is_pressed('q'):
            change_mode('txt')

        if mode == 'text_il':
            if keyboard.is_pressed('n'):
                change_submode('normal')
            if keyboard.is_pressed('i'):
                change_submode('italics')
            if keyboard.is_pressed('b'):
                change_submode('bold')

        if keyboard.is_pressed('ctrl+q'):
            if mode == 'text_il':
                change_mode('txt')
            else:
                change_mode('text_il')  # inline content
                submode = 'normal'

        if keyboard.is_pressed('d'):
            change_mode('source')

        if keyboard.is_pressed('a'):
            change_mode('answers')

        if keyboard.is_pressed('ctrl+a'):
            # TODO: check if txt+image answers are a thing
            change_mode('answers_img')  # answers are images

        if old_mode == 'text_il' and mode != 'text_il':
            if tag_is_open:
                close_tag('p')

        if keyboard.is_pressed('ctrl+e'):
            write_question()

        if keyboard.is_pressed('ctrl+f'):
            write_index()
            exit()

    clipboard_content = clipboard.paste()
    if clipboard_content != last_content:
        last_content = clipboard_content

        if mode != 'text_il':
            clipboard_content = clipboard_content.strip()

        if mode != 'answers':
            clipboard_content = clipboard_content.replace('\n', ' ')
            clipboard_content = clipboard_content.replace('\r', '')

        if mode == 'header_left':
            write_header('left', clipboard_content)

        elif mode == 'header_center':
            write_header('centered', clipboard_content)

        elif mode == 'txt':
            write_paragraph('txt', clipboard_content)

        elif mode == 'text_il':
            if not tag_is_open:
                open_tag('p', 'txt')
                tag_is_open = True

            c = clipboard_content
            if submode == 'italics':
                c = f"<i>{c}</i>"
            if submode == 'bold':
                c = f"<b>{c}</b>"
            write_content(c, esc=False)

        elif mode == 'source':
            write_paragraph('source', clipboard_content)

        elif mode == 'answers':
            is_discursive = False
            write_answers(clipboard_content)

        if mode == 'text_il':
            submode = 'normal'
        else:
            mode = 'txt'
        show_mode = True

    if show_mode:
        if not keyboard_grab_activated:
            print(f">>Keyboard grab deactivated. (CTRL+SHIFT)")
        else:
            print(f">>Next: {mode}")
            if mode == 'text_il':
                print(F"Submode: {submode}")
        show_mode = False

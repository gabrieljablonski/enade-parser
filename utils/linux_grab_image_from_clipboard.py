import os
from random import randint
from subprocess import check_output
from PIL import Image


out = check_output('scrot -v'.split())
if 'not found' in str(out):
    raise Exception(out)
else:
    print(f"scrot installation found: {str(out)}")


def grab_clipboard():
    img_name = f"scrot_image_{randint(0, 99)}.png"
    cmd = f"scrot -u {img_name}"  # -u flag captures current window
    output = check_output(cmd.split())
    if output:
        raise Exception('Failed to grab image from clipboard.\n', output)

    try:
        img = Image.open(img_name)
    except IOError as e:
        raise e

    try:
        os.remove(img_name)
    except (IsADirectoryError, FileNotFoundError) as e:
        raise e

    return img

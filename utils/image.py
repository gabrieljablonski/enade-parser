import cv2
import numpy as np
from platform import system

if system() == 'Linux':
    from .linux_grab_image_from_clipboard import grab_clipboard
else:
    from PIL import ImageGrab
    from hotkeys import send_hotkey, Key
    _grab_clipboard = ImageGrab.grabclipboard
    del ImageGrab

    def grab_clipboard():
        send_hotkey(Key.ALT, Key.PRNT_SCRN, wait=.5)
        return _grab_clipboard()


WIN_NAME_CROP = 'Select region to crop'
WIN_NAME_CAPTURE = 'Image captured'


class ImageGrabException(Exception):
    pass


def grab_image_from_clipboard():
    return np.array(grab_clipboard())


def manual_crop(img, roi):
    return img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]


def auto_crop(img, grayscale=False):
    """
    crops image based on bounding rectangle
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = cv2.bitwise_not(gray)
    roi = cv2.boundingRect(mask)
    if grayscale:
        return manual_crop(gray, roi)
    return manual_crop(img, roi)


def best_crop(img, roi, grayscale=False):
    return auto_crop(manual_crop(img, roi), grayscale=grayscale)


def capture_picture(grayscale=False):
    try:
        img_grab = grab_image_from_clipboard()
    except (IsADirectoryError, FileNotFoundError, IOError) as e:
        raise ImageGrabException('Failed to grab image.\n', e)

    image = cv2.cvtColor(img_grab, cv2.COLOR_RGB2BGR)
    roi = cv2.selectROI(WIN_NAME_CROP, image)
    cv2.destroyWindow(WIN_NAME_CROP)
    if roi[2:] == (0, 0):  # (0, 0, 0, 0) if no ROI is selected; (x, y, 0, 0) if clicked but no area was selected
        return None
    return best_crop(image, roi, grayscale)

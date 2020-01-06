import cv2
import numpy as np
from platform import system

if system() == 'Linux':
    ...
else:
    from PIL import ImageGrab
    from hotkeys import send_hotkey, Key
    _grab_clipboard = ImageGrab.grabclipboard
    del ImageGrab

    def grab_clipboard():
        send_hotkey(Key.ALT, Key.PRNT_SCRN)
        return _grab_clipboard()


class ImageGrabException(Exception):
    pass


def grab_image_from_clipboard():
    return np.array(grab_clipboard())


def manual_crop(img, roi):
    return img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]


def auto_crop(img):
    """
    crops image based on bounding rectangle
    """
    gray = cv2.bitwise_not(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    roi = cv2.boundingRect(gray)
    return manual_crop(img, roi)


def best_crop(img, roi):
    return auto_crop(manual_crop(img, roi))


def capture_picture():
    try:
        img_grab = grab_image_from_clipboard()
    except (IsADirectoryError, FileNotFoundError, IOError) as e:
        raise ImageGrabException('Failed to grab image.\n', e)

    image = cv2.cvtColor(img_grab, cv2.COLOR_RGB2BGR)
    roi = cv2.selectROI('Select region to crop', image)
    return best_crop(image, roi)

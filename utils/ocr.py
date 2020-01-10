import pytesseract


DEFAULT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# REMINDER TO DOWNLOAD `por.traineddata`
def set_tesseract_path(path):
    pytesseract.pytesseract.tesseract_cmd = path or DEFAULT_PATH


def get_text_in_image(img, lang='por'):
    return pytesseract.image_to_string(img, lang=lang)

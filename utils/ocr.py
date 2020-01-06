import pytesseract

# REMINDER TO DOWNLOAD `por.traineddata`
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_text_in_image(img, lang='por'):
    return pytesseract.image_to_string(img, lang=lang)

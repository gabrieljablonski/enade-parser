## Virtual Environment

```
python -m venv venv
.\venv\Scripts\activate

python -m pip install -r requirements.txt
```

## Tesseract

- https://github.com/UB-Mannheim/tesseract/wiki
- https://github.com/tesseract-ocr/tessdata_best/blob/master/por.traineddata

Move `por.traineddata` to `<TESSERACT_PATH>/tessdata`

## VSCode

Set as default program for XML files.

- [Portuguese - Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker-portuguese-brazilian)
- [XML Tools](https://marketplace.visualstudio.com/items?itemName=DotJoshJohnson.xml)


Enable spell checking on XML files.

## Recommended Options

- Enable autosave in VSCode
- Set default program for HTML files as the same for PDF files

## Running
```
python .\enade_parser.py --tesseract-path "<TESSERACT_PATH>"
```

`TESSERACT_PATH` defaults to `C:\Program Files\Tesseract-OCR\tesseract.exe`.

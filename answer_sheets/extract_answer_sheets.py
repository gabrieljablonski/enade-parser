import glob
from pathlib import Path
from json import dumps

from pdf2txt import pdf_to_text

BASE_PATH = Path(r'D:\GitReps\enade-parser\pdfs_by_year')
ANSWER_SHEET_PATH_PATTERN = str(BASE_PATH.joinpath('*').joinpath('gabaritos').joinpath('*2018*.pdf'))

answer_sheet_files = list(glob.glob(ANSWER_SHEET_PATH_PATTERN))

answer_sheet = {}

for i, f in enumerate(answer_sheet_files):
    print(f"--{i+1}/{len(answer_sheet_files)}--")
    text = pdf_to_text(f)

    subject, year = Path(f).parts[-1].strip('.pdf').split('_')[:2]
    if subject not in answer_sheet:
        answer_sheet[subject] = {}
    
    answers = text[text.index(b'35\n\n')+4:-2].replace(b'ANULADA\n', b'')
    ans = []

    for option in answers.split(b'\n'):
        ans.append(option.decode() if option else None)
        if len(ans) == 35:
            break
    answer_sheet[subject][year] = ans

with open('answer_sheet.json', 'w', encoding='utf8') as out:
    out.write(dumps(answer_sheet, ensure_ascii=False, indent=4) + '\n')

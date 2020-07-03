import glob
from pathlib import Path
from json import dumps

from pdf2txt import pdf_to_text

BASE_PATH = Path(r'D:\git\enade-parser\pdfs_by_year')
ANSWER_SHEET_PATH_PATTERN = str(BASE_PATH.joinpath('2019').joinpath('gabaritos').joinpath('*.pdf'))

answer_sheet_files = list(glob.glob(ANSWER_SHEET_PATH_PATTERN))

answer_sheet = {}

for i, f in enumerate(answer_sheet_files):
    print(f"--{i+1}/{len(answer_sheet_files)}--")
    text = pdf_to_text(f).decode('utf8')

    subject, year = Path(f).parts[-1].strip('.pdf').split('_')[:2]
    if subject not in answer_sheet:
        answer_sheet[subject] = {}
    
    answers = text[text.index('GABARITO\n')+len('GABARITO'):-3].replace('\nANULADA\n', '')
    ans = []

    for option in answers.split('\n')[1:]:
        ans.append(option if option else None)
        if len(ans) == 35:
            break
    answer_sheet[subject][year] = ans

with open('answer_sheet.json', 'w', encoding='utf8') as out:
    out.write(dumps(answer_sheet, ensure_ascii=False, indent=4))

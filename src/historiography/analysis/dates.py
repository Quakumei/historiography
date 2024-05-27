"""
    Process pdfs to extract date periods
"""

from pathlib import Path
import time
import re


from pdfminer.high_level import extract_text
import pandas as pd
from pandarallel import pandarallel
pandarallel.initialize(progress_bar=True, nb_workers=2)

from tqdm import tqdm
tqdm.pandas()

from ..logger import logger

PERIODS = [
    {
        "start": 1300,
        "end": 1350,
        "desc": "Период формирования Ногайской Орды, выходящей на историческую арену как отдельный субъект."
    },
    {
        "start": 1350,
        "end": 1380,
        "desc": "Время первого упоминания Ногайской Орды в исторических источниках. Орда активно участвует в политической жизни Золотой Орды и соперничает за власть."
    },
    {
        "start": 1390,
        "end": 1400,
        "desc": "Период при Едигее, после его борьбы с Тохтамышем за власть в Золотой Орде, а также больших военных кампаний Едигея против славянских земель.",
    },
    {
        "start": 1440,
        "end": 1635,
        "desc": "Вероятное начало окончательного формирования Ногайской Орды как самостоятельного государства.",
    },
    {
        "start": 1555,
        "end": 1560,
        "desc": "Период упадка Ногайской Орды из-за увеличения влияния Русского царства и Крымского ханства.",
    },
    {
        "start": 1634,
        "end": 1635,
        "desc": "Распад Ногайской Орды на несколько малых формирований, многие из которых впоследствии были постепенно сассимилированы или подчинены соседями.",
    }
]

def get_article_text(pdf_link: str) -> str:
    import requests
    import tempfile
    with tempfile.TemporaryDirectory() as tempdirname:
        file_title = pdf_link.split('/')[-2]
        filepath = f'{tempdirname}/{file_title}.pdf'
        retry_count = 0
        response = requests.get(pdf_link)
        while response.status_code != 200:
            response = requests.get(pdf_link)
            if retry_count < 3 and response.status_code != 200:
                logger.warning(f"[{retry_count=}] Status code is non-200 (={response.status_code}) for {pdf_link=}")
                retry_count += 1  
                time.sleep(5)
                continue
            else:
                return f"0 Not successful ({response.status_code=}): {response.content=}"
                
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        return extract_text(filepath)

def load_historiography_csv_with_texts(path, head: bool = True) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise ValueError(f"{path=} does not exist.")
    
    df = pd.read_csv(p)
    if head:
        df = df.head(10)
    if "full_text" not in df.columns:
        df['full_text'] = df['pdf_link'].parallel_apply(get_article_text)
        df.to_csv(str(p).replace(p.stem, f'{p.stem}_full'))
    
    return df
    

def dates_to_periods(dates_list) -> list[dict]:
    relevant_periods = []
    for d in dates_list:
        for p in PERIODS:
            if p['start'] >= d <= p['end']:  
                relevant_periods.append((p['start'], p['end']))
    return sorted(list(set(relevant_periods)), key=lambda x: x[0])

def extract_dates(text):
    regex = r'1\d{3}'
    return list(map(int, re.findall(regex, text)))

if __name__ == '__main__':
    HISTORIOGRAPHY_CSV = 'data/historiography.csv'
    full_texts_df = load_historiography_csv_with_texts(HISTORIOGRAPHY_CSV, head=False)
    full_texts_df['periods'] = full_texts_df['full_text'].parallel_apply(extract_dates).parallel_apply(dates_to_periods)
    print(full_texts_df[['title', 'periods']])

    

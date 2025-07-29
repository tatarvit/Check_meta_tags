import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def analyze_headings_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        return [{
            'URL': url,
            'Title': 'Ошибка загрузки',
            'Tag': '',
            'Level': '',
            'Text': '',
            'Warning': str(e)
        }]
    
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title else 'Нет <title>'

    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    prev_level = 0
    h1_count = 0
    results = []

    for h in headings:
        tag = h.name
        level = int(tag[1])
        text = h.get_text(strip=True)

        if tag == 'h1':
            h1_count += 1

        # Проверка последовательности заголовков
        if prev_level and level > prev_level + 1:
            warning = f'Скачок: H{prev_level} → {tag}'
        else:
            warning = ''

        results.append({
            'URL': url,
            'Title': title,
            'Tag': tag.upper(),
            'Level': level,
            'Text': text,
            'Warning': warning
        })

        prev_level = level

    if h1_count > 1:
        results.append({
            'URL': url,
            'Title': title,
            'Tag': 'H1',
            'Level': 1,
            'Text': '[дополнительно]',
            'Warning': f'Несколько H1: {h1_count}'
        })

    return results


def analyze_from_csv(file_path, url_column='URL'):
    df = pd.read_csv(file_path)
    if url_column not in df.columns:
        raise ValueError(f"Колонка '{url_column}' не найдена в файле")

    all_results = []
    for url in tqdm(df[url_column].dropna(), desc=" Анализируем страницы"):
        results = analyze_headings_from_url(url)
        all_results.extend(results)

    return pd.DataFrame(all_results)

result_df = analyze_from_csv('files/meta_tags_dev.csv', url_column='URL')
result_df.to_excel('headings_report.xlsx', index=False)
print("Готово! Отчет сохранен в headings_report.xlsx")


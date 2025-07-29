import pandas as pd
import requests
from bs4 import BeautifulSoup

# Upload CSV with expected data
df = pd.read_csv('files/meta_tags_dev.csv')  # Заменить на имя твоего CSV-файла

results = []

for index, row in df.iterrows():
    url = row['URL']
    expected_title = str(row['Title']).strip()
    expected_desc = str(row['Description']).strip()
    expected_h1 = str(row['H1']).strip()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get up-to-date data
        actual_title = soup.title.string.strip() if soup.title else 'No title'
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        actual_desc = meta_desc_tag['content'].strip() if meta_desc_tag else 'No description'
        actual_h1_tag = soup.find('h1')
        actual_h1 = actual_h1_tag.get_text(strip=True) if actual_h1_tag else 'No H1'

        # Matching
        title_match = actual_title == expected_title
        desc_match = actual_desc == expected_desc
        h1_match = actual_h1 == expected_h1

        results.append({
            'URL': url,
            'Expected Title': expected_title,
            'Actual Title': actual_title,
            'Title Match': title_match,

            'Expected Description': expected_desc,
            'Actual Description': actual_desc,
            'Description Match': desc_match,

            'Expected H1': expected_h1,
            'Actual H1': actual_h1,
            'H1 Match': h1_match,
        })

    except Exception as e:
        results.append({
            'URL': url,
            'Expected Title': expected_title,
            'Actual Title': f'ERROR: {e}',
            'Title Match': False,

            'Expected Description': expected_desc,
            'Actual Description': 'ERROR',
            'Description Match': False,

            'Expected H1': expected_h1,
            'Actual H1': 'ERROR',
            'H1 Match': False,
        })

# Save the result
result_df = pd.DataFrame(results)
result_df.to_excel('meta_comparison_report.xlsx', index=False)

print("Проверка завершена. Отчёт сохранён в 'meta_comparison_report.xlsx'")

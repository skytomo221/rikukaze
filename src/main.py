import re
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

base_url = 'something'
date_format = '%Y-%m-%d'
not_found_message = '404 Not Found'
output_dir = '/workspace/data'
begin = datetime(2021, 2, 18)
end = datetime(2021, 9, 20)
sleeptime = 1


def datatime_range(begin: datetime, end: datetime) -> datetime:
    dt = begin
    while dt < end:
        yield dt
        dt = dt + timedelta(days=1)


def markdown(content) -> str:
    if type(content) is str:
        return content
    else:
        if content.name == 'h1':
            return f'\n# {content.get_text()}\n'
        elif content.name == 'h2':
            return f'\n## {content.get_text()}\n'
        elif content.name == 'p':
            return content.get_text()
        else:
            return ''


def not_found(soup: BeautifulSoup) -> bool:
    return soup.body.h1.string == not_found_message


def req_and_save_site(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, 'html.parser')

    if not_found(soup):
        print(f'{url} -> 404 Not Found')
        return
    else:
        print(f'{url} -> 200 OK')

    article = soup.body.main.article
    title = article.header.h1.string
    content = article.find('div', class_='content')

    article_text = '\n'.join(list(map(markdown, content.contents))).strip()
    article_text = re.sub(r'\n\n+', '\n\n', article_text)
    article_text = article_text + '\n'

    with open(f'{output_dir}/{title}.md', 'w') as f:
        f.write(article_text)


if __name__ == "__main__":
    dtr = datatime_range(begin, end)
    for dt in dtr:
        full_url = f'{base_url}{dt.strftime(date_format)}'
        req_and_save_site(full_url)
        time.sleep(sleeptime)

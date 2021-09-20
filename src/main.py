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
    length = (end - begin).days + 1
    for n in range(length):
        yield begin + timedelta(n)


class Rikukaze:

    def __init__(self, url):
        self.url = url

    def get(self):
        response = requests.get(self.url)
        response.encoding = response.apparent_encoding
        self.soup = BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def found(soup: BeautifulSoup) -> bool:
        return soup.body.h1.string != not_found_message

    def analyze(self):
        self.article = self.soup.body.main.article
        self.title = self.article.header.h1.string
        self.content = self.article.find('div', class_='content')

    @staticmethod
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

    def to_markdown(self) -> str:
        text = '\n'.join(map(self.markdown, self.content.contents)).strip()
        text = f'# {self.title}\n\n{text}\n'
        text = re.sub(r'\n\n+', '\n\n', text)
        return text

    def save(self):
        self.get()

        if not self.found(self.soup):
            print(f'{self.url} -> 404 Not Found')
            return
        else:
            print(f'{self.url} -> 200 OK')

        self.analyze()
        text = self.to_markdown()

        with open(f'{output_dir}/{self.title}.md', 'w') as f:
            f.write(text)


if __name__ == "__main__":
    for dt in datatime_range(begin, end):
        full_url = f'{base_url}{dt.strftime(date_format)}'
        rikukaze = Rikukaze(full_url)
        rikukaze.save()
        time.sleep(sleeptime)

import datetime
import json
import re
from collections import defaultdict
import requests
from bs4 import BeautifulSoup


def scrape_test(season):
    url = f'https://www.basketball-reference.com/leagues/NBA_{season}_transactions.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    transaction_days = soup.select('ul.page_index > li')
    found_matches = {}

    def get_element_text(element):
        if hasattr(element, 'href'):
            if 'data-attr-to' in element.attrs:
                res = (element['data-attr-to'], ), 'team'
            elif 'data-attr-from' in element.attrs:
                res = (element['data-attr-from'], ), 'team'
            elif 'players' in element['href']:
                res = re.findall(r'^/players/[a-z]/(.+?)\.html$', element['href']), 'player'
            elif 'executives' in element['href']:
                res = re.findall(r'^/executives/(.+?)\.html$', element['href']), 'executive'
            else:
                res = re.findall(r'^/coaches/(.+?)\.html$', element['href']), 'coach'
            if len(res[0]):
                found_matches[element.get_text()] = res[0][0], res[1]
                return res[0][0], res[1], element.get_text()
            return *found_matches[element.get_text()], element.get_text()
        return None, None, str(element)
    last_date = None
    to_save = defaultdict(list)
    for day in transaction_days:
        date = day.select('span')[0].get_text()
        if date == '?':
            date = last_date
        if '?' in date:
            date = date.replace('?', '1')
        last_date = date
        date = datetime.datetime.strptime(date, '%B %d, %Y').date().isoformat()
        day_transactions = day.select('p')
        for d in day_transactions:
            transaction_text = ''
            transaction_to_find = {}
            for c in d.contents:
                found_id, id_type, initial_text = get_element_text(c)
                if found_id:
                    transaction_text += found_id
                    transaction_to_find[found_id] = [id_type, initial_text]
                else:
                    transaction_text += initial_text
            to_save[date].append([transaction_text, transaction_to_find])
    with open(f'transactions/cache/transactions_{season}.txt', 'w') as f:
        json.dump(to_save, f)


def scrape_all():
    for season in range(1950, 2022):
        print(f'scraping {season}...')
        scrape_test(season)


if __name__ == '__main__':
    scrape_all()

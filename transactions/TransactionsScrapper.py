import datetime
import re
import unidecode
from bs4 import BeautifulSoup


class TransactionsScrapper:

    @staticmethod
    def scrap_transactions(transactions_html):
        soup = BeautifulSoup(transactions_html, 'html.parser')
        transaction_days = soup.select('ul.page_index > li')
        found_matches = {}

        def get_element_text(element):
            if hasattr(element, 'href'):
                if 'data-attr-to' in element.attrs:
                    res, res_type = (element['data-attr-to'],), 'team'
                elif 'data-attr-from' in element.attrs:
                    res, res_type = (element['data-attr-from'],), 'team'
                elif 'players' in element['href']:
                    res, res_type = re.findall(r'^/players/[a-z]/(.+?)\.html$', element['href']), 'player'
                elif 'executives' in element['href']:
                    res, res_type = re.findall(r'^/executives/(.+?)\.html$', element['href']), 'executive'
                else:
                    res, res_type = re.findall(r'^/coaches/(.+?)\.html$', element['href']), 'coach'
                if len(res):
                    text_to_add_to_ret = res[0]
                    if text_to_add_to_ret == '':
                        return None, None, None, None
                    initial_text_to_ret = element.get_text()
                    if res_type == 'player' and res[0].endswith('c'):
                        res_type = 'coach'
                        if '(' in element.get_text() and ')' in element.get_text():
                            text_to_add_to_ret += ' ' + element.get_text()[
                                                        element.get_text().index('('): element.get_text().index(
                                                            ')') + 1]
                            initial_text_to_ret = element.get_text()[:element.get_text().index('(') - 1]
                    found_matches[element.get_text()] = text_to_add_to_ret, res[0], res_type
                    return text_to_add_to_ret, res[0], res_type, initial_text_to_ret
                if element.get_text() == '':
                    return '', None, None, ''
                elif element.get_text() == 'cash':
                    return 'cash', None, None, 'cash'
                return *found_matches[element.get_text()], element.get_text()
            return str(element), None, None, str(element)

        last_date = None
        to_save = []
        for day in transaction_days:
            transaction_number = 0
            initial_date = day.select('span')[0].get_text()
            if initial_date == '?':
                date = last_date
            elif '?' in initial_date:
                date = initial_date.replace('?', '1')
            else:
                date = initial_date
            last_date = date
            date = datetime.datetime.strptime(date, '%B %d, %Y').date()
            transaction_year = date.year
            transaction_month = date.month
            transaction_day = date.day if '?' not in initial_date else -1
            day_transactions = day.select('p')
            for d in day_transactions:
                transaction_text = ''
                transaction_to_find = {}
                pass_t = False
                for c in d.contents:
                    text_to_add, found_id, id_type, initial_text = get_element_text(c)
                    if text_to_add is None:
                        pass_t = True
                        break
                    text_to_add, initial_text = unidecode.unidecode(text_to_add), unidecode.unidecode(initial_text)
                    transaction_text += text_to_add
                    if found_id:
                        transaction_to_find[found_id] = [id_type, initial_text]
                if pass_t:
                    continue
                transaction_text = transaction_text.replace(' ( was later selected)', '')
                to_save.append([transaction_year, transaction_month, transaction_day, transaction_number,
                                transaction_text, transaction_to_find])
                transaction_number += 1
        return to_save

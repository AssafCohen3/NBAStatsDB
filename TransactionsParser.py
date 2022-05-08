import json
import re
import string
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from pyparsing import *


def take_until(until, label=''):
    to_ret = Regex(fr'.+?(?={re.escape(until)})')
    if label != '':
        return to_ret(label)
    return to_ret


# 'waived': CaselessLiteral('The') + team_nt('team') + 'waived' + person_nt('player') + '.' + Opt(waive_reason),
# 'waived_unknown': CaselessLiteral('The') + team_nt('team') + 'waived' + Regex(r'.+(?=\.$)')('player_no_id') + '.' + Opt(waive_reason),

def person_or_unknown(label, next_part=None, unknown_part=None):
    if next_part:
        return MatchFirst([person_nt(label), take_until(next_part, label + '_no_id')])
    return MatchFirst([person_nt(label), unknown_part(label + '_no_id')])


number = Combine(Opt('-') + ZeroOrMore(Word(string.digits) + Suppress(',')) + Word(string.digits) + Opt('.' + Word(string.digits)))
team_nt = Word(string.ascii_uppercase)
person_nt = Word(string.ascii_lowercase + string.digits)
later_selected_part = Suppress('(') + person_or_unknown('player', next_part=' was later selected)') + Suppress('was later selected)')

sign_extension = '(Signing is extension' + MatchFirst([Literal('on'), Literal('of')]) + 'deal signed in ' + number + Opt('.') + ')'
waive_reason = MatchFirst([Suppress('(Ended two-way contract.)')])
matched_contract = '(' + team_nt('matching_team') + 'matched offer sheet signed with' + team_nt('matched_team') + ')'
rounds_phrasing = MatchFirst([Literal('round'), Literal('-rd')])
rounds = MatchFirst([Literal('1st'), Literal('2nd'), Literal('3rd'), Literal('4th'), Literal('5th'), Literal('6th'), Literal('7th'), Literal('8th')])
second_round_pick = Group(Suppress('a') + MatchFirst([number, Literal('future')])('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('draft pick') + Opt(later_selected_part))

cash_part = Combine('$' + number + Opt('MM'))
cash_considerations = Group('cash considerations' + Opt('(reportedly' + cash_part('cash_sum') + ')'))
cash_tradee = Group('cash' + Opt('(reportedly' + cash_part('cash_sum') + ')'))
team_tradees = MatchFirst([cash_considerations.set_results_name('cash_consideration', True),
                           cash_tradee.set_results_name('cash', True),
                           Literal('future considerations').set_results_name('future_consideration', True),
                           Literal('a trade exception').set_results_name('trade_exception', True),
                           second_round_pick.set_results_name('draft_pick', True),
                           person_nt.set_results_name('player', True),
                           Group(person_nt('person') + '(' + take_until(')', 'role') + ')').set_results_name('person_with_role', True),
                           Group(Regex(r'.+?(?=(?: \(.+\))??(?: to the |,| and |\.(?!.*to the)))')('person_no_id') + '(' + take_until(')', 'role') + ')').set_results_name('person_with_role', True),
                           Regex(r'.+?(?=(?: to the |,| and |\.(?!.*to the)))').set_results_name('player_no_id', True)])
team_trade_part = ZeroOrMore(team_tradees + Suppress(',')) + team_tradees + Opt(Suppress('and') + team_tradees)
pick_source = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is') + team_nt('team') + Literal('\'s pick') + Opt(', top-' + number + 'protected') + '.)')
favorable_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is least favorable pick.)'))
swap_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is a swap.)'))
unknown_pick_explanation = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Combine('pick is' + CharsNotIn(')'))('explanation') + ')')
unknown_brackets = Group(Suppress('(') + CharsNotIn(')')('content') + Suppress(')'))
trade_part = 'The' + team_nt('TeamA') + 'traded' + Group(team_trade_part)('TeamATradees') + 'to the' + \
             team_nt('TeamB') + 'for' + Group(team_trade_part)('TeamBTradees')
one_side_trade_part = CaselessLiteral('The') + team_nt('TradingTeam') + 'traded' + Group(team_trade_part)('Tradees') + 'to the' + team_nt('RecievingTeam')
trade_agreement = take_until(' agreed ', 'agreeding_team') + 'agreed ' + restOfLine('agreement')
after_trade_part = ZeroOrMore(MatchFirst([cash_part('cash_sum'),
                                          pick_source.set_results_name('picks_explains', True),
                                          unknown_pick_explanation.set_results_name('unknown_draft_brackets', True),
                                          unknown_brackets.set_results_name('unknown_brackets', True),
                                          trade_agreement,
                                          Regex('.+').set_results_name('unknown_all', True)]))

templates = {
    'sign and compensate': 'The' + team_nt('new_team') + 'signed' +
                           MatchFirst([person_nt('player'), take_until(' (', 'person_no_id') + '(' + take_until(')', 'role') + ')']) +
                           'as a' + Opt('veteran') + 'free agent and sent' + Group(team_trade_part)('TeamATradees') + 'to the' + team_nt('old_team') + 'as compensation.' + MatchFirst([Suppress(LineEnd()), restOfLine])('description'),
    'sign with length': 'The' + team_nt('team') + 'signed' + person_nt('player') + 'to a' + number('contract_length') + '-year contract.',
    'free agent sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' as a') + MatchFirst([Literal('as an unrestricted'), Literal('as a')]) + Opt('veteran') + 'free agent.' + Opt(unknown_brackets),
    'multi year contract sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to a multi-year contract') + 'to a multi-year contract.' + Opt(sign_extension) + Opt(matched_contract),
    'two way contract sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to a two-way contract') + 'to a two-way contract.',
    'exhibit 10': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to an Exhibit 10 contract') + 'to an Exhibit 10 contract.',
    '10 day contract': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to ') + 'to' + MatchFirst([Literal('a') + Opt(Literal('2nd')), Literal('the first of two')]) + '10-day contract' + Opt('s') + '.',
    '10 day contract expired': person_or_unknown('player', ' not re-signed by ') + 'not re-signed by' + team_nt('team') + '; 10-day contract expires.',
    'release from 10 day contract': CaselessLiteral('The') + team_nt('team') + 'released' + person_or_unknown('player', ' from ') + 'from' + Opt('2nd') + '10-day contract.',
    'contract extension': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', ' to a contract extension') + 'to a contract extension.',
    'rest of season sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_nt('player') + Opt('to' + MatchFirst([Literal('a 10-day contract'), Literal('two 10-day contracts')]) + ', then signed') + 'to a contract for the rest of the season.',
    're-signing': 'The' + team_nt('team') + 're-signed' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'waived': CaselessLiteral('The') + team_nt('team') + 'waived' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.$)')) + '.' + Opt(waive_reason),
#    'waived_unknown': CaselessLiteral('The') + team_nt('team') + 'waived' + Regex(r'.+(?=\.$)')('player_no_id') + '.' + Opt(waive_reason),
    'claimed from waivers': CaselessLiteral('The') + team_nt('newTeam') + 'claimed' + person_or_unknown('player', ' on waivers from the ') + 'on waivers from the' + team_nt('oldTeam') + '.',
#    'unknown claimed from waivers': CaselessLiteral('The') + team_nt('newTeam') + 'claimed' + person_nt('player') + 'on waivers from the' + team_nt('oldTeam') + '.',
    'sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'simple_trade': trade_part + '.' + after_trade_part,
    'multiple_teams_trade': 'In a' + number + '-team trade,' + ZeroOrMore(MatchFirst([Group(one_side_trade_part) + MatchFirst([Suppress('; and '), Suppress(';')]), Group(one_side_trade_part)]))('trades') + '.' + after_trade_part,
    'penalty trade': one_side_trade_part + '.' + take_until(' was penalized ', 'penalized_team') + 'was penalized for ' + restOfLine('reason'),
    'one side trade': one_side_trade_part + '.' + after_trade_part,
    'retirement': person_or_unknown('player', ' announced retirement') + 'announced retirement.' + Opt('Officially announced retiredment.') + Opt('(Announced he would retire at the end of the' + restOfLine),
    'firing': CaselessLiteral('The') + team_nt('team') + 'fired' + person_or_unknown('person', ' as ') + 'as ' + CharsNotIn('.')('role') + '.' + restOfLine,
    'appintment': CaselessLiteral('The') + team_nt('team') + 'appointed' + person_or_unknown('person', ' as ') + 'as ' + CharsNotIn('.')('role') + '.' + Opt('(Appointed on an interim basis)'),
#    'unknown appointment': CaselessLiteral('The') + team_nt('team') + 'appointed' + take_until(' as ', 'person_no_id') + 'as ' + CharsNotIn('.')('role') + '.',
    'convert contract': 'The' + team_nt('team') + 'converted' + person_or_unknown('player', ' from a two-way contract') + 'from a two-way contract to a regular contract.',
    'suspension_by_league': person_or_unknown('player', ' was suspended by the league') + 'was suspended by the league (' + number('suspension_length') + '-game suspension)',
#    'unknown_suspension_by_league': take_until(' was ', 'player_no_id') + 'was suspended by the league (' + number('suspension_length') + '-game suspension)',
    'suspension_by_team': person_or_unknown('player', ' was suspended from the') + 'was suspended from the' + team_nt('team') + Opt('(' + number('suspension_length') + '-game suspension)'),
    'assigned to': 'The' + team_nt('team') + 'assigned' + person_or_unknown('player', ' to the ') + 'to the ' + restOfLine('to'),
    'recalling': 'The' + team_nt('team') + 'recalled' + person_or_unknown('player', ' from the ') + 'from the ' + restOfLine('from'),
    'resignation': person_or_unknown('person', 'resigns as ') + 'resigns as' + take_until(' for ', 'role') + 'for' + team_nt('team') + '.',
    'hiring': CaselessLiteral('The') + team_nt('team') + 'hired' + person_or_unknown('person', ' as ') + 'as ' + CharsNotIn('.')('role') + '.' + Opt('(' + take_until(')', 'role_more') + ')'),
#    'unknown_hiring': CaselessLiteral('The') + team_nt('team') + 'hired' + take_until(' as ', 'person_no_id') + 'as ' + CharsNotIn('.')('role') + '.',
    'sold rights': CaselessLiteral('The') + team_nt('old_team') + 'sold the player rights to' + person_or_unknown('player', ' to the ') + 'to the' + team_nt('new_team') + '.' + Opt(unknown_brackets.set_results_name('explanation')),
#    'sold rights to unknown': CaselessLiteral('The') + team_nt('team') + 'sold the player rights to' + take_until(' to the ', 'player_no_id') + 'to the' + team_nt('team') + '.' + Opt(unknown_brackets.set_results_name('explanation')),
    'dispersal draft': 'The' + team_nt('new_team') + 'selected' + person_or_unknown('player', ' from the ') + 'from the' + team_nt('old_team') + 'in the dispersal draft.' + MatchFirst([Suppress(LineEnd()), restOfLine])('next'),
    'released': 'The' + team_nt('team') + 'released' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'reassignment': 'The' + team_nt('team') + 'reassigned' + Regex(r'.+?(?= [a-z0-9]+\.)')('role') + person_or_unknown('person', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'expansion draft': 'The' + team_nt('new_team') + 'drafted' + person_or_unknown('player', ' from the ') + 'from the' + team_nt('old_team') + 'in the NBA expansion draft.',
#    'unknown expansion draft': 'The' + team_nt('new_team') + 'drafted' + take_until(' from the ',  'player_no_id') + 'from the' + team_nt('old_team') + 'in the NBA expansion draft.',
    'role retire from team': MatchFirst([Literal('Player/Head Coach'), Literal('Head Coach')])('role') + person_or_unknown('person', ' retired from the ') + 'retired from the' + team_nt('team'),
    'retire from team': person_or_unknown('player', ' retired from the ') + 'retired from the' + team_nt('team'),
}


def tests():
    test_str = 'The BOS traded a 1988 2nd round draft pick (graysy01 was later selected) to the MIA. Miami agreed not to select Dennis Johnson in the expansion draft.'
    aaa = 'Miami agreed not to select Dennis Johnson in the expansion draft.'
    trade_part_aaaaaaaa = 'The' + team_nt('TeamA') + 'traded' + Group(team_trade_part)('TeamATradees') + 'to the' + \
                 team_nt('TeamB') + 'for' + Group(team_trade_part)('TeamBTradees') + '.'
    parser = Regex(r'.+?(?=(?: to the |,| and |\.(?!.*to the)))').set_results_name('player_no_id', True)
    temp = templates['simple_trade']
    res = trade_agreement.parseString(aaa)
    print(res.asDict())


def scrape_test(season):
    url = f'https://www.basketball-reference.com/leagues/NBA_{season}_transactions.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    transaction_days = soup.select('ul.page_index > li')
    found_matches = {}
    def get_element_text(element):
        if hasattr(element, 'href'):
            if 'data-attr-to' in element.attrs:
                res = (element['data-attr-to'], )
            elif 'data-attr-from' in element.attrs:
                res = (element['data-attr-from'], )
            elif 'players' in element['href']:
                res = re.findall(r'^/players/[a-z]/(.+?)\.html$', element['href'])
            elif 'executives' in element['href']:
                res = re.findall(r'^/executives/(.+?)\.html$', element['href'])
            else:
                res = re.findall(r'^/coaches/(.+?)\.html$', element['href'])
            if len(res):
                found_matches[element.get_text()] = res[0]
                return res[0]
            print(f'******************************** {element} *****************')
            return found_matches[element.get_text()]
        return str(element)

    to_save = {}
    for day in transaction_days:
        date = day.select('span')[0].get_text()
        day_transactions = day.select('p')
        day_transactions = [''.join(list(map(get_element_text, d.contents))) for d in day_transactions]
        to_save[date] = day_transactions
    with open(f'transactions_{season}.txt', 'w') as f:
        json.dump(to_save, f)


def parse_test(season):
    with open(f'transactions_{season}.txt', 'r') as f:
        transactions = json.load(f)
    parsed = defaultdict(list)
    for i, (day, day_transactions) in enumerate(transactions.items()):
        print(f'parsing {day} transactions...')
        for transaction in day_transactions:
            found = False
            for desc, template in templates.items():
                try:
                    res = template.parseString(transaction, True).asDict()
                except ParseException:
                    continue
                found = True
                print(f'parsed {transaction} as\n\t{res} with type {desc}')
                parsed[day].append([transaction, desc, res])
                break
            if not found:
                if 'traded  to the' in transaction:
                    print(f'passing transaction {transaction}. ilegal input')
                    continue
                print(f'finished {i} from {len(transactions.items())}')
                raise Exception(f'not found for {transaction} in {day}')
    for day, day_transactions in parsed.items():
        for initial, transaction_desc, transaction_dict in day_transactions:
            if transaction_desc in ['multiple_teams_trade', 'simple_trade'] and ('unknown_draft_bracketsss' in transaction_dict or 'unknown_brackets' in transaction_dict):
                print(day)
                print(initial)
                print(transaction_desc)
                print(transaction_dict)
                print('*******************************')


def scrape_all():
    for season in range(1950, 2021):
        print(f'scraping {season}...')
        scrape_test(season)


def parse_all():
    for season in range(1950, 2021):
        print(f'parsing {season}...')
        parse_test(season)


if __name__ == '__main__':
    #tests()
    #scrape_all()
    parse_all()

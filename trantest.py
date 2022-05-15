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


def take_until_new(until_nt, label='', consume=True, excluded_chars=''):
    to_ret = Combine(OneOrMore(Word(printables, exclude_chars=excluded_chars), stopOn=until_nt))
    if label != '':
        to_ret = to_ret(label)
    if consume:
        to_ret = to_ret + Suppress(until_nt)
    return to_ret


def person_or_unknown(label, next_part=None, unknown_part=None):
    if next_part:
        return MatchFirst([person_nt(label), take_until(next_part, label + '_no_id')])
    return MatchFirst([person_nt(label), unknown_part(label + '_no_id')])


possible_roles = MatchFirst([Literal('Team President'),
                             Literal('Executive Director of Basketball Operations'),
                             Literal('President of Business and Basketball Operations'),
                             Literal('Interim Executive Vice-President of Basketball Ope'),
                             Literal('Executive VP of Basketball Operations'),
                             Literal('President of Basketball Operations'),
                             Literal('Player/Head Coach'),
                             Literal('Interim Head Coach'),
                             Literal('Interim GM'),
                             Literal('General Manager'),
                             Literal('Head Coach'),
                             Literal('President'),
                             Literal('GM'),
                             Literal('vice president'),
                             Literal('coach')])
number = Combine(Opt('-') + ZeroOrMore(Word(string.digits) + Suppress(',') + FollowedBy(Word(string.digits))) + Word(string.digits) + Opt('.' + Word(string.digits)))
date_nt = Group(Word(alphas)('month') + number('day') + ',' + number('year'))
date_no_day_nt = Group(Word(alphas)('month') + number('year'))
team_nt = Word(string.ascii_uppercase)
person_nt = Word(string.ascii_lowercase + string.digits)

later_selected_part = Suppress('(') + person_or_unknown('player', ' was later selected)') + Suppress('was later selected)')
rounds_phrasing = MatchFirst([Literal('round'), Literal('-rd')])
rounds = MatchFirst([Literal('1st'), Literal('2nd'), Literal('3rd'), Literal('4th'), Literal('5th'), Literal('6th'), Literal('7th'), Literal('8th')])
draft_pick = Group(Suppress('a') + MatchFirst([number, Literal('future')])('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('draft pick') + Opt(later_selected_part))

cash_part = Combine('$' + number + Literal('M')[1, 2])
cash_considerations = Group(CaselessLiteral('cash considerations') + Opt('(reportedly' + cash_part('cash_sum') + ')'))
cash_tradee = Group(CaselessLiteral('cash') + Opt('(reportedly' + cash_part('cash_sum') + ')'))
team_tradees = MatchFirst([cash_considerations.set_results_name('cash_consideration', True),
                           cash_tradee.set_results_name('cash', True),
                           Literal('future considerations').set_results_name('future_consideration', True),
                           Literal('a trade exception').set_results_name('trade_exception', True),
                           draft_pick.set_results_name('draft_pick', True),
                           person_nt.set_results_name('player', True),
                           Group(person_nt('person') + '(' + take_until(')', 'role') + ')').set_results_name('person_with_role', True),
                           Group(Regex(r'.+?(?=(?: \(.+\))??(?: to the |,| and |\.(?!.*to the)))')('person_no_id') + '(' + possible_roles('role') + ')').set_results_name('person_with_role', True),
                           Regex(r'.+?(?=(?: to the |,| and |\.(?!.*to the)))').set_results_name('player_no_id', True)])
team_trade_part = ZeroOrMore(team_tradees + Suppress(',')) + team_tradees + Opt(Suppress('and') + team_tradees)
pick_source = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is') + team_nt('team') + Literal('\'s pick') + Opt(', top-' + number('protection') + 'protected') + '.)')
favorable_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is least favorable pick.)'))
swap_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is a swap.)'))
# unknown_pick_explanation = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Combine('pick is' + CharsNotIn(')'))('explanation') + ')')
# unknown_brackets = Group(Suppress('(') + CharsNotIn(')')('content') + Suppress(')'))

trade_part = 'The' + team_nt('TeamA') + 'traded' + Group(team_trade_part)('TeamATradees') + 'to the' + \
             team_nt('TeamB') + 'for' + Group(team_trade_part)('TeamBTradees')
one_side_trade_part = CaselessLiteral('The') + team_nt('TradingTeam') + 'traded' + Group(team_trade_part)('Tradees') + 'to the' + team_nt('RecievingTeam')
agreed_to_terms = Group(take_until(' agreed to terms with ', 'player') + 'agreed to terms with' + take_until(' in ', 'team') + 'in' + date_no_day_nt('date_no_day') + 'to complete the trade.')
agreed_to_not_select = Group(take_until_new(Opt('also') + 'agreed' + Opt('not')('not') + 'to select', 'team') +
                             take_until(' in the ', 'player') + 'in the' +
                             MatchFirst([number('year'), 'expansion']) + 'draft.')
sources_explain = Group('Some sources have' + take_until(' to ', 'player') + 'to' + take_until(' in this deal but ', 'team') + 'in this deal but he was already sold to them on' +
                        date_nt('date') + '.')
player_to_be_named_later = Group(take_until(' was sent as ', 'player') + 'was sent as' + Opt('the') + 'player to be named later on' + date_nt('date') + '.')
sent_to_complete_the_trade = Group(take_until(' was sent to ', 'player') + 'was sent to' + take_until(' to complete the trade on ', 'team') + 'to complete the trade on' + date_nt('date') + '.')
played_in_between = Group(Opt('(') + take_until(' played in the ', 'player') + 'played in the' + take_until(' in between.', 'played_in') + 'in between.' + Opt(')'))
refused_to_report = Group(take_until(' got ', 'team_got') + 'got' + take_until(' in ', 'got') + 'in' + number('year') + 'when' + take_until(' refused to report;', 'player1') +
                          'refused to report;' + take_until(' was later sold to ', 'player2') + 'was later sold to' + take_until('.', 'team_sold_to') + '.')
original_trade_cancelled = Group(take_until(' was originally traded for ', 'traded_player') + 'was originally traded for' + take_until(' on ', 'original_tradee') + 'on' + date_nt('date') + 'but the trade was cancelled.')
compensation_for_sign = Group('This exchange was arranged as compensation for' + take_until(' signing veteran free agent ', 'compensating_team') + 'signing veteran free agent' +
                              take_until(' on ', 'player') + 'on' + date_nt('date') + '.')
for_pick_in_dispersal = Group('This trade was for the' + take_until(' pick in the ', 'pick') + 'pick in the ABA dispersal draft.')
option_to_swap = Group(take_until(' had the option to swap ', 'team1') + 'had the option to swap' + take_until(' with ', 'could_swap') + 'with' +
                       take_until(' in ', 'team2') + 'in' +
                       MatchFirst([number('year'),
                                   'either' + number('year1') + 'or' + number('year2')]) +
                       MatchFirst(['but opted for' + take_until(' instead.', 'opted_for') + 'instead.',
                                   'but did not do so.',
                                   '.']))
relinquished_option_to_swap = Group(take_until(' also relinquished the ', 'team1') + 'also relinquished the option to swap' + take_until(' with ', 'can_swap') + take_until(' in ', 'team2') + 'in' + number('year') + '.')
earlier_of_two = Group(take_until(' received the ', 'team1') + 'received the' + MatchFirst([Literal('earlier'), Literal('best')]) + 'of' + take_until(' in ', 'earlier_of') +
                       'in' + number('year') + '(' + MatchFirst([Literal('both'), Literal('all')]) + 'owned by' + take_until(').', 'team2') + ').')
originally_received = Group(take_until(' originally received ', 'team') + 'originally received' + take_until(' but he was ', 'player') + 'but he was' + take_until('.', 'reason') + '.')
received_consulation = Group(take_until(' also received the consultation services ', 'team1') + 'also received the consultation services of' +
                             Combine(OneOrMore(Word(printables), stopOn=possible_roles))('team2') + possible_roles('consule_role') + take_until('.', 'person') + '.')
contigent_on_being_on_roster_and_waved = Group('The' + take_until(' was contingent upon ', 'contigent_part') + 'was contingent upon' +
                                               take_until_new(MatchFirst([Literal('making'), Literal('being on')]), 'player') +
                                               take_until_new(Literal('roster'), 'team') +
                                               MatchFirst([
                                                   'on' + date_nt('contignet_date') + 'but he was waived on' + date_nt('waved_on') + '.',
                                                   'but he did not do so.'
                                               ]))
conditioned_and_not_exercised = Group('The' + take_until(' traded to ', 'conditioned_part') + 'traded to' + take_until(' was conditional and ', 'team') + 'was conditional and was not exercised.')
# TODO check this
pick_did_not_convey = Group('Pick did not convey because' + restOfLine('reason'))
after_trade_part = ZeroOrMore(MatchFirst([cash_part('cash_sum'),
                                          pick_source.set_results_name('picks_sources', True),
                                          favorable_pick.set_results_name('favorable_picks', True),
                                          swap_pick.set_results_name('swap_picks', True),
                                          # unknown_pick_explanation.set_results_name('unknown_draft_brackets', True),
                                          # unknown_brackets.set_results_name('unknown_brackets', True),
                                          sources_explain.set_results_name('sorces_explanations', True),
                                          player_to_be_named_later.set_results_name('player_to_be_named_later', True),
                                          played_in_between.set_results_name('played_in_between', True),
                                          refused_to_report.set_results_name('refused_to_reports', True),
                                          sent_to_complete_the_trade.set_results_name('sent_to_complete_trade', True),
                                          original_trade_cancelled.set_results_name('original_trade_cancelled', True),
                                          compensation_for_sign.set_results_name('compensation_for_sign', True),
                                          for_pick_in_dispersal.set_results_name('for_pick_in_dispersal', True),
                                          option_to_swap.set_results_name('option_to_swap', True),
                                          relinquished_option_to_swap.set_results_name('relinquished_option_to_swap', True),
                                          earlier_of_two.set_results_name('earlier_of_two', True),
                                          originally_received.set_results_name('originally_received', True),
                                          received_consulation.set_results_name('received_consulation', True),
                                          contigent_on_being_on_roster_and_waved.set_results_name('contigent_on_being_on_roster_and_waved', True),
                                          conditioned_and_not_exercised.set_results_name('conditioned_and_not_exercised', True),
                                          agreed_to_not_select.set_results_name('agreed_to_not_select', True),
                                          pick_did_not_convey.set_results_name('pick_did_not_convey', True),
                                          agreed_to_terms.set_results_name('agreeds_to_terms', True)]))
# Regex('.+').set_results_name('unknown_all', True)]))

matched_contract = Group('(' + team_nt('matching_team') + 'matched offer sheet signed with' + team_nt('matched_team') + ')')
# sign_extension = '(Signing is extension' + MatchFirst([Literal('on'), Literal('of')]) + 'deal signed in ' + number + Opt('.') + ')'
sign_and_trade = Group('(Sign and trade with' + take_until(')', 'sign_and_traded_from_team') + ')')
renegotiaion_sign = Group('Signing is a renegotiation & extension of deal signed in' + number)
extension = Group('(Signing is extension' + MatchFirst([Literal('on'), Literal('of')]) + 'deal signed in' + number + Opt('and extended in' + number) + Opt('.') + ')')
sign_to_keep = Group('(Signing is an extension to keep him under contract thru' + number + '-' + number + ')')
sign_with_salary_and_length = Group('Signed ' + number('contract_length') + '-yr/' + cash_part('salary') + 'contract ' + restOfLine('sign_date'))
jumped_to = Group('(' + take_until(' to the ', 'player') + 'to the' + take_until('.)', 'jumped_to') + '.)')
returned_from = Group('(' + take_until(' returned from the ', 'player') + 'returned from the' + take_until('.)', 'returned_from') + '.)')
selected_but_not_signed = Group('(' + take_until(' was selected by ', 'player') + 'was selected by' + take_until(' in the expansion draft but did not sign', 'team') +
                                'in the expansion draft but did not sign.)')
sued = Group('(The NBA sued' + take_until(' because ', 'team') + 'because' + take_until('; ', 'reason') + '; the Supreme Court ruled' + take_until(' on ', 'court_decision') + 'on' + date_nt('date') + '.)')
for_future_services = Group('(' + take_until(' was playing in the ', 'player') + 'was playing in the' + take_until(' at the time ', 'played_in') + 'at the time and was signed for future services.)')
'The compensatory draft picks were sent to San Diego on February 3, 1981.'
compansatory_picks_sented = Group('The compensatory draft picks were sent to' + take_until(' on ', 'sent_to_team') + 'on' + date_nt('date') + '.')
waive_reason = MatchFirst(['(' + Literal('Ended two-way contract.')('reason') + ')',
                           Literal('Ended two-way contract.')('reason'),
                           Literal('Move made for salary cap purposes post-retirement')('reason'),
                           '(' + Literal('reached contract buyout agreement')('reason') + ')'])

signing_additional = ZeroOrMore(MatchFirst([matched_contract.set_results_name('matched_contract', True),
                                            sign_and_trade.set_results_name('sign_and_trade', True),
                                            renegotiaion_sign.set_results_name('renegotiation', True),
                                            extension.set_results_name('extension', True),
                                            sign_to_keep.set_results_name('sign_to_keep', True),
                                            jumped_to.set_results_name('jumped_to', True),
                                            returned_from.set_results_name('returned_from', True),
                                            selected_but_not_signed.set_results_name('selected_but_not_signed', True),
                                            sued.set_results_name('sued', True),
                                            for_future_services.set_results_name('for_future_services', True),
                                            compansatory_picks_sented.set_results_name('compansatory_picks_sented', True),
                                            option_to_swap.set_results_name('option_to_swap', True),
                                            contigent_on_being_on_roster_and_waved.set_results_name('contigent_on_being_on_roster_and_waved', True),
                                            sign_with_salary_and_length.set_results_name('sign_with_salary_length', True)]))

agrees_to_play_games = Group(take_until(' agreed to', 'agreeing_team') + 'agreed to play' + number('games_number') + 'home games in' + take_until('.', 'games_location') + '.')
turn_player_to_nba_after_fold = Group('(' + take_until(' was turned over to NBA after ', 'player') + 'was turned over to NBA after' +
                                      take_until(' folded and sold to', 'folding_team') + 'folded and sold to' + take_until('.)', 'selecting_team') + '.)')
dispersal_additional = MatchFirst([
    agrees_to_play_games.set_results_name('agrees_to_play_game', True),
    turn_player_to_nba_after_fold.set_results_name('players_turns_after_fold', True)
])

traded_and_returned = Group('(' + take_until(' was traded to ', 'player') + 'was traded to' + take_until(' on ', 'team') + 'on' + date_nt('date') + 'but evidently he was returned.)')
report_correction = Group('(Report says' + take_until(' also gave up ', 'solding_team') + 'also gave up' + take_until(' for ', 'gaved_up') + 'for' +
                          take_until(' in this transaction, ', 'player1') + 'in this transaction, but' + take_until(' was already sold to them ', 'player2') + 'was already sold to them on' +
                          date_nt('date') + '.)')
complete_trade = Group('(This completes the trade where' + take_until(' obtained ', 'obtaining_team') + 'obtained' + take_until(' from ', 'player') + 'from' +
                       take_until(' on ', 'obtained_from_team') + 'on' + date_nt('date') + '.)')
'(Johnson returned to Houston but Houston kept the draft picks from trade on June 9, 1977.)'
returned_and_kept = Group('(' + take_until(' returned to ', 'player') + 'returned to' + take_until(' but ', 'team1') + 'but' +
                          take_until(' kept the draft picks from trade on ', 'team2') + 'kept the draft picks from trade on' + date_nt('date') + '.)')
sold_rights_additional = MatchFirst([
    traded_and_returned.set_results_name('traded_and_returned', True),
    report_correction.set_results_name('reports_correction', True),
    played_in_between.set_results_name('played_in_between', True),
    returned_and_kept.set_results_name('returned_and_kept', True),
    complete_trade.set_results_name('compete_trade', True)
])

signing_another_team_draft_pick = Group('signing' + take_until(' draft pick ', 'team') + 'draft pick' + take_until(' in ', 'player') + 'in' + number('year') + '.')
trade_penalization_reasons = MatchFirst([
    signing_another_team_draft_pick('signing_another_team_draft_pick')
])

templates = {
    'sign and compensate': 'The' + team_nt('new_team') + 'signed' +
                           MatchFirst([person_nt('player'), take_until(' (', 'person_no_id') + '(' + possible_roles('role') + ')', take_until(' as a ', 'person_no_id')]) +
                           'as a' + Opt('veteran') + 'free agent and sent' + Group(team_trade_part)('TeamATradees') + 'to the' + team_nt('old_team') + 'as compensation.' +
                           Group(signing_additional)('additional'),
    'sign with length': 'The' + team_nt('team') + 'signed' + person_nt('player') + 'to a' + number('contract_length') + '-year contract.' + Group(signing_additional)('additional'),
    'ceremonial contract': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\. (?:\(Ceremonial Contract|ceremonial contract))')) +
                           '.' + MatchFirst([Literal('(Ceremonial Contract)'),
                                             Literal('ceremonial contract')]),
    'free agent sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' as a') + MatchFirst([Literal('as an unrestricted'), Literal('as a')]) + Opt('veteran') + 'free agent.' +
                        Group(signing_additional)('additional'),
    'multi year contract sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to a multi-year contract') + 'to a multi-year contract.' +
                        Group(signing_additional)('additional'),
    'two way contract sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to a two-way contract') + 'to a two-way contract.' + Group(signing_additional)('additional'),
    'exhibit 10': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to an Exhibit 10 contract') + 'to an Exhibit 10 contract.' + Group(signing_additional)('additional'),
    '10 day contract': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', ' to ') + 'to' + MatchFirst([Literal('a') + Opt(Literal('2nd')), Literal('the first of two')]) + '10-day contract' + Opt('s') + '.' + Group(signing_additional)('additional'),
    'contract extension': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', ' to a contract extension') + 'to a contract extension.' + Group(signing_additional)('additional'),
    'rest of season sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_nt('player') + Opt('to' + MatchFirst([Literal('a 10-day contract'), Literal('two 10-day contracts')]) + ', then signed') + 'to a contract for the rest of the season.' + Group(signing_additional)('additional'),
    're-signing': 'The' + team_nt('team') + 're-signed' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.)')) + '.' + Group(signing_additional)('additional'),
    # TODO refine
    'subtitution contract': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', ' to a substitution contract') + 'to a substitution contract (' +
                            Opt('substituting for' + person_or_unknown('substituted_player', ')')) + Opt('filled open two-way slot') + ')',
    'sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.)')) + '.' + Group(signing_additional)('additional'),
    '10 day contract expired': person_or_unknown('player', ' not re-signed by ') + 'not re-signed by' + team_nt('team') + '; 10-day contract expires.',
    'release from 10 day contract': CaselessLiteral('The') + team_nt('team') + 'released' + person_or_unknown('player', ' from ') + 'from' + Opt('2nd') + '10-day contract.',
    'waived': CaselessLiteral('The') + team_nt('team') + 'waived' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.)')) + '.' + Opt(Group(waive_reason)('reason')),
    'claimed from waivers': CaselessLiteral('The') + team_nt('newTeam') + 'claimed' + person_or_unknown('player', ' on waivers from the ') + 'on waivers from the' + team_nt('oldTeam') + '.',
    'penalty trade': one_side_trade_part + '.' + take_until(' was penalized ', 'penalized_team') + 'was penalized for' + Group(trade_penalization_reasons)('reason'),  # + restOfLine('reason'),
    'simple_trade': trade_part + '.' + Group(after_trade_part)('additional'),
    'multiple_teams_trade': 'In a' + number + '-team trade,' + ZeroOrMore(MatchFirst([Group(one_side_trade_part) + MatchFirst([Suppress('; and '), Suppress(';')]), Group(one_side_trade_part)]))('trades') + '.' + Group(after_trade_part)('additional'),
    'one side trade': one_side_trade_part + '.' + Group(after_trade_part)('additional'),
    'retirement': person_or_unknown('player', ' announced retirement') + 'announced retirement.' +
                  Opt(MatchFirst([Literal('Officially announced retiredment.'),
                                  Literal('(Announced he would retire at the end of the season)'),
                                  '(Signed with' + team_nt('retirement_team') + 'to to retire with team)'])),
    'firing': CaselessLiteral('The') + team_nt('team') + 'fired' + person_or_unknown('person', ' as ') + 'as ' + possible_roles('role') + '.',
    'appintment': CaselessLiteral('The') + team_nt('team') + 'appointed' + person_or_unknown('person', ' as ') + 'as ' + possible_roles('role') + Opt('(' + Literal('w/ day-to-day control')('role_more') + ')') + '.' +
                  Opt(MatchFirst([Literal('(Appointed on an interim basis)'),
                                  Literal('Named interim head coach')])),
    'convert contract': 'The' + team_nt('team') + 'converted' + person_or_unknown('player', ' from a two-way contract') + 'from a two-way contract to a regular contract.',
    'suspension_by_league': person_or_unknown('player', ' was suspended by the league') + 'was suspended by the league (' +
                        Opt(MatchFirst([
                                number('suspension_length_games') + '-game suspension',
                                number('suspension_length_weeks') + '-week suspension',
                                Literal('Indefinite')])) + ')',
    'suspension_by_team': person_or_unknown('player', ' was suspended from the') + 'was suspended from the' + team_nt('team') + Opt('(' + number('suspension_length') + '-game suspension)'),
    'assigned to': 'The' + team_nt('team') + 'assigned' + person_or_unknown('player', ' to the ') + 'to the ',
    'recalling': 'The' + team_nt('team') + 'recalled' + person_or_unknown('player', ' from the ') + 'from the ',
    'resignation': person_or_unknown('person', 'resigns as ') + 'resigns as' + possible_roles('role') + 'for' + team_nt('team') + '.',
    'hiring': CaselessLiteral('The') + team_nt('team') + 'hired' + person_or_unknown('person', ' as ') + 'as ' + possible_roles('role') + '.',  # + Opt('(' + take_until(')', 'role_more') + ')'),
    'sold rights': CaselessLiteral('The') + team_nt('old_team') + 'sold the player rights to' + person_or_unknown('player', ' to the ') + 'to the' + team_nt('new_team') + '.' + Opt(Group(sold_rights_additional)('additional')),  # + Opt(unknown_brackets.set_results_name('explanation')),
    'dispersal draft': 'The' + team_nt('new_team') + 'selected' + person_or_unknown('player', ' from the ') + 'from the' + team_nt('old_team') + 'in the dispersal draft.' + Opt(Group(dispersal_additional)('additional')),  # + MatchFirst([Suppress(LineEnd()), restOfLine])('next'),
    'released': 'The' + team_nt('team') + 'released' + person_or_unknown('player', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'reassignment': 'The' + team_nt('team') + 'reassigned' + possible_roles('role') + person_or_unknown('person', unknown_part=Regex(r'.+?(?=\.$)')) + '.',
    'expansion draft': 'The' + team_nt('new_team') + 'drafted' + person_or_unknown('player', ' from the ') + 'from the' + team_nt('old_team') + 'in the NBA expansion draft.',
    'role retire from team': possible_roles('role') + person_or_unknown('person', ' retired from the ') + 'retired from the' + team_nt('team'),
    'retire from team': person_or_unknown('player', ' retired from the ') + 'retired from the' + team_nt('team'),
}

def tests():
    test_str = 'The BOS sold the player rights to kudelfr01 to the BLB. (Report says Boston also gave up a 1st round draft pick for Bob Brannum in this transaction, but Brannum was already sold to them on September 23, 1950.)'
    aaa = 'Toronto had the option to swap 1st round draft picks with Dallas in 1997 (a draft pick owned by Dallas that was originally owned by Minnesota) but did not do so.'
    temp = templates['simple_trade']
    option_to_swapppp = Group(
        take_until(' had the option to swap ', 'team1') + 'had the option to swap' + take_until(' with ',
                                                                                                'could_swap') + 'with' +
        take_until(' in ', 'team2') + 'in' +
        MatchFirst([number('year') + Opt(
            '(a draft pick owned by' + take_until_new('that was originally owned by', 'owned_team') + take_until_new(
                ')', 'originally_owned_team', excluded_chars=')')),
                    'either' + number('year1') + 'or' + number('year2')]) +
        Opt(MatchFirst(['but opted for' + take_until(' instead.', 'opted_for') + 'instead',
                        'but did not do so' + Opt(';' + take_until_new('received a', 'team3') +
                                                  take_until_new('in', 'received') + number('year') + 'instead')])) +
        '.'
        )
    res = option_to_swapppp('aa').parseString(aaa)
    print(res.asDict())


if __name__ == '__main__':
    tests()


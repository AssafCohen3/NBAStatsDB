import json
import re
import string
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from pyparsing import *


# def take_until(until, label=''):
#     to_ret = Regex(fr'.+?(?={re.escape(until)})')
#     if label != '':
#         return to_ret(label)
#     return to_ret
from transactions.transaction_constants import ROLES


def take_until_new(until_nt, label='', consume=True, excluded_chars=None):
    to_ret = Combine(OneOrMore(Word(printables, exclude_chars=excluded_chars), stopOn=until_nt), join_string=' ', adjacent=False)
    if label != '':
        to_ret = to_ret(label)
    if consume:
        to_ret = to_ret + Suppress(until_nt)
    return to_ret


def person_or_unknown(label, next_part, consume=True, excluded_chars=None):
    person_nt_to_ret = person_nt
    if consume:
        person_nt_to_ret = person_nt_to_ret + Suppress(next_part)
    return MatchFirst([person_nt_to_ret(label), take_until_new(next_part, label + '_no_id', consume=consume, excluded_chars=excluded_chars)])


possible_roles = MatchFirst(list(map(Literal, ROLES)))
number = Combine(Opt('-') + ZeroOrMore(Word(string.digits) + Suppress(',') + FollowedBy(Word(string.digits))) + Word(string.digits) + Opt('.' + Word(string.digits)))
date_nt = Group(Word(alphas)('month') + number('day') + ',' + number('year'))
date_slash_nt = Group(number('month') + '/' + number('day') + '/' + number('year'))
date_no_day_nt = Group(Word(alphas)('month') + number('year'))
team_nt = Word(string.ascii_uppercase)
person_nt = Word(string.ascii_lowercase + string.digits)

protections = MatchFirst([
    CaselessLiteral('top') + Opt('-') + number('top_protection')
])
later_selected_part = Suppress('(') + person_or_unknown('player', 'was later selected)')
rounds_phrasing = MatchFirst([Literal('round'), Literal('-rd'), Literal('-round')])
rounds = MatchFirst([Literal('1st'), Literal('2nd'), Literal('3rd'), Literal('4th'), Literal('5th'), Literal('6th'), Literal('7th'), Literal('8th')])
draft_pick = Group(Suppress('a') + MatchFirst([number, Literal('future')])('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('draft pick') + Opt(later_selected_part))
protection_pick = Group(number('year') + rounds('round') + rounds_phrasing)

cash_part = Combine('$' + number + Opt(MatchFirst([CaselessLiteral('M')[1, 2], CaselessLiteral('K')])))
cash_considerations = Group(CaselessLiteral('cash considerations')('cash_considerations') + Opt('(reportedly' + cash_part('cash_sum')('cash_num') + ')'))
cash_tradee = Group(
    MatchFirst([
        Opt(cash_part('cash_sum_pre')) + CaselessLiteral('cash')('cash') + Opt('(reportedly' + cash_part('cash_sum') + ')'),
        cash_part('cash_sum')
    ]))
trade_exception = Group(MatchFirst([cash_part('cash_num'), 'a']) + Literal('trade exception')('trade_exception'))
team_tradees = MatchFirst([cash_considerations.set_results_name('cash_considerations', True),
                           trade_exception.set_results_name('trade_exception', True),
                           cash_tradee.set_results_name('cash', True),
                           Literal('future considerations').set_results_name('future_considerations', True),
                           draft_pick.set_results_name('draft_pick', True),
                           Group(person_nt('person') + '(' + take_until_new(')', 'role', excluded_chars=')')).set_results_name('person_with_role', True),
                           Regex(r'[a-z]+[0-9]+c').set_results_name('person', True),
                           person_nt.set_results_name('player', True),
                           Group(Regex(r'.+?(?=(?: \(.+\))??(?: to the |,| and |\.(?!.*to the)))')('person_no_id') + '(' + possible_roles('role') + ')').set_results_name('person_no_id_with_role', True),
                           Regex(r'.+?(?=(?: to the |,| and |\.(?!.*to the)))').set_results_name('player_no_id', True)])
team_trade_part = ZeroOrMore(team_tradees + Suppress(',')) + team_tradees + Opt(Suppress('and') + team_tradees)
pick_source = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is') + team_nt('team') + Literal('\'s pick') + Opt(', top-' + number('protection') + 'protected') + '.)')
favorable_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is least favorable pick.)'))
swap_pick = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Suppress('pick is a swap.)'))
# unknown_pick_explanation = Group(Suppress('(') + number('pick_year') + Opt(rounds('pick_round') + Suppress(rounds_phrasing)) + Combine('pick is' + CharsNotIn(')'))('explanation') + ')')
# unknown_brackets = Group(Suppress('(') + CharsNotIn(')')('content') + Suppress(')'))

trade_part = 'The' + team_nt('team_a') + 'traded' + Group(team_trade_part)('team_a_tradees') + 'to the' + \
             team_nt('team_b') + 'for' + Group(team_trade_part)('team_b_tradees')
one_side_trade_part = CaselessLiteral('The') + team_nt('trading_team') + 'traded' + Group(team_trade_part)('tradees') + 'to the' + team_nt('receiving_team')
agreed_to_terms = Group(take_until_new('agreed to terms with', 'player') + take_until_new('in', 'team') + date_no_day_nt('date_no_day') + 'to complete the trade.')
agreed_to_not_select = Group(take_until_new(Opt('also') + 'agreed' + Opt('not')('not') + 'to select', 'team') +
                             take_until_new('in the', 'player') +
                             MatchFirst([number('year'), 'expansion']) + 'draft.')
agreeing_to_take = Group('(In exchange for the' + take_until_new('agreeing to take', 'team') +
                         take_until_new('in the', 'player') +
                         MatchFirst([number('year'), 'expansion']) + 'draft)')
sources_explain = Group('Some sources have' + take_until_new('to', 'player') + take_until_new('in this deal but he was already sold to them on', 'team') +
                        date_nt('date') + '.')
player_to_be_named_later = Group(take_until_new('was sent as', 'player') + Opt('the') + 'player to be named later on' + date_nt('date') + '.')
sent_to_complete_the_trade = Group(take_until_new('was sent to', 'player') + take_until_new('to complete the trade on', 'team') + date_nt('date') + '.')
played_in_between = Group(Opt('(') + take_until_new('played in the', 'player') + take_until_new('in between.', 'played_in') + Opt(')'))
refused_to_report = Group(take_until_new('got', 'team_got') + take_until_new('in', 'got') + number('year') + 'when' + take_until_new('refused to report;', 'player1') +
                          take_until_new('was later sold to', 'player2') + take_until_new('.', 'team_sold_to', excluded_chars='.'))
original_trade_cancelled = Group(take_until_new('was originally traded for', 'traded_player') + take_until_new('on', 'original_tradee') + date_nt('date') + 'but the trade was cancelled.')
compensation_for_sign = Group('This exchange was arranged as compensation for' + take_until_new('signing veteran free agent', 'compensating_team') +
                              take_until_new('on', 'player') + date_nt('date') + '.')
for_pick_in_dispersal = Group('This trade was for the' + take_until_new('pick in the ABA dispersal draft.', 'pick'))
option_to_swap = Group(take_until_new('had the option to swap', 'team1') +
                       MatchFirst([
                           take_until_new('with', 'could_swap') + take_until_new('in', 'team2'),
                           take_until_new('in', 'could_swap')
                       ]) +
                       MatchFirst([number('year') + Opt('(a draft pick owned by' + take_until_new('that was originally owned by', 'owned_team') + take_until_new(')', 'originally_owned_team', excluded_chars=')')),
                                   'either' + number('year1') + 'or' + number('year2')]) +
                       Opt(MatchFirst(['but opted for' + take_until_new('instead', 'opted_for'),
                                       'but did not do so' + Opt(';' + take_until_new('received a', 'team3') +
                                                                 take_until_new('in', 'received') + number('year') + 'instead')])) +
                       '.'
                       )
relinquished_option_to_swap = Group(take_until_new('also relinquished the option to swap', 'team1') + take_until_new('with', 'can_swap') + take_until_new('in', 'team2') + number('year') + '.')
earlier_of_two = Group(take_until_new('received the', 'team1') + MatchFirst([Literal('earlier'), Literal('best')]) + 'of' + take_until_new('in', 'earlier_of') + number('year') + '(' +
                       MatchFirst([Literal('both'), Literal('all')]) + 'owned by' + take_until_new(').', 'team2', excluded_chars=')'))
originally_received = Group(take_until_new('originally received', 'team') + take_until_new('but he was', 'player') + take_until_new('.', 'reason', excluded_chars='.'))
received_consulation = Group(take_until_new('also received the consultation services of', 'team1') +
                             take_until_new(possible_roles, 'team2', consume=False) + possible_roles('consule_role') + take_until_new('.', 'person', excluded_chars='.'))
contigent_on_being_on_roster_and_waved = Group('The' + take_until_new('was contingent upon', 'contigent_part') +
                                               take_until_new(MatchFirst([Literal('making'), Literal('being on')]), 'player') +
                                               take_until_new(Literal('roster'), 'team') +
                                               MatchFirst([
                                                   'on' + date_nt('contignet_date') + 'but he was waived on' + date_nt('waved_on') + '.',
                                                   'but he did not do so.'
                                               ]))
conditioned_and_not_exercised = Group('The' + take_until_new('traded to', 'conditioned_part') + take_until_new(MatchFirst([Literal('was'), Literal('were')]) + 'conditional' + Opt('was') + 'and' + MatchFirst([Literal('was'), Literal('were')]) + 'not exercised.', 'team'))
# TODO check this
pick_did_not_convey = Group('Pick did not convey because' + restOfLine('reason'))
same_draft_pick = Group('This was the same' + take_until_new('that', 'same_part') + take_until_new('had previously traded to', 'team1') + take_until_new('on', 'team2') + date_nt('date') + '.')
too_complicated_to_stracture = Group(MatchFirst([
    Literal('Minnesota removed the 2nd overall draft pick through 6th overall draft pick protection on the 1st round draft pick obtained for Sean Rooks on November 1, 1994; the draft pick was changed to either 1997 (unless it was the 1st draft pick overall) or 1998.'),
    Literal('(Pick was PHI\'s choice of 2003-2005 2nd round picks. Ultimately PHI sent PHO\'s 2005 2nd round pick, acquired on 6/7/05 from UTA.)'),
    Literal('Trade originally included a first round pick from Sacramento before 2008 and was later swapped for the 2003 pick after Sacramento acquired it from Atlanta'),
    Literal('This trade was restructured in September 2009. In the original version, New Jersey received either a protected 1st round draft pick (2011, 2012, or 2013) or two 2nd round draft picks (2013 and 2015).'),
    Literal('The 2nd round draft pick that Denver received was top 55 protected, but that protection was removed in a later deal.'),
    'The 2nd round draft pick that Dallas received was top 55 protected, but that protection was removed in a later deal.',
    'Cleveland had the option to swap the least favorable of its 1st round draft picks with Los Angeles in 2013 and did so.',
    'Right to swap 2016 2nd-rd picks became #33 for #55 after Los Angeles acquired pick from Milwaukee',
    """(NOH traded MIN's 2016 2nd-round pick back to MIN; MIN traded top-13 protected 2014 1st round pick, which became 2016 and 2017 2nd round picks, including the pick MIN re-acquired from NOH, to PHO.)""",
    """(1st Round pick from PHI to ORL was eventually traded back to PHI. 1st-Rd pick from LAL to ORL turns into 2017 & 2018 2nd-Rd picks if Lakers 1st-Rd pick traded to PHO/PHI does not convey by 2017)""",
    'Memphis lifted the top-55 protection on the 2016 2nd-round draft pick sent to Dallas (via Denver) in a previous deal.'
]))
protected_must_land = Group(take_until_new('was protected and required to', 'protected_part') + take_until_new(', conveying by', 'protection', excluded_chars=',') +
                            number('year') + 'at the latest')
# TODO check this
originally_included = Group('Trade originally included' + take_until_new('that became', 'originally_included') + take_until_new('after', 'became_to') + restOfLine('reason'))
accepted_in_lieu = Group(take_until_new('accepted', 'team1') + take_until_new('from', 'tradee1') + take_until_new('on', 'team2') + date_nt('date') + 'in lieu of' + take_until_new('.', 'in_lieu_of', excluded_chars='.'))
originally_sented = Group('The' + take_until_new('was originally sent from', 'tradee') + take_until_new('to', 'team1') + take_until_new('in a trade on', 'team2') + date_nt('date') + '.')
trade_exception = Group(take_until_new('also received a trade exception from', 'team1') + take_until_new('.', 'team2', excluded_chars='.'))
did_not_receive_beacuse_protection = Group(take_until_new('did not receive the', 'team1') +
                                           MatchFirst([take_until_new('from', 'tradee1') + take_until_new('because', 'team2'),
                                                       take_until_new(MatchFirst([Literal('because'), Literal('beacuse')]), 'tradee1')]) +
                                           MatchFirst([
                                               take_until_new('; they received', 'reason', excluded_chars=';') + take_until_new('instead.', 'tradee2'),
                                               take_until_new('.', 'reason', excluded_chars='.')
                                           ]))
acquired_rights_to_swap = Group('(' + take_until_new('acquired right to swap', 'team1') + take_until_new('with', 'rights_to') + take_until_new(')', 'team2', excluded_chars=')'))
got_as_result = Group('(' + team_nt('team1') + 'got' + number('year') + '#' + number('overall') + 'overall pick from' + team_nt('team2') + 'as result of pick swap)')
is_right_to_swap_option = Group('(' + protection_pick + 'pick' + 'is' + team_nt('team') + Opt('\'s') + 'option right-to-swap)')

pick_protection_generic = Group(
    MatchFirst([
        '(pick was protected and did not convey)',
        '(' + Group(protections)('protection') + 'protected, so never conveyed)',
        '(' + Opt(Opt(protection_pick + 'pick is') + Group(protections)('protection')) + 'protected' + (Literal(',') | 'and') + 'did not convey)',
        '(Pick is' + Group(protections + Opt('and' + number('range1') + '-' + number('range2')))('protection') + 'protected and was not conveyed)'
        #
        # '(' + take_until_new('protected, so never conveyed)', 'protection'),
        # '(Pick is' + take_until_new('protected', 'protection') + ('.' | Literal('and was not conveyed')) + ')',
        # '(' + take_until_new('pick was protected and not conveyed)', 'protected_part'),
        # '(Pick is conditional and did not convey.)',
        # take_until_new('was protected and not conveyed', 'protected_part'),
        # '(' + Opt('The') + take_until_new('acquired', 'team') + take_until_new((Literal('was') | 'is' | 'are'), 'protected_part') +
        # Opt(take_until_new('protected', 'protection')),
        # '(' + Opt('The') + take_until_new('acquired', 'team') + take_until_new((Literal('was') | 'is') + 'protected' + Opt('and' + Opt('did') + 'not convey' + Opt('ed')) + '.)', 'pick'),
    ])
)
unknown_brackets = Group('(' + take_until_new(')', 'unknown_part', excluded_chars='()'))
after_trade_part = MatchFirst([OneOrMore(MatchFirst([cash_part('cash_sum'),
                                                     pick_source.set_results_name('picks_sources', True),
                                                     favorable_pick.set_results_name('favorable_picks', True),
                                                     swap_pick.set_results_name('swap_picks', True),
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
                                                     agreeing_to_take.set_results_name('agreeing_to_take', True),
                                                     pick_did_not_convey.set_results_name('pick_did_not_convey', True),
                                                     same_draft_pick.set_results_name('same_draft_pick', True),
                                                     protected_must_land.set_results_name('protected_must_land', True),
                                                     originally_included.set_results_name('originally_included', True),
                                                     accepted_in_lieu.set_results_name('accepted_in_lieu', True),
                                                     originally_sented.set_results_name('originally_sented', True),
                                                     trade_exception.set_results_name('trade_exception', True),
                                                     did_not_receive_beacuse_protection.set_results_name('did_not_receive_beacuse_protection', True),
                                                     acquired_rights_to_swap.set_results_name('acquired_rights_to_swap', True),
                                                     got_as_result.set_results_name('got_as_result', True),
                                                     is_right_to_swap_option.set_results_name('is_right_to_swap_option', True),
                                                     pick_protection_generic.set_results_name('pick_protection_generic', True),
                                                     agreed_to_terms.set_results_name('agreeds_to_terms', True),
                                                     unknown_brackets.set_results_name('unknown_brackets', True)])) + line_end,
                               Regex(r".+")('unknown_all')])
# Regex('.+').set_results_name('unknown_all', True)]))
# too_complicated_to_stracture.set_results_name('too_complicated_to_stracture', True),

matched_contract = Group('(' + team_nt('matching_team') + 'matched offer sheet signed with' + team_nt('matched_team') + ')')
# sign_extension = '(Signing is extension' + MatchFirst([Literal('on'), Literal('of')]) + 'deal signed in ' + number + Opt('.') + ')'
sign_and_trade = Group('(Sign and trade with' + take_until_new(')', 'sign_and_traded_from_team', excluded_chars=')'))
renegotiaion_sign = Group('Signing is a renegotiation & extension of deal signed in' + number)
extension = Group('(Signing is extension' + MatchFirst([Literal('on'), Literal('of')]) + 'deal signed in' + number + Opt('and extended in' + number) + Opt('.') + ')')
sign_to_keep = Group('(Signing is an extension to keep him under contract thru' + number + '-' + number + ')')
sign_with_salary_and_length = Group('Signed ' + number('contract_length') + '-yr/' + cash_part('salary') + 'contract ' + restOfLine('sign_date'))
jumped_to = Group('(' + take_until_new('to the', 'player') + take_until_new('.)', 'jumped_to', excluded_chars='.'))
returned_from = Group('(' + take_until_new('returned from the', 'player') + take_until_new('.)', 'returned_from', excluded_chars='.'))
selected_but_not_signed = Group('(' + take_until_new('was selected by', 'player') + take_until_new('in the expansion draft but did not sign.)', 'team'))
sued = Group('(The NBA sued' + take_until_new('because', 'team') + take_until_new('; the Supreme Court ruled', 'reason', excluded_chars=';') +
             take_until_new('on', 'court_decision') + date_nt('date') + '.)')
for_future_services = Group('(' + take_until_new('was playing in the', 'player') + take_until_new('at the time and was signed for future services.)', 'played_in'))
compansatory_picks_sented = Group('The compensatory draft picks were sent to' + take_until_new('on', 'sent_to_team') + date_nt('date') + '.')
waive_reason = MatchFirst(['(' + Literal('Ended two-way contract.')('reason') + ')',
                           Literal('Ended two-way contract.')('reason'),
                           Literal('Move made for salary cap purposes post-retirement')('reason'),
                           '(' + Literal('reached contract buyout agreement')('reason') + ')'])

signing_additional = OneOrMore(MatchFirst([matched_contract.set_results_name('matched_contract', True),
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

agrees_to_play_games = Group(take_until_new('agreed to play', 'agreeing_team') + number('games_number') + 'home games in' + take_until_new('.', 'games_location', excluded_chars='.'))
turn_player_to_nba_after_fold = Group('(' + take_until_new('was turned over to NBA after', 'player') +
                                      take_until_new('folded and sold to', 'folding_team') + take_until_new('.)', 'selecting_team', excluded_chars='.'))
dispersal_additional = MatchFirst([
    agrees_to_play_games.set_results_name('agrees_to_play_game', True),
    turn_player_to_nba_after_fold.set_results_name('players_turns_after_fold', True)
])

traded_and_returned = Group('(' + take_until_new('was traded to', 'player') + take_until_new('on', 'team') + date_nt('date') + 'but evidently he was returned.)')
report_correction = Group('(Report says' + take_until_new('also gave up', 'solding_team') + take_until_new('for', 'gaved_up') +
                          take_until_new('in this transaction, but', 'player1') + take_until_new('was already sold to them on', 'player2') +
                          date_nt('date') + '.)')
complete_trade = Group('(This completes the trade where' + take_until_new('obtained', 'obtaining_team') + take_until_new('from', 'player') +
                       take_until_new('on', 'obtained_from_team') + date_nt('date') + '.)')
returned_and_kept = Group('(' + take_until_new('returned to', 'player') + take_until_new('but', 'team1') +
                          take_until_new('kept the draft picks from trade on', 'team2') + date_nt('date') + '.)')
sold_rights_additional = MatchFirst([
    traded_and_returned.set_results_name('traded_and_returned', True),
    report_correction.set_results_name('reports_correction', True),
    played_in_between.set_results_name('played_in_between', True),
    returned_and_kept.set_results_name('returned_and_kept', True),
    complete_trade.set_results_name('compete_trade', True)
])

signing_another_team_draft_pick = Group('signing' + take_until_new('draft pick', 'team') + take_until_new('in', 'player') + number('year') + '.')
trade_penalization_reasons = MatchFirst([
    signing_another_team_draft_pick('signing_another_team_draft_pick')
])

subtitution_additinonal = MatchFirst([
    '; contract disapproved on' + date_slash_nt + 'due to failed physical)',
    ', whose subsitute contract for' + person_or_unknown('player', 'was disapproved)', excluded_chars=')'),
    ')'
])

templates = {
    'sign_and_compensate': 'The' + team_nt('new_team') + 'signed' +
                           MatchFirst([person_nt('player'), Group(take_until_new('(', 'person_no_id') + possible_roles('role') + ')')('person_with_role'), take_until_new('as a', 'person_no_id', consume=False)]) +
                           'as a' + Opt('veteran') + 'free agent and sent' + Group(team_trade_part)('team_a_tradees') + 'to the' + team_nt('old_team') + 'as compensation.' +
                           Opt(Group(signing_additional)('additional')),
    'sign_with_length': 'The' + team_nt('team') + 'signed' + person_nt('player') + 'to a' + number('contract_length') + '-year contract.' + Opt(Group(signing_additional)('additional')),
    'ceremonial_contract': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', next_part='.' + Opt('(') + CaselessLiteral('ceremonial contract') + Opt(')')),
    'free_agent_sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', MatchFirst([Literal('as an unrestricted'), Literal('as a')])) + Opt('veteran') + 'free agent.' +
                        Opt(Group(signing_additional)('additional')),
    'multi_year_contract_sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', 'to a multi-year contract.') +
                        Opt(Group(signing_additional)('additional')),
    'two_way_contract_sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', 'to a two-way contract.') + Opt(Group(signing_additional)('additional')),
    'exhibit_10': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', 'to an Exhibit 10 contract.') + Opt(Group(signing_additional)('additional')),
    '10_day_contract': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', 'to') + MatchFirst([Literal('a') + Opt(Literal('2nd')), Literal('the first of two')]) + '10-day contract' + Opt('s') + '.' + Opt(Group(signing_additional)('additional')),
    'contract_extension': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', 'to a contract extension.') + Opt(Group(signing_additional)('additional')),
    'rest_of_season_sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', 'to') + Opt(MatchFirst([Literal('a 10-day contract'), Literal('two 10-day contracts')]) + ', then signed to') + 'a contract for the rest of the season.' + Opt(Group(signing_additional)('additional')),
    're_signing': 'The' + team_nt('team') + 're-signed' + person_or_unknown('player', '.', excluded_chars='.') + Opt(Group(signing_additional)('additional')),
    # TODO refine
    'subtitution_contract': 'The' + team_nt('team') + 'signed' + person_or_unknown('player', 'to a substitution contract (') +
                            ('substituting for' +
                             person_or_unknown('substituted_player', MatchFirst([Literal(','), Literal(';'), Literal(')')]), excluded_chars=';,)', consume=False) +
                             Suppress(subtitution_additinonal)
                             |
                             'filled open two-way slot)'),
    'sign': CaselessLiteral('The') + team_nt('team') + 'signed' + person_or_unknown('player', '.', excluded_chars='.') + Opt(Group(signing_additional)('additional')),
    '10_day_contract_expired': person_or_unknown('player', 'not re-signed by') + team_nt('team') + '; 10-day contract expires.',
    'release_from_10_day_contract': CaselessLiteral('The') + team_nt('team') + 'released' + person_or_unknown('player', 'from') + Opt('2nd') + '10-day contract.',
    'waived': CaselessLiteral('The') + team_nt('team') + 'waived' + person_or_unknown('player', '.', excluded_chars='.') + Opt(Group(waive_reason)('reason')),
    'claimed_from_waivers': CaselessLiteral('The') + team_nt('new_team') + 'claimed' + person_or_unknown('player', 'on waivers from the') + team_nt('old_team') + '.',
    'penalty_trade': one_side_trade_part + '.' + take_until_new('was penalized for', 'penalized_team') + Group(trade_penalization_reasons)('reason'),
    'simple_trade': trade_part + '.' + Opt(Group(after_trade_part)('additional')),
    'multiple_teams_trade': 'In a' + number + '-team trade,' + ZeroOrMore(MatchFirst([Group(one_side_trade_part) + MatchFirst([Suppress('; and '), Suppress(';')]), Group(one_side_trade_part)]))('trades') + '.' + Opt(Group(after_trade_part)('additional')),
    'one_side_trade': one_side_trade_part + '.' + Opt(Group(after_trade_part)('additional')),
    'retirement': MatchFirst([Regex(r'[a-z]+[0-9]+x')('person') + 'announced retirement.', person_or_unknown('player', 'announced retirement.')]) +
                  Opt(MatchFirst([Literal('Officially announced retiredment.'),
                                  Literal('(Announced he would retire at the end of the season)'),
                                  '(Announced he would retire at the end of the' + Combine(number + '-' + number)('retirement_season') + 'season on' + date_slash_nt('retirement_date') + '.)',
                                  '(Signed with' + team_nt('retirement_team') + 'to to retire with team)'])),
    'firing': CaselessLiteral('The') + team_nt('team') + 'fired' + person_or_unknown('person', 'as') + possible_roles('role') + '.' + Opt('(Parties mutually agreed to part ways.)'),
    'appointment': CaselessLiteral('The') + team_nt('team') + 'appointed' + person_or_unknown('person', 'as') + possible_roles('role') + Opt('(' + Suppress('w/ day-to-day control') + ')') + '.' +
                  Opt(MatchFirst([Literal('(Appointed on an interim basis)'),
                                  Literal('Named interim head coach')])),
    'convert_contract': 'The' + team_nt('team') + 'converted' + person_or_unknown('player', 'from a two-way contract to a regular contract.'),
    'suspension_by_league': person_or_unknown('player', 'was suspended by the league (') +
                        Opt(MatchFirst([
                                number('suspension_length_games') + '-game suspension',
                                number('suspension_length_weeks') + '-week suspension',
                                Literal('Indefinite')])) + ')',
    'suspension_by_team': person_or_unknown('player', 'was suspended from the') + team_nt('team') + Opt('(' + number('suspension_length') + '-game suspension)'),
    'assigned_to': 'The' + team_nt('team') + 'assigned' + person_or_unknown('player', 'to the') + (take_until_new('of the', 'assigned_to_team') | 'of the') + take_until_new('.', 'where', excluded_chars='.'),
    'recalling': 'The' + team_nt('team') + 'recalled' + person_or_unknown('player', 'from the') + (take_until_new('of the', 'recalling_from_team') | 'of the') + take_until_new('.', 'where', excluded_chars='.'),
    'resignation': person_or_unknown('person', 'resigns as') + possible_roles('role') + 'for' + team_nt('team') + '.',
    'hiring': CaselessLiteral('The') + team_nt('team') + 'hired' + person_or_unknown('person', 'as') + possible_roles('role') + '.' + Opt('(Interim)'),
    'sold_rights': CaselessLiteral('The') + team_nt('old_team') + 'sold the player rights to' + person_or_unknown('player', 'to the') + team_nt('new_team') + '.' + Opt(Group(sold_rights_additional)('additional')),
    'dispersal_draft': 'The' + team_nt('new_team') + 'selected' + person_or_unknown('player', 'from the') + team_nt('old_team') + 'in the dispersal draft.' + Opt(Group(dispersal_additional)('additional')),
    'released': 'The' + team_nt('team') + 'released' + person_or_unknown('player', '.' + line_end, excluded_chars='.'),
    'reassignment': 'The' + team_nt('team') + 'reassigned' + possible_roles('role') + person_or_unknown('person', '.' + line_end, excluded_chars='.'),
    'expansion_draft': 'The' + team_nt('new_team') + 'drafted' + person_or_unknown('player', 'from the') + team_nt('old_team') + 'in the NBA expansion draft.',
    'role_retire_from_team': possible_roles('role') + person_or_unknown('person', 'retired from the') + team_nt('team'),
    'retire_from_team': person_or_unknown('player', 'retired from the') + team_nt('team'),
}


def parse_transaction(transaction):
    for desc, template in templates.items():
        try:
            res = template.parseString(transaction, True).asDict()
        except ParseException:
            continue
        return [transaction, desc, res]
    return None


def generate_season_transactions(season):
    with open(f'../transactions/cache/transactions_{season}.txt', 'r') as f:
        transactions = json.load(f)
    for season, transaction_year, transaction_month, transaction_day, transaction_number, transaction_text, transaction_to_find in transactions:
        parsed = parse_transaction(transaction_text)
        if not parsed:
            if 'traded  to the' in transaction_text:
                continue
            raise Exception(f'not found for {transaction_text} in {transaction_year}-{transaction_month}-{transaction_day}')
        yield [transaction_year, transaction_month, transaction_day, transaction_number, *parsed, transaction_to_find]


def parse_test(season):
    with open(f'../transactions/transactions_{season}.txt', 'r') as f:
        transactions = json.load(f)
    parsed = defaultdict(list)
    count = 0
    for i, (day, day_transactions) in enumerate(transactions.items()):
        # print(f'parsing {day} transactions...')
        for transaction, transaction_to_find in day_transactions:
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
                raise Exception(f'not found for {transaction} in {day}')
                # print(f'not found for {transaction} in {day}')
    # for day, day_transactions in parsed.items():
    #     for initial, transaction_desc, transaction_dict in day_transactions:
    #         if transaction_desc in ['multiple_teams_trade', 'simple_trade'] and ('unknown_draft_bracketsss' in transaction_dict or 'unknown_brackets' in transaction_dict):
    #             print(day)
    #             print(initial)
    #             print(transaction_desc)
    #             print(transaction_dict)
    #             print('*******************************')
    return count


def parse_all():
    count = 0
    for season in range(1950, 2022):
        # print(f'parsing {season}...')
        count += parse_test(season)
    print(count)


def generate_transactions(from_season=1950):
    for season in range(from_season, 2022):
        for t in generate_season_transactions(season):
            yield season - 1, *t



def tests():
    test_str = 'The BOS sold the player rights to kudelfr01 to the BLB. (Report says Boston also gave up a 1st round draft pick for Bob Brannum in this transaction, but Brannum was already sold to them on September 23, 1950.)'
    aaa = 'The 2nd round draft pick was contingent upon Campbell making Washington\'s roster but he did not do so.'
    temp = templates['simple_trade']
    res = temp('aaa').parseString(aaa)
    print(res.asDict())


if __name__ == '__main__':
    # tests()
    # scrape_all()
    parse_all()



import json
from dbmanager.transactions.MarkingDict import MarkingDict, create_deep_mraking_dict


class TransactionsCreator:
    def __init__(self):
        self.transformations_chain = {
            'free_agent_sign': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'two_way_contract_sign': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'sign': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'subtitution_contract': [self.create_sign_transaction(),
                                     self.collect_to_unknown(['substituted_player_no_id']),
                                     self.optional_property('additional', self.get_single_and_assert)],
            'exhibit_10': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'convert_contract': [self.create_sign_transaction('sign', True, 'convert'), self.optional_property('additional', self.get_single_and_assert)],
            'ceremonial_contract': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            '10_day_contract': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'rest_of_season_sign': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'sign_with_length': [self.create_sign_transaction(), self.collect_to_unknown(['contract_length'])],
            'contract_extension': [self.create_sign_transaction('sign', True, 'extension'), self.optional_property('additional', self.get_single_and_assert)],
            're_signing': [self.create_sign_transaction('sign', True, 're-sign'), self.optional_property('additional', self.get_single_and_assert)],
            'multi_year_contract_sign': [self.create_sign_transaction(), self.optional_property('additional', self.get_single_and_assert)],
            'sold_rights': [self.create_move_transaction('sold rights', False, 'sold rights'), self.optional_property('additional', self.get_single_and_assert)],
            'dispersal_draft': [self.create_move_transaction('draft selection', True, 'draft selection'), self.optional_property('additional', self.get_single_and_assert)],
            'expansion_draft': [self.create_move_transaction('draft selection', True, 'draft selection'), self.optional_property('additional', self.get_single_and_assert)],
            'hiring': [self.create_executive_transaction('hire', True, 'hired to team')],
            'appointment': [self.create_executive_transaction('appoint', True, 'hired to team')],
            'reassignment': [self.create_executive_transaction('reassign', True, 'hired to team')],
            'simple_trade': [self.create_simple_trade_transaction],
            'sign_and_compensate': [self.create_sign_and_compensate_transaction],
            'multiple_teams_trade': [self.create_multiple_team_trade_transaction],
            'penalty_trade': [self.create_penalty_trade_transaction],
            'one_side_trade': [self.create_single_side_trade],
            'waived': [self.create_sign_transaction('waive', False, 'leave team'), self.collect_to_unknown(['reason'])],
            'released': [self.create_sign_transaction('release', False, 'leave team')],
            '10_day_contract_expired': [self.create_sign_transaction('contract expired', False, 'leave team')],
            'release_from_10_day_contract': [self.create_sign_transaction('released', False, 'leave team')],
            'suspension_by_league': [self.optional_property_destruct('player', self.get_single_and_assert),
                                     self.optional_property_destruct('player_no_id', self.get_single_and_assert),
                                     self.collect_to_unknown(['suspension_length_games', 'suspension_length_weeks']), self.add_properties('suspension', True, 'suspended')],
            'suspension_by_team': [self.create_sign_transaction('suspension', True, 'suspended'), self.collect_to_unknown(['suspension_length'])],
            'resignation': [self.create_executive_transaction('resign', False, 'leave team')],
            'firing': [self.create_executive_transaction('fire', False, 'leave team')],
            'assigned_to': [self.create_sign_transaction('assign to', False, 'leave team'), self.collect_to_unknown(['assigned_to_team', 'where'])],
            'recalling': [self.create_sign_transaction('recall', True, 'return to team'), self.collect_to_unknown(['recalling_from_team', 'where'])],
            'claimed_from_waivers': [self.create_move_transaction('claim from waivers', True, 'claim from waivers')],
            'retire_from_team': [self.create_sign_transaction('retire', False, 'leave team')],
            'role_retire_from_team': [self.create_executive_transaction('retire', False, 'leave team')],
            'retirement': [self.optional_property_destruct('player', self.get_single_and_assert),
                           self.optional_property_destruct('person', self.get_single_and_assert),
                           self.add_properties('retire', False, 'retire'),
                           self.collect_to_unknown(['retirement_season', 'retirement_date', 'retirement_team'])]
        }

    @staticmethod
    def add_properties(action_type, on_roster_after, sub_type_a):
        def def_to_ret(_):
            return {
                'action_type': action_type,
                'sub_type_a': sub_type_a,
                'on_team_a_after': on_roster_after,
            }
        return def_to_ret

    @staticmethod
    def create_default_transaction(transaction_year, transaction_month, transaction_day, transaction_season, transaction_number, transaction_type):
        return {
            'season': transaction_season,
            'year': transaction_year,
            'month': transaction_month,
            'day': transaction_day,
            'transaction_number': transaction_number,
            'team_a_nba_id': 0,
            'team_a_nba_name': None,
            'team_a_bref_abbr': '',
            'team_a_bref_name': '',
            'team_b_nba_id': 0,
            'team_b_nba_name': None,
            'team_b_bref_abbr': '',
            'team_b_bref_name': '',
            'player_bref_id': '',
            'player_bref_name': '',
            'player_nba_id': 0,
            'player_nba_name': None,
            'person_bref_id': '',
            'person_bref_name': '',
            'person_role': None,
            'transaction_type': transaction_type,
            'action_type': '',
            'sub_type_a': '',
            'sub_type_b': None,
            'sub_type_c': None,
            'on_team_a_after': False,
            'on_team_b_after': False,
            'pick_year': -1,
            'pick_round': -1,
            'picks_number': -1,
            'tradee_type': '',
            'additional': '{}'
        }

    @staticmethod
    def optional_property(opt_property, transformation=lambda a: a):
        def def_to_ret(analyzed_transaction):
            return {
                opt_property: transformation(analyzed_transaction[opt_property])
            } if opt_property in analyzed_transaction else {}
        return def_to_ret

    @staticmethod
    def optional_property_destruct(opt_property, transformation=lambda a: a):
        def def_to_ret(analyzed_transaction):
            return {
                **transformation(analyzed_transaction[opt_property])
            } if opt_property in analyzed_transaction else {}
        return def_to_ret

    @staticmethod
    def get_element_with_no_id_option(parent, element_name):
        return parent[element_name] if element_name in parent else parent[element_name + '_no_id']

    @staticmethod
    def get_single_and_assert(element):
        if len(element) != 1:
            raise Exception('wattt')
        return element[0]

    @staticmethod
    def destruct_team_obj(team_obj, prefix='team_a'):
        return {
            f'{prefix}_nba_id': team_obj['team_nba_id'],
            f'{prefix}_nba_name': team_obj['team_nba_name'],
            f'{prefix}_bref_abbr': team_obj['team_bref_abbr'],
            f'{prefix}_bref_name': team_obj['team_bref_name'],
        }

    def collect_to_unknown(self, to_collect):
        def def_to_ret(analyzed_transaction):
            additional_obj = {}
            for p in to_collect:
                additional_obj.update(self.optional_property(p, self.get_single_and_assert)(analyzed_transaction))
            for k, i in additional_obj.items():
                if isinstance(i, MarkingDict):
                    additional_obj[k] = dict(i)
            return {
                'additional': json.dumps(additional_obj)
            } if additional_obj else {}
        return def_to_ret

    def transform_tradee(self, tradee_type, objects):
        if tradee_type in ('player', 'player_no_id'):
            return [{
                **o,
                'tradee_type': 'player'
            } for o in objects]
        elif tradee_type == 'person_no_id_with_role':
            return [{
                'person_bref_id': self.get_single_and_assert(o['person_no_id'])['person_bref_id'],
                'person_bref_name': self.get_single_and_assert(o['person_no_id'])['person_bref_name'],
                'person_role': self.get_single_and_assert(o['role']),
                'tradee_type': 'executive'
            } for o in objects]
        elif tradee_type == 'person_with_role':
            return [{
                'person_bref_id': self.get_single_and_assert(o['person'])['person_bref_id'],
                'person_bref_name': self.get_single_and_assert(o['person'])['person_bref_name'],
                'person_role': self.get_single_and_assert(o['role']),
                'tradee_type': 'executive'
            } for o in objects]
        elif tradee_type == 'person':
            return [{
                'person_bref_id': o['person_bref_id'],
                'person_bref_name': o['person_bref_name'],
                'tradee_type': 'executive'
            } for o in objects]
        elif tradee_type == 'cash':
            cash_obj = self.get_single_and_assert(objects)
            if 'cash' in cash_obj:
                cash = self.get_single_and_assert(cash_obj['cash'])
                if cash != 'cash':
                    raise Exception(f'wat. cash = {cash}')
            return [{
                **self.collect_to_unknown(['cash_sum_pre'])(cash_obj),
                **self.collect_to_unknown(['cash_sum'])(cash_obj),
                'tradee_type': 'cash'
            }]
        elif tradee_type == 'trade_exception':
            trade_exception_obj = self.get_single_and_assert(objects)
            trade_exception = self.get_single_and_assert(trade_exception_obj['trade_exception'])
            if trade_exception != 'trade exception':
                raise Exception(f'wat. trade_exception = {trade_exception}')
            return [{
                **self.collect_to_unknown(['cash_num'])(trade_exception_obj),
                'tradee_type': 'trade exception'
            }]
        elif tradee_type == 'cash_considerations':
            cash_considerations_obj = self.get_single_and_assert(objects)
            cash_considerations = self.get_single_and_assert(cash_considerations_obj['cash_considerations'])
            if cash_considerations != 'cash considerations':
                raise Exception(f'wat. cash_considerations = {cash_considerations}')
            return [{
                **self.collect_to_unknown(['cash_num'])(cash_considerations_obj),
                'tradee_type': 'cash considerations'
            }]
        elif tradee_type == 'draft_pick':
            picks = [{
                **self.optional_property('pick_round', self.get_single_and_assert)(p),
                'pick_year': self.get_single_and_assert(p['pick_year']),
                'tradee_type': 'draft pick',
                'picks_number': 1,
                **self.optional_property_destruct('player', self.get_single_and_assert)(p),
                **self.optional_property_destruct('player_no_id', self.get_single_and_assert)(p)
            } for p in objects]
            dups = {}
            for d in picks:
                pick_round_key = d['pick_round'] if 'pick_round' in d else -1
                pick_player_key = d['player_bref_name'] if 'player_bref_name' in d else -1
                pick_key = (d['pick_year'], pick_round_key, pick_player_key)
                if pick_key not in dups:
                    dups[pick_key] = 0
                dups[pick_key] = dups[pick_key] + 1
            to_ret = []
            for d in picks:
                pick_round_key = d['pick_round'] if 'pick_round' in d else -1
                pick_player_key = d['player_bref_name'] if 'player_bref_name' in d else -1
                pick_key = (d['pick_year'], pick_round_key, pick_player_key)
                if pick_key in dups:
                    if dups[pick_key] > 1:
                        to_ret.append({
                            **d,
                            'picks_number': dups[pick_key]
                        })
                        dups.pop(pick_key)
                    else:
                        to_ret.append(d)
            return to_ret
        elif tradee_type == 'future_considerations':
            cons = self.get_single_and_assert(objects)
            if cons != 'future considerations':
                raise Exception(f'wat. future considerations = {cons}')
            return [{
                'tradee_type': 'future considerations'
            }]
        raise Exception(f'unknown tradee type: {tradee_type}')

    def transform_tradees(self, tradees):
        to_ret = []
        for key, value in tradees.items():
            to_ret.extend(self.transform_tradee(key, value))
        return to_ret

    def create_multiple_team_trade_transaction(self, analyzed_trade):
        patches_to_ret = []
        for trade in analyzed_trade['trades']:
            team_a_obj = self.get_single_and_assert(trade['receiving_team'])
            team_b_obj = self.get_single_and_assert(trade['trading_team'])
            team_b_tradees_obj = self.get_single_and_assert(trade['tradees'])
            initial_team_b_to_a_trade_object = {
                **self.destruct_team_obj(team_a_obj),
                **self.destruct_team_obj(team_b_obj, 'team_b'),
                'action_type': 'trade',
                'sub_type_a': 'move',
                'on_team_a_after': True,
                'on_team_b_after': False,
            }
            team_b_tradees_patches = self.transform_tradees(team_b_tradees_obj)
            patches_to_ret.extend([{**initial_team_b_to_a_trade_object, **patch} for patch in team_b_tradees_patches])
        return patches_to_ret + [self.optional_property('additional', self.get_single_and_assert)(analyzed_trade)]

    def create_single_side_trade(self, analyzed_trade):
        team_a_obj = self.get_single_and_assert(analyzed_trade['receiving_team'])
        team_b_obj = self.get_single_and_assert(analyzed_trade['trading_team'])
        team_b_tradees_obj = self.get_single_and_assert(analyzed_trade['tradees'])
        initial_team_b_to_a_trade_object = {
            **self.destruct_team_obj(team_a_obj),
            **self.destruct_team_obj(team_b_obj, 'team_b'),
            'action_type': 'trade',
            'sub_type_a': 'move',
            'on_team_a_after': True,
            'on_team_b_after': False,
        }
        team_b_tradees_patches = self.transform_tradees(team_b_tradees_obj)
        return [dict(**initial_team_b_to_a_trade_object, **patch) for patch in team_b_tradees_patches] + [self.optional_property('additional', self.get_single_and_assert)(analyzed_trade)]

    def create_penalty_trade_transaction(self, analyzed_trade):
        penalized_team = self.destruct_team_obj(self.get_single_and_assert(analyzed_trade['penalized_team']), 'penalized_team')
        reason = self.get_single_and_assert(analyzed_trade['reason'])
        additional_patch = {
            **penalized_team,
            'reason': reason
        }
        team_a_obj = self.get_single_and_assert(analyzed_trade['receiving_team'])
        team_b_obj = self.get_single_and_assert(analyzed_trade['trading_team'])
        team_b_tradees_obj = self.get_single_and_assert(analyzed_trade['tradees'])
        initial_team_b_to_a_trade_object = {
            **self.destruct_team_obj(team_a_obj),
            **self.destruct_team_obj(team_b_obj, 'team_b'),
            'action_type': 'trade',
            'sub_type_a': 'move',
            'on_team_a_after': True,
            'on_team_b_after': False,
        }
        team_b_tradees_patches = self.transform_tradees(team_b_tradees_obj)
        return [dict(**initial_team_b_to_a_trade_object, **patch) for patch in team_b_tradees_patches] + [{
            'additional': json.dumps(additional_patch)
        }]

    def create_simple_trade_transaction(self, analyzed_trade):
        team_a_obj = self.get_single_and_assert(analyzed_trade['team_a'])
        team_a_tradees_obj = self.get_single_and_assert(analyzed_trade['team_a_tradees'])
        team_b_obj = self.get_single_and_assert(analyzed_trade['team_b'])
        team_b_tradees_obj = self.get_single_and_assert(analyzed_trade['team_b_tradees'])
        initial_team_a_to_b_trade_object = {
            **self.destruct_team_obj(team_b_obj),
            **self.destruct_team_obj(team_a_obj, 'team_b'),
            'action_type': 'trade',
            'sub_type_a': 'move',
            'on_team_a_after': True,
            'on_team_b_after': False,
        }
        initial_team_b_to_a_trade_object = {
            **self.destruct_team_obj(team_a_obj),
            **self.destruct_team_obj(team_b_obj, 'team_b'),
            'action_type': 'trade',
            'sub_type_a': 'move',
            'on_team_a_after': True,
            'on_team_b_after': False,
        }
        team_a_tradees_patches = self.transform_tradees(team_a_tradees_obj)
        team_b_tradees_patches = self.transform_tradees(team_b_tradees_obj)
        return [{**initial_team_a_to_b_trade_object, **patch} for patch in team_a_tradees_patches] + \
               [{**initial_team_b_to_a_trade_object, **patch} for patch in team_b_tradees_patches] + [self.optional_property('additional', self.get_single_and_assert)(analyzed_trade)]

    def create_sign_and_compensate_transaction(self, analyzed_transaction):
        move_transaction = self.create_move_transaction('sign', True, 'sign')(analyzed_transaction)
        team_a_obj = self.get_single_and_assert(analyzed_transaction['new_team'])
        team_a_tradees_obj = self.get_single_and_assert(analyzed_transaction['team_a_tradees'])
        team_b_obj = self.get_single_and_assert(analyzed_transaction['old_team'])
        initial_team_a_to_b_trade_object = {
            'action_type': 'trade',
            'sub_type_a': 'move',
            'on_team_a_after': True,
            'on_team_b_after': False,
            **self.destruct_team_obj(team_b_obj),
            **self.destruct_team_obj(team_a_obj, 'team_b'),
        }
        team_a_tradees_patches = self.transform_tradees(team_a_tradees_obj)
        return [move_transaction] + [dict(**initial_team_a_to_b_trade_object, **patch) for patch in team_a_tradees_patches] + \
               [self.optional_property('additional', self.get_single_and_assert)(analyzed_transaction)]

    def create_sign_transaction(self, action_type='signing', on_roster_after=True, sub_type_a='sign'):
        def to_ret_def(analyzed_sign):
            if 'player' in analyzed_sign or 'player_no_id' in analyzed_sign:
                obj = self.get_single_and_assert(self.get_element_with_no_id_option(analyzed_sign, 'player'))
            elif 'person_with_role' in analyzed_sign:
                pers_obj = self.get_single_and_assert(analyzed_sign['person_with_role'])
                obj = {
                    **self.get_single_and_assert(pers_obj['person_no_id']),
                    'person_role': self.get_single_and_assert(pers_obj['role'])
                }
            else:
                raise Exception('no known signee')
            team_obj = self.destruct_team_obj(self.get_single_and_assert(analyzed_sign['team']))
            return {
                **team_obj,
                **obj,
                'action_type': action_type,
                'sub_type_a': sub_type_a,
                'on_team_a_after': on_roster_after,
            }
        return to_ret_def

    def create_executive_transaction(self, action_type, on_team_after, sub_type_a):
        def to_ret_def(analyzed_sign):
            person_obj = self.get_single_and_assert(self.get_element_with_no_id_option(analyzed_sign, 'person'))
            role = self.get_single_and_assert(analyzed_sign['role'])
            team_obj = self.destruct_team_obj(self.get_single_and_assert(analyzed_sign['team']))
            return {
                **team_obj,
                **person_obj,
                'person_role': role,
                'action_type': action_type,
                'sub_type_a': sub_type_a,
                'on_team_a_after': on_team_after,
            }
        return to_ret_def

    def create_move_transaction(self, action_type, on_team_a_after, sub_type_a):
        def def_to_ret(analyzed_transaction):
            if 'player' in analyzed_transaction or 'player_no_id' in analyzed_transaction:
                obj = self.get_single_and_assert(self.get_element_with_no_id_option(analyzed_transaction, 'player'))
            elif 'person_with_role' in analyzed_transaction:
                pers_obj = self.get_single_and_assert(analyzed_transaction['person_with_role'])
                obj = {
                    **self.get_single_and_assert(pers_obj['person_no_id']),
                    'person_role': self.get_single_and_assert(pers_obj['role'])
                }
            else:
                raise Exception('no known signee')
            team_a_obj = self.destruct_team_obj(self.get_single_and_assert(analyzed_transaction['new_team']))
            team_b_obj = self.destruct_team_obj(self.get_single_and_assert(analyzed_transaction['old_team']), 'team_b')
            return {
                **team_a_obj,
                **team_b_obj,
                **obj,
                'on_team_a_after': on_team_a_after,
                'action_type': action_type,
                'sub_type_a': sub_type_a,
            }
        return def_to_ret

    def create_transaction(self, analyzed_transaction, transaction, transaction_type, season, transaction_year, transaction_month, transaction_day, transaction_number):
        try:
            marking_transaction = create_deep_mraking_dict(analyzed_transaction)
            transformed_transaction = self.create_default_transaction(transaction_year, transaction_month, transaction_day, season, transaction_number, transaction_type)
            transactions_to_ret = [transformed_transaction]
            for transformation in self.transformations_chain[transaction_type]:
                transformations_res = transformation(marking_transaction)
                if isinstance(transformations_res, list):
                    transactions_to_ret = [{**transformed_transaction, **res} for res in transformations_res if res]
                    # after splitting the transactions the chain cant continue for now
                    break
                elif transformations_res:
                    transformed_transaction.update(transformations_res)
            if not marking_transaction.validate():
                raise Exception(f'not all keys used in {marking_transaction}.\nnot used keys: {marking_transaction.not_used_keys()}')
            for t in transactions_to_ret:
                if len(t.keys()) != 32:
                    raise Exception(f'{t}\nhas incorrect key number: {len(t.keys())}')
        except Exception as e:
            print(f'while creating {analyzed_transaction}\n{transaction}')
            raise e
        return transactions_to_ret

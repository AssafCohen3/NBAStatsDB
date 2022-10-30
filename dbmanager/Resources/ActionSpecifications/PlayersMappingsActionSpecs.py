import csv
import datetime
import os.path
from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Errors import InvalidActionCallError
from dbmanager.Resources.ActionSpecifications.ActionInput import FileSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class CompleteMissingPlayersMappings(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayersMappingsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'complete_missing_players_mappings'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.players_mappings.actions.complete_missing_players_mappings.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class ReadPlayersMappingsFromFile(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayersMappingsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        file_path = params['file_path']
        if not file_path.endswith('.csv'):
            raise InvalidActionCallError(cls, params, 'The file for the mappings must be a csv file')
        if not os.path.isfile(file_path):
            raise InvalidActionCallError(cls, params, f'{file_path} does not exist')
        with open(file_path, 'r', encoding='ISO-8859-1') as f:
            csvreader = csv.reader(f, )
            headers = next(csvreader)
            missing_fields = [f for f in
                              ['PlayerBREFId', 'PlayerBREFName', 'PlayerBREFBirthDate', 'PlayerNBAId', 'PlayerNBAName',
                               'PlayerNBABirthDate']
                              if f not in headers]
            if len(missing_fields) > 0:
                raise InvalidActionCallError(cls, params, f'missing the following columns in the file: {", ".join(missing_fields)}')
            bref_id_idx = headers.index('PlayerBREFId')
            bref_name_idx = headers.index('PlayerBREFName')
            bref_birthdate_idx = headers.index('PlayerBREFBirthDate')
            nba_id_idx = headers.index('PlayerNBAId')
            nba_name_idx = headers.index('PlayerNBAName')
            nba_birthdate_idx = headers.index('PlayerNBABirthDate')
            for i, p in enumerate(csvreader):
                if len(p) < 6:
                    raise InvalidActionCallError(cls, params, f'Expecting at least 6 values in line {i + 2} but found only {len(p)}')
                if not p[nba_id_idx]:
                    raise InvalidActionCallError(cls, params, f'The value of PlayerNBAId in line {i + 2} is empty')
                try:
                    int(p[nba_id_idx])
                except ValueError:
                    raise InvalidActionCallError(cls, params, f'The value of PlayerNBAId in line {i + 2} is not a number')

                if not p[nba_name_idx]:
                    raise InvalidActionCallError(cls, params, f'The value of PlayerNBAName in line {i + 2} is empty')

                if p[nba_birthdate_idx]:
                    try:
                        datetime.date.fromisoformat(p[nba_birthdate_idx])
                    except ValueError:
                        raise InvalidActionCallError(cls, params, f'The value of PlayerNBABirthDate in line {i + 2} is not a legal iso date')

                if not p[bref_id_idx]:
                    raise InvalidActionCallError(cls, params, f'The value of PlayerBREFId in line {i + 2} is empty')
                if not p[bref_name_idx]:
                    raise InvalidActionCallError(cls, params, f'The value of PlayerBREFName in line {i + 2} is empty')
                if p[bref_birthdate_idx]:
                    try:
                        datetime.date.fromisoformat(p[bref_birthdate_idx])
                    except ValueError:
                        raise InvalidActionCallError(cls, params, f'The value of PlayerBREFBirthDate in line {i + 2} is not a legal iso date')

    @classmethod
    def get_action_id(cls) -> str:
        return 'read_players_mappings_from_file'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.players_mappings.actions.read_players_mappings_from_file.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            # TODO replace to the main branch when possible
            FileSelector('https://github.com/AssafCohen3/NBAStatsDB/blob/gui-interface/dbmanager/players_ids/players_example.csv')
        ]

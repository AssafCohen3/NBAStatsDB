from typing import List, Type, Tuple, Dict
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.PlayersMappingsActions import CompleteMissingPlayersMappingsAction, \
    ReadPlayersMappingsFromFileAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.PlayersIndex import PlayerDetails, players_index


class PlayersMappingsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return PlayersMappingsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            CompleteMissingPlayersMappingsAction,
            ReadPlayersMappingsFromFileAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        current_mappings_stmt = (
            select(PlayerMapping.PlayerNBAId, PlayerMapping.PlayerBREFId)
        )
        current_mapped_players_list: List[Tuple[int, str]] = session.execute(current_mappings_stmt).fetchall()
        mapped_nba_players: Dict[int, Tuple[int, str]] = {
            r[0]: r for r in current_mapped_players_list
        }
        all_players: Dict[int, PlayerDetails] = players_index.get_data()
        missing_players = 0
        for player in all_players.values():
            if player.player_id not in mapped_nba_players:
                if player.first_season >= 2022 and not player.played_games_flag and player.draft_year is None:
                    # no point at searching new players that hasnt played games
                    # since they wont have reference to stats.nba
                    continue
                missing_players += 1
        mappings_count = len(current_mapped_players_list)
        possible_mappings_count = mappings_count + missing_players
        return [
            ResourceMessage(
                gettext('resources.players_mappings.messages.existing_mappings.title'),
                gettext('resources.players_mappings.messages.existing_mappings.text',
                        mappings_count=mappings_count,
                        possible_mappings_count=possible_mappings_count),
                StatusOption.OK if mappings_count == possible_mappings_count else StatusOption.MISSING,
            )
        ]

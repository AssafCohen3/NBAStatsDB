from sqlalchemy import select

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import Player
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc


class UpdateActivePlayersAwards(ActionSpecificationAbc):

    def validate_request(self, session, params):
        return True, None

    @property
    def action_id(self):
        return 'update_active_players_awards'

    @property
    def action_title(self):
        return gettext('resources.awards.actions.update_active_players_awards.title')

    def get_action_inputs(self, session):
        return []


class UpdateAllPlayersAwards(ActionSpecificationAbc):

    def validate_request(self, session, params):
        return True, None

    @property
    def action_id(self):
        return 'update_all_players_awards'

    @property
    def action_title(self):
        return gettext('resources.awards.actions.update_all_players_awards.title')

    def get_action_inputs(self, session):
        return []


class UpdatePlayerAwards(ActionSpecificationAbc):

    def validate_request(self, session, params):
        if 'player_id' not in params:
            return False, gettext('resources.awards.actions.update_player_awards.player_id_required')
        player_id_stmt = (
                select(Player.PlayerId).
                where(Player.PlayerId == params['player_id'])
        )
        player_id = session.execute(player_id_stmt).fetchall()
        if len(player_id) > 0:
            return True, None
        return False, gettext('resources.awards.actions.update_player_awards.player_id_not_found')

    @property
    def action_id(self):
        return 'update_player_awards'

    @property
    def action_title(self):
        return gettext('resources.awards.actions.update_player_awards.title')

    def get_action_inputs(self, session):
        return [{
            'type': 'PlayerAutoComplete',
            'params': {}
        }]


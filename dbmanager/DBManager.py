from typing import Dict, Type, List, Any, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import create_translatable_from_json, TranslatableField
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFPlayersActions import UpdateBREFPlayersAction
from dbmanager.Resources.Actions.BREFPlayoffSeriesActions import UpdateBREFPlayoffSeriesAction
from dbmanager.Resources.Actions.NBAPlayersActions import UpdateNBAPlayersAction
from dbmanager.Resources.Actions.PlayerBoxScoreActions import UpdatePlayerBoxScoresAction
from dbmanager.Resources.Actions.PlayersMappingsActions import CompleteMissingPlayersMappingsAction
from dbmanager.Resources.Actions.TeamBoxScoreActions import UpdateTeamBoxScoresAction
from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import ActionsGroupPreset, \
    create_actions_group_preset, ActionsGroupPresetObject
from dbmanager.Resources.BREFPlayersResourceHandler import BREFPlayersResourceHandler
from dbmanager.Resources.BREFPlayoffSeriesResourceHandler import BREFPlayoffSeriesResourceHandler
from dbmanager.Resources.BREFStartersResourceHandler import BREFStartersResourceHandler
from dbmanager.Resources.BREFTransactionsResourceHandler import BREFTransactionsResourceHandler
from dbmanager.Resources.EventsResourceHandler import EventsResourceHandler
from dbmanager.Resources.NBAAwardsResourceHandler import NBAAwardsResourceHandler
from dbmanager.Resources.NBAHonoursResourceHandler import NBAHonoursResourceHandler
from dbmanager.Resources.NBAPlayersBirthdateResourceHandler import NBAPlayersBirthdateResourceHandler
from dbmanager.Resources.NBAPlayersResourceHandler import NBAPlayersResourceHandler
from dbmanager.Resources.OddsResourceHandler import OddsResourceHandler
from dbmanager.Resources.PlayerBoxScoreResourceHandler import PlayerBoxScoreResourceHandler
from dbmanager.Resources.PlayerMappingResourceHandler import PlayersMappingsResourceHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from dbmanager.Database.Models.Resource import Resource
from dbmanager.Errors import ResourceNotExistError, PresetNotExistError
from dbmanager.Resources.TeamBoxScoreResourceHandler import TeamBoxScoreResourceHandler
from dbmanager.base import Base
# noinspection PyUnresolvedReferences
import dbmanager.Database.Models
# noinspection PyUnresolvedReferences
import dbmanager.pbp.Patcher
from dbmanager.tasks.TasksGroup import TasksGroup


class DbManager:
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.session: Optional[scoped_session] = None
        self.available_resources: List[Type[ResourceAbc]] = [
            PlayerBoxScoreResourceHandler,
            TeamBoxScoreResourceHandler,
            NBAPlayersResourceHandler,
            BREFPlayoffSeriesResourceHandler,
            PlayersMappingsResourceHandler,
            BREFPlayersResourceHandler,
            NBAAwardsResourceHandler,
            EventsResourceHandler,
            NBAHonoursResourceHandler,
            OddsResourceHandler,
            BREFStartersResourceHandler,
            NBAPlayersBirthdateResourceHandler,
            BREFTransactionsResourceHandler,
        ]
        self.resources: Dict[str, Type[ResourceAbc]] = {
            res.get_id(): res for res in self.available_resources
        }

    def init(self, engine: Engine, session: scoped_session):
        self.engine = engine
        self.session = session
        Base.metadata.create_all(self.engine)
        to_add = [{
            'ResourceId': res.get_id(),
            'LastUpdated': None
        } for res in self.available_resources]
        stmt = insert(Resource).on_conflict_do_nothing()
        self.session.execute(stmt, to_add)
        self.session.commit()

    def load_presets(self) -> Dict[int, ActionsGroupPresetObject]:
        available_actions_presets: Dict[int, ActionsGroupPresetObject] = {
            -1: create_actions_group_preset(-1, TranslatableField({'en': 'Basic Update', 'he': 'עדכון בסיסי'}),
                                            [
                                                (UpdateNBAPlayersAction, {}),
                                                (UpdateTeamBoxScoresAction, {'season_type_code': '0'}),
                                                (UpdatePlayerBoxScoresAction, {'season_type_code': '0'}),
                                                (UpdateBREFPlayoffSeriesAction, {}),
                                                (CompleteMissingPlayersMappingsAction, {}),
                                                (UpdateBREFPlayersAction, {})
                                            ]),
            0: create_actions_group_preset(0, TranslatableField({'en': 'Update Boxscores', 'he': 'עדכן בוקססקורס'}),
                                           [
                                               (UpdateNBAPlayersAction, {}),
                                               (UpdateTeamBoxScoresAction, {'season_type_code': '0'}),
                                               (UpdatePlayerBoxScoresAction, {'season_type_code': '0'}),
                                           ]),
        }
        stmt = select(ActionsGroupPreset)
        presets: List[Tuple[ActionsGroupPreset]] = self.session.execute(stmt).fetchall()
        presets_models: List[ActionsGroupPreset] = [p[0] for p in presets]
        for preset_row in presets_models:
            preset_actions: List[Tuple[Type[ActionAbc], Dict[str, str]]] = []
            for action_recipe in preset_row.action_recipets:
                action_cls = self.get_resource(action_recipe.ResourceId).get_action_cls(action_recipe.ActionId)
                params = {param.ParamKey: param.ParamValue for param in action_recipe.action_params}
                preset_actions.append((action_cls, params))
            available_actions_presets[preset_row.ActionsGroupPresetId] = create_actions_group_preset(preset_row.ActionsGroupPresetId, create_translatable_from_json(preset_row.PresetTranslatableNameJson), preset_actions)
        return available_actions_presets

    def get_resource(self, resource_id: str) -> Type[ResourceAbc]:
        if resource_id not in self.resources:
            raise ResourceNotExistError(resource_id)
        return self.resources[resource_id]

    def dispatch_action(self, resource_id: str, action_id: str, params: Dict[str, str]) -> ActionAbc:
        resource = self.get_resource(resource_id)
        action_to_run = resource.create_action(self.session, action_id, params)
        return action_to_run

    def get_resources_list_compact(self) -> List[Dict[str, Any]]:
        available_ids = [res.get_id() for res in self.available_resources]
        stmt = (
            select(Resource.ResourceId, Resource.LastUpdated).
            where(Resource.ResourceId.in_(available_ids))
        )
        resources = self.session.execute(stmt).fetchall()
        resources = [{
            'resource_id': resource_id,
            'last_updated': last_updated,
            'resource_name': self.get_resource(resource_id).get_name(),
            # TODO add or not
            # 'messages': self.get_resource(resource_id).get_messages(self.session)
        } for resource_id, last_updated in resources]
        return resources

    def get_resource_details(self, resource_id: str) -> Dict[str, Any]:
        resource = self.get_resource(resource_id)
        to_ret = {
            'resource_id': resource.get_id(),
            'last_updated': resource.get_last_updated(self.session),
            'resource_name': resource.get_name(),
            'messages': resource.get_messages(self.session),
            'actions_specs': list(map(lambda spec: spec.to_dict(self.session), resource.get_actions_specs())),
            'related_tables': resource.get_related_tables(),
            'depend_on_resources': list(map(lambda d: {
                'resource_id': d.get_id(),
                'resource_name': d.get_name()
            }, resource.get_dependencies()))
        }
        return to_ret

    def get_actions_presets_list(self) -> List[Dict]:
        to_ret = [
            {
                'preset_id': actions_preset.preset_id,
                'preset_name': actions_preset.preset_name.get_value(),
            }
            for actions_preset in self.load_presets().values()
        ]
        return to_ret

    def get_actions_preset_details(self, preset_id: int) -> Dict:
        presets = self.load_presets()
        if preset_id not in presets:
            raise PresetNotExistError(preset_id)
        preset = presets[preset_id]
        to_ret = {
            'preset_id': preset.preset_id,
            'preset_name': preset.preset_name.get_value(),
            'action_recipes': [recipe.to_dict() for recipe in preset.action_recipes]
        }
        return to_ret

    def dispatch_preset(self, preset_id: int) -> TasksGroup:
        presets = self.load_presets()
        if preset_id not in presets:
            raise PresetNotExistError(preset_id)
        preset: ActionsGroupPresetObject = presets[preset_id]
        actions_to_dispatch: List[ActionAbc] = [action_recipe.action_cls.create_action_from_request(self.session, action_recipe.params)
                                                for action_recipe in sorted(preset.action_recipes, key=lambda p: p.order)]
        return TasksGroup(f'preset_{preset.preset_id}', preset.preset_name, actions_to_dispatch)

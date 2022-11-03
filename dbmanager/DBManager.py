import sqlite3
from typing import Dict, Type, List, Any, Optional, Tuple

import sqlalchemy.exc
from sqlalchemy import select, insert
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import create_translatable_from_json, TranslatableFieldFromAction
from dbmanager.Database.Models.ActionsGroupPreset import ActionsGroupPreset
from dbmanager.PresetsManager import PresetsManager
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionDependency
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFPlayersActions import UpdateBREFPlayersAction
from dbmanager.Resources.Actions.BREFPlayoffSeriesActions import UpdateBREFPlayoffSeriesAction
from dbmanager.Resources.Actions.NBAPlayersActions import UpdateNBAPlayersAction
from dbmanager.Resources.Actions.PlayerBoxScoreActions import UpdatePlayerBoxScoresAction
from dbmanager.Resources.Actions.PlayersMappingsActions import CompleteMissingPlayersMappingsAction
from dbmanager.Resources.Actions.TeamBoxScoreActions import UpdateTeamBoxScoresAction
from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import create_actions_group_preset, ActionsGroupPresetObject
from dbmanager.Resources.BREFAwardsResourceHandler import BREFAwardsResourceHandler
from dbmanager.Resources.BREFPlayersResourceHandler import BREFPlayersResourceHandler
from dbmanager.Resources.BREFPlayoffSeriesResourceHandler import BREFPlayoffSeriesResourceHandler
from dbmanager.Resources.BREFStartersResourceHandler import BREFStartersResourceHandler
from dbmanager.Resources.BREFTransactionsResourceHandler import BREFTransactionsResourceHandler
from dbmanager.Resources.PBPEventsResourceHandler import PBPEventsResourceHandler
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
from dbmanager.SharedData.CachedData import CachedData
from dbmanager.base import MyModel
# noinspection PyUnresolvedReferences
import dbmanager.Database.Models
# noinspection PyUnresolvedReferences
import dbmanager.pbp.Patcher
from dbmanager.tasks.TaskAbc import TaskAbc
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
            PBPEventsResourceHandler,
            NBAHonoursResourceHandler,
            OddsResourceHandler,
            BREFStartersResourceHandler,
            NBAPlayersBirthdateResourceHandler,
            BREFTransactionsResourceHandler,
            BREFAwardsResourceHandler,
        ]
        self.resources: Dict[str, Type[ResourceAbc]] = {
            res.get_id(): res for res in self.available_resources
        }
        self.cached_presets = CachedData(self._load_presets)
        self.presets_manager: Optional[PresetsManager] = None

    def init(self, engine: Engine, session: scoped_session):
        try:
            self.engine = engine
            self.session = session
            MyModel.metadata.create_all(self.engine)
            to_add = [{
                'ResourceId': res.get_id(),
                'LastUpdated': None
            } for res in self.available_resources]
            stmt = insert(Resource).on_conflict_do_nothing()
            self.session.execute(stmt, to_add)
            self.session.commit()
            self.presets_manager = PresetsManager(self.session, self.cached_presets)
            self.create_default_presets()
        except (sqlite3.OperationalError, sqlalchemy.exc.OperationalError) as e:
            self.session.rollback()
            self.session.close()
            self.engine.dispose()
            self.engine = None
            self.session = None
            self.presets_manager = None
            raise e

    def is_initiated(self):
        return self.session is not None

    def create_default_presets(self):
        default_presets: List[Tuple[str, Dict[str, str], List[Tuple[Type[ActionAbc], Dict[str, str]]]]] = [
            ('default_base_update', {'en': 'Basic Update', 'he': 'עדכון בסיסי'},
                [
                    (UpdateNBAPlayersAction, {}),
                    (UpdateTeamBoxScoresAction, {'season_type_code': '0'}),
                    (UpdatePlayerBoxScoresAction, {'season_type_code': '0'}),
                    (UpdateBREFPlayoffSeriesAction, {}),
                    (CompleteMissingPlayersMappingsAction, {}),
                    (UpdateBREFPlayersAction, {})
                ]
             ),
            ('default_update_boxscore', {'en': 'Update Boxscores', 'he': 'עדכן בוקססקורס'},
             [
                 (UpdateNBAPlayersAction, {}),
                 (UpdateTeamBoxScoresAction, {'season_type_code': '0'}),
                 (UpdatePlayerBoxScoresAction, {'season_type_code': '0'}),
             ]
             ),
        ]
        for preset_id, preset_name, actions_cls in default_presets:
            if preset_id in self.presets_manager.get_presets():
                continue
            self.presets_manager.create_preset(preset_id, preset_name)
            for i, (action_cls, params) in enumerate(actions_cls):
                self.presets_manager.create_action_recipe(preset_id, action_cls, i, params)

    def _load_presets(self) -> Dict[str, ActionsGroupPresetObject]:
        available_actions_presets: Dict[str, ActionsGroupPresetObject] = {}
        stmt = select(ActionsGroupPreset)
        presets: List[Tuple[ActionsGroupPreset]] = self.session.execute(stmt).fetchall()
        presets_models: List[ActionsGroupPreset] = [p[0] for p in presets]
        for preset_row in presets_models:
            preset_actions: List[Tuple[int, Type[ActionAbc], int, Dict[str, str]]] = []
            for action_recipe in preset_row.action_recipets:
                action_cls = self.get_resource(action_recipe.ResourceId).get_action_cls(action_recipe.ActionId)
                params = {param.ParamKey: param.ParamValue for param in action_recipe.action_params}
                preset_actions.append((action_recipe.ActionRecipeId, action_cls, action_recipe.Order, params))
            available_actions_presets[preset_row.ActionsGroupPresetId] = create_actions_group_preset(preset_row.ActionsGroupPresetId, create_translatable_from_json(preset_row.PresetTranslatableNameJson), preset_actions)
        return available_actions_presets

    def get_resource(self, resource_id: str) -> Type[ResourceAbc]:
        if resource_id not in self.resources:
            raise ResourceNotExistError(resource_id)
        return self.resources[resource_id]

    def dispatch_action(self, resource_id: str, action_id: str, params: Dict[str, str], download_dependencies: bool) -> TaskAbc:
        resource = self.get_resource(resource_id)
        action_to_run = resource.create_action(self.session, action_id, params)
        to_ret = action_to_run
        if download_dependencies:
            depends_on_actions: List[TaskAbc] = []
            all_dependencies: List[ActionDependency] = action_to_run.get_action_spec().get_action_dependencies_nested(
                action_to_run.get_action_spec().parse_params(self.session, params)
            )
            for depends_on_action in all_dependencies:
                dependent_spec = depends_on_action.dependent_action_spec
                resource = self.get_resource(dependent_spec.get_resource().get_id())
                dependent_action_to_run = resource.get_action_cls(dependent_spec.get_action_id()).\
                    create_action_from_parsed_params(self.session, depends_on_action.parsed_params)
                depends_on_actions.append(dependent_action_to_run)
            to_ret = TasksGroup(f'action_with_dep-{action_id}', TranslatableFieldFromAction(action_to_run.get_action_spec()),
                                [*depends_on_actions, to_ret])

        return to_ret

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

    def get_resources_with_actions_compact(self) -> List[Dict[str, Any]]:
        available_ids = [res.get_id() for res in self.available_resources]
        stmt = (
            select(Resource.ResourceId, Resource.LastUpdated).
            where(Resource.ResourceId.in_(available_ids))
        )
        resources_last_update = self.session.execute(stmt).fetchall()
        resources_with_actions = [{
            'resource_id': (resource := self.get_resource(resource_id)).get_id(),
            'resource_name': resource.get_name(),
            'actions': [act.to_compact_dict() for act in resource.get_actions_specs()],
            'last_updated': last_updated
        } for resource_id, last_updated in resources_last_update]
        return resources_with_actions

    def get_resource_details(self, resource_id: str) -> Dict[str, Any]:
        resource = self.get_resource(resource_id)
        to_ret = {
            'resource_id': resource.get_id(),
            'last_updated': resource.get_last_updated(self.session),
            'resource_name': resource.get_name(),
            'description': resource.get_resource_spec().get_description(),
            'messages': resource.get_messages(self.session),
            'actions_specs': list(map(lambda spec: spec.to_dict(self.session), resource.get_actions_specs())),
            'related_tables': [{'name': rt.__name__} for rt in resource.get_related_tables()],
            'depend_on_resources': list(map(lambda d: {
                'resource_id': d.get_id(),
                'resource_name': d.get_name()
            }, resource.get_dependencies()))
        }
        return to_ret

    def get_action_spec(self, resource_id: str, action_id: str):
        resource = self.get_resource(resource_id)
        action = resource.get_action_cls(action_id)
        return action.get_action_spec().to_dict(self.session)

    def get_actions_presets_list(self) -> List[Dict]:
        return self.presets_manager.get_actions_presets_list()

    def get_actions_preset_details(self, preset_id: str) -> Dict:
        return self.presets_manager.get_actions_preset_details(preset_id)

    def get_extended_actions_presets_list(self) -> List[Dict]:
        return self.presets_manager.get_extended_actions_presets_list()

    def create_preset(self, preset_id: str, preset_name_json: Dict[str, str]) -> str:
        return self.presets_manager.create_preset(preset_id, preset_name_json)

    def edit_preset(self, preset_id: str, preset_name_json: Dict[str, str]) -> str:
        return self.presets_manager.edit_preset(preset_id, preset_name_json)

    def remove_preset(self, preset_id: str) -> str:
        return self.presets_manager.remove_preset(preset_id)

    def create_action_recipe(self, preset_id: str, resource_id: str, action_id: str, order: int, params: Dict[str, str]) -> int:
        action_cls = self.get_resource(resource_id).get_action_cls(action_id)
        return self.presets_manager.create_action_recipe(preset_id, action_cls, order, params)

    def edit_action_recipe_params(self, preset_id: str, recipe_id: int, params: Dict[str, str]) -> int:
        return self.presets_manager.edit_action_recipe_params(preset_id, recipe_id, params)

    def change_action_recipe_order(self, preset_id: str, recipe_id: int, new_order: int) -> int:
        return self.presets_manager.change_action_recipe_order(preset_id, recipe_id, new_order)

    def delete_action_recipe(self, preset_id: str, recipe_id: int) -> int:
        return self.presets_manager.delete_action_recipe(preset_id, recipe_id)

    def copy_action_recipe(self, preset_id: str, recipe_id: int, new_preset_id: str, order_in_new_preset: int) -> int:
        return self.presets_manager.copy_action_recipe(preset_id, recipe_id, new_preset_id, order_in_new_preset)

    def dispatch_preset(self, preset_id: str) -> TasksGroup:
        presets = self.cached_presets.get_data()
        if preset_id not in presets:
            raise PresetNotExistError(preset_id)
        preset: ActionsGroupPresetObject = presets[preset_id]
        actions_to_dispatch: List[ActionAbc] = [action_recipe.action_cls.create_action_from_request(self.session, action_recipe.params)
                                                for action_recipe in sorted(preset.action_recipes.values(), key=lambda p: p.order)]
        return TasksGroup(f'preset_{preset.preset_id}', preset.preset_name, actions_to_dispatch)

from typing import Dict, Type, List, Any, Optional
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session

from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.BREFPlayersResourceHandler import BREFPlayersResourceHandler
from dbmanager.Resources.BREFPlayoffSeriesResourceHandler import BREFPlayoffSeriesResourceHandler
from dbmanager.Resources.NBAPlayersResourceHandler import NBAPlayersResourceHandler
from dbmanager.Resources.PlayerBoxScoreResourceHandler import PlayerBoxScoreResourceHandler
from dbmanager.Resources.PlayerMappingResourceHandler import PlayersMappingsResourceHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from dbmanager.Database.Models.Resource import Resource
from dbmanager.Errors import ResourceNotExistError
from dbmanager.Resources.TeamBoxScoreResourceHandler import TeamBoxScoreResourceHandler
from dbmanager.base import Base
# noinspection PyUnresolvedReferences
import dbmanager.Database.Models
# noinspection PyUnresolvedReferences
import dbmanager.pbp.Patcher


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

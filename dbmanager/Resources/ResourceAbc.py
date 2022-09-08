import abc
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from dbmanager.Database.Models.Resource import Resource
from dbmanager.Errors import ActionNotExistError
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


@dataclass
class ResourceMessage:
    title: str
    text: str
    status: str


class ResourceAbc(ABC):

    # disgusting extraction of the resource details to a class to allow to reference it from action to prevent circular import
    @classmethod
    @abstractmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        pass

    @classmethod
    def get_id(cls):
        return cls.get_resource_spec().get_id()

    @classmethod
    def get_name(cls):
        return cls.get_resource_spec().get_name()

    @classmethod
    def get_dependencies(cls):
        return cls.get_resource_spec().get_dependencies()

    @classmethod
    def get_related_tables(cls):
        return cls.get_resource_spec().get_related_tables()

    @classmethod
    @abstractmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        """
        get the resource actions
        """

    @classmethod
    def get_actions_specs(cls) -> List[Type[ActionSpecificationAbc]]:
        return list(map(lambda act: act.get_action_spec(), cls.get_actions()))

    @classmethod
    def get_action_cls(cls, action_id: str) -> Type[ActionAbc]:
        actions = [act for act in cls.get_actions() if act.get_action_spec().get_action_id() == action_id]
        if len(actions) == 0:
            raise ActionNotExistError(cls.get_id(), action_id)
        return actions[0]

    @classmethod
    def validate_request(cls, session: scoped_session, action_id: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        validate the params and returns the parsed params
        """
        action_cls = cls.get_action_cls(action_id)
        return action_cls.get_action_spec().validate_request(session, params)

    @classmethod
    def create_action(cls, session: scoped_session, action_id: str, params: Dict[str, str]) -> ActionAbc:
        parsed_params = cls.validate_request(session, action_id, params)
        return cls.get_action_cls(action_id).create_action_from_params(session, parsed_params)

    @classmethod
    @abc.abstractmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        """
        Get messages describing the status of the resource
        message has title(translateable), text(translateable) and status
        """

    @classmethod
    def get_last_updated(cls, session: scoped_session) -> Optional[datetime.date]:
        stmt = (
            select(Resource.LastUpdated).
            where(Resource.ResourceId == cls.get_id())
        )
        results = session.execute(stmt).fetchall()
        if len(results) == 0:
            return None
        return results[0][0]

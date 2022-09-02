import abc
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Type, Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from dbmanager.Database.Models.Resource import Resource
from dbmanager.Errors import ActionNotExistError
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.Actions.ActionAbc import ActionAbc


@dataclass
class ResourceMessage:
    title: str
    text: str
    status: str


@dataclass
class RelatedTable:
    name: str


class ResourceAbc(ABC):

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
    @abstractmethod
    def get_id(cls) -> str:
        """
        get the resource id
        """

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """
        get the resource name
        """

    @classmethod
    @abc.abstractmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        """
        Get messages describing the status of the resource
        message has title(translateable), text(translateable) and status
        """

    @classmethod
    @abc.abstractmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        """
        Get related tables.
        """

    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> List[Type['ResourceAbc']]:
        """
        Get resources that the resource depends on.
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

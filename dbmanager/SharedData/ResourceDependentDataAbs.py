import datetime
from abc import ABC, abstractmethod
from threading import Lock
from typing import List, Dict, Optional, Type, Tuple, TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from dbmanager.Database.Models.Resource import Resource
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


T = TypeVar('T')


class ResourceDependentDataAbs(ABC, Generic[T]):
    def __init__(self):
        self._lock = Lock()
        self.data: Optional[T] = None
        self.last_updated: Dict[str, Optional[float]] = {
            resource.get_id(): None
            for resource in self.get_resource_dependent_list()
        }

    @abstractmethod
    def get_resource_dependent_list(self) -> List[Type[ResourceSpecificationAbc]]:
        pass

    def to_refresh(self, session: scoped_session) -> bool:
        if self.data is None:
            return True
        last_updates_stmt = (
            select(Resource.ResourceId, Resource.LastUpdated).
            where(Resource.ResourceId.in_(list(map(lambda r: r.get_id(), self.get_resource_dependent_list()))))
        )
        last_updates: List[Tuple[str, datetime.datetime]] = session.execute(last_updates_stmt).fetchall()
        for resource_id, resource_last_update in last_updates:
            if self.last_updated[resource_id] != resource_last_update.timestamp():
                return True
        return False

    def get_data(self, session: scoped_session) -> T:
        with self._lock:
            if self.to_refresh(session):
                self.data = self._fetch_data(session)
                last_updates_stmt = (
                    select(Resource.ResourceId, Resource.LastUpdated).
                    where(Resource.ResourceId.in_(list(map(lambda r: r.get_id(), self.get_resource_dependent_list()))))
                )
                last_updates: List[Tuple[str, datetime.datetime]] = session.execute(last_updates_stmt).fetchall()
                for resource_id, resource_last_update in last_updates:
                    self.last_updated[resource_id] = resource_last_update.timestamp()
        return self.data

    @abstractmethod
    def _fetch_data(self, session: scoped_session) -> T:
        pass

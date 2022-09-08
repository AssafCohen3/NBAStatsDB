from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Type


@dataclass
class RelatedTable:
    name: str


class ResourceSpecificationAbc(ABC):
    @classmethod
    @abstractmethod
    def get_id(cls) -> str:
        """
        get the resource id
        """

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """
        get the resource name
        """

    @classmethod
    @abstractmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        """
        Get related tables.
        """

    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        """
        Get resources that the resource depends on.
        """

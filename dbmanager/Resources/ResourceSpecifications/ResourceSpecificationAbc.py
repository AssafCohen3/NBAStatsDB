from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Type

from dbmanager.base import MyModel


@dataclass
class Source:
    site: str
    example_link: str


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
    def get_related_tables(cls) -> List[Type[MyModel]]:
        """
        Get related tables.
        """

    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        """
        Get resources that the resource depends on.
        """

    @classmethod
    @abstractmethod
    def get_source(cls) -> Source:
        """
        get the resource source
        """

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """
        get the resource description
        """

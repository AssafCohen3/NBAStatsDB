from sqlalchemy import Column, DateTime
from sqlalchemy import Text
from dbmanager.base import Base


class Resource(Base):
    __tablename__ = 'Resource'
    ResourceId = Column(Text, primary_key=True)
    LastUpdated = Column(DateTime)

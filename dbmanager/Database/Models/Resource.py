from sqlalchemy import Column, Computed, DateTime
from sqlalchemy import Integer, Text, Date
from dbmanager.base import Base


class Resource(Base):
    __tablename__ = 'Resource'
    ResourceId = Column(Text, primary_key=True)
    LastUpdated = Column(DateTime)

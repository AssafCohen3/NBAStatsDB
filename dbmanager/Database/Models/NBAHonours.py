from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text

from dbmanager.base import Base


class NBAHonours(Base):
    __tablename__ = 'NBAHonours'
    PlayerId = Column(Integer)
    FullName = Column(Text)
    Jersey = Column(Text)
    Position = Column(Text)
    TeamId = Column(Integer)
    Description = Column(Text)
    Season = Column(Integer)
    HonourType = Column(Text)
    __table_args__ = (
        PrimaryKeyConstraint('PlayerId', 'FullName', 'TeamId', 'Season', 'Description', 'Jersey', 'Position'),
    )

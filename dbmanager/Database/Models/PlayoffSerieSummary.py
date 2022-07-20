from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text
from dbmanager.base import Base


class PlayoffSerieSummary(Base):
    __tablename__ = 'PlayoffSerieSummary'
    Season = Column(Integer)
    TeamAId = Column(Integer)
    TeamAName = Column(Text)
    TeamBId = Column(Integer)
    TeamBName = Column(Text)
    TeamAWins = Column(Integer)
    TeamBWins = Column(Integer)
    WinnerId = Column(Integer)
    WinnerName = Column(Text)
    LoserId = Column(Integer)
    LoserName = Column(Text)
    SerieOrder = Column(Integer)
    LevelTitle = Column(Text)
    __table_args__ = (
        PrimaryKeyConstraint('Season', 'TeamAId', 'TeamBId'),
    )

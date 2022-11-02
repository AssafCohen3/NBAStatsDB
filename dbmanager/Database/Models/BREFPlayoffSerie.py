from sqlalchemy import Column, PrimaryKeyConstraint, Date
from sqlalchemy import Integer, Text
from dbmanager.base import MyModel


class BREFPlayoffSerie(MyModel):
    __tablename__ = 'BREFPlayoffSerie'
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
    SerieStartDate = Column(Date)
    SerieEndDate = Column(Date)
    IsOver = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('Season', 'TeamAId', 'TeamBId'),
    )

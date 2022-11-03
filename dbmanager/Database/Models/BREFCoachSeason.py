from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text

from dbmanager.base import MyModel


class BREFCoachSeason(MyModel):
    __tablename__ = 'BREFCoachSeason'
    CoachId = Column(Text)
    CoachName = Column(Text, nullable=False)
    TeamId = Column(Integer, nullable=False)
    TeamName = Column(Text, nullable=False)
    Season = Column(Integer)
    FromGameNumber = Column(Integer)
    ToGameNumber = Column(Integer)
    RegularSeasonGamesCount = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('CoachId', 'Season', 'FromGameNumber'),
    )

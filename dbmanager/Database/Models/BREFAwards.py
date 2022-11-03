from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text, Date

from dbmanager.base import MyModel


class BREFAwards(MyModel):
    __tablename__ = 'BREFAwards'
    PersonId = Column(Text)
    PersonName = Column(Text)
    PersonType = Column(Text)
    TeamId = Column(Integer)
    TeamName = Column(Text)
    AwardId = Column(Text)
    AwardName = Column(Text)
    AllNBATeamNumber = Column(Integer)
    Season = Column(Integer)
    DateAwarded = Column(Date)
    Conference = Column(Text)
    __table_args__ = (
        PrimaryKeyConstraint('PersonId', 'AwardId', 'Season', 'DateAwarded'),
    )

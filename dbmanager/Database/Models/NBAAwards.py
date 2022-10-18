from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text, Date

from dbmanager.base import Base


class NBAAwards(Base):
    __tablename__ = 'NBAAwards'
    PlayerId = Column(Integer)
    FullName = Column(Text)
    TeamId = Column(Integer)
    TeamName = Column(Text)
    Description = Column(Text)
    AllNBATeamNumber = Column(Integer)
    Season = Column(Integer)
    DateAwarded = Column(Date)
    Confrence = Column(Text)
    AwardType = Column(Text)
    SubTypeA = Column(Text)
    SubTypeB = Column(Text)
    SubTypeC = Column(Text)
    __table_args__ = (
        PrimaryKeyConstraint('PlayerId', 'FullName', 'TeamId', 'Season', 'Description', 'DateAwarded'),
    )

from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text, Float

from dbmanager.base import MyModel


class Odds(MyModel):
    __tablename__ = 'Odds'
    TeamId = Column(Integer)
    TeamName = Column(Text)
    Odd = Column(Float)
    Round = Column(Integer)
    Season = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('Season', 'Round', 'TeamId'),
    )

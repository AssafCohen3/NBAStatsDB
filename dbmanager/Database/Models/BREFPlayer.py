from sqlalchemy import Column
from sqlalchemy import Integer, Text, Date, Float
from dbmanager.base import MyModel


class BREFPlayer(MyModel):
    __tablename__ = 'BREFPlayer'
    PlayerId = Column(Text, primary_key=True)
    PlayerName = Column(Text)
    FromYear = Column(Integer)
    ToYear = Column(Integer)
    Position = Column(Text)
    Height = Column(Float)
    Weight = Column(Integer)
    Birthdate = Column(Date)
    Active = Column(Integer)
    HOF = Column(Integer)

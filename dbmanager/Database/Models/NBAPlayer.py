from sqlalchemy import Column
from sqlalchemy import Integer, Text, Date
from dbmanager.base import MyModel


class NBAPlayer(MyModel):
    __tablename__ = 'NBAPlayer'
    PlayerId = Column(Integer, primary_key=True)
    FirstName = Column(Text)
    LastName = Column(Text)
    PlayerSlug = Column(Text)
    Active = Column(Integer)
    Position = Column(Text)
    Height = Column(Text)
    Weight = Column(Text)
    College = Column(Text)
    Country = Column(Text)
    DraftYear = Column(Integer)
    DraftRound = Column(Integer)
    DraftNumber = Column(Integer)
    FirstSeason = Column(Integer)
    BirthDate = Column(Date)

from sqlalchemy import Column, Computed
from sqlalchemy import Integer, Text, Date
from dbmanager.base import Base


class Player(Base):
    __tablename__ = 'Player'
    PlayerId = Column(Integer, primary_key=True)
    FirstName = Column(Text)
    LastName = Column(Text)
    FullName = Column(Text, Computed("FirstName || ' ' || LastName", persisted=False))
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
    BirthDate = Column(Date)
    UpdatedAtSeason = Column(Integer)

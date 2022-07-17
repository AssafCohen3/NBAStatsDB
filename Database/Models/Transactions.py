from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text
from base import Base


class Transactions(Base):
    __tablename__ = 'Transactions'
    Season = Column(Integer, nullable=False)
    Year = Column(Integer, nullable=False)
    Month = Column(Integer, nullable=False)
    Day = Column(Integer, nullable=False)
    TransactionNumber = Column(Integer, nullable=False)
    TeamANBAId = Column(Integer, nullable=False)
    TeamANBAName = Column(Text)
    TeamABREFAbbr = Column(Text, nullable=False)
    TeamABREFName = Column(Text, nullable=False)
    TeamBNBAId = Column(Integer, nullable=False)
    TeamBNBAName = Column(Text)
    TeamBBREFAbbr = Column(Text, nullable=False)
    TeamBBREFName = Column(Text, nullable=False)
    PlayerNBAId = Column(Integer, nullable=False)
    PlayerNBAName = Column(Text)
    PlayerBREFId = Column(Text, nullable=False)
    PlayerBREFName = Column(Text, nullable=False)
    PersonBREFId = Column(Text, nullable=False)
    PersonBREFName = Column(Text, nullable=False)
    PersonRole = Column(Text)
    TransactionType = Column(Text, nullable=False)
    ActionType = Column(Text, nullable=False)
    SubTypeA = Column(Text, nullable=False)
    SubTypeB = Column(Text)
    SubTypeC = Column(Text)
    OnTeamAAfter = Column(Integer, nullable=False)
    OnTeamBAfter = Column(Integer, nullable=False)
    PickYear = Column(Integer, nullable=False)
    PickRound = Column(Integer, nullable=False)
    PicksNumber = Column(Integer, nullable=False)
    TradeeType = Column(Text, nullable=False)
    Additional = Column(Text, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('Season', 'Year', 'Month', 'Day', 'TransactionNumber', 'TeamABREFAbbr', 'TeamBBREFAbbr', 'PlayerBREFId', 'PlayerBREFName',
                             'PersonBREFId', 'PersonBREFName', 'TransactionType', 'PickYear', 'PickRound', 'TradeeType', 'Additional'),
    )

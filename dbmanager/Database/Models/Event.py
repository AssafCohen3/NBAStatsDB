from sqlalchemy import Column, PrimaryKeyConstraint
from sqlalchemy import Integer, Text, Float
from dbmanager.base import Base


class Event(Base):
    __tablename__ = 'Event'
    Season = Column(Integer)
    SeasonType = Column(Text)
    GameId = Column(Text)
    TeamAId = Column(Integer)
    TeamAName = Column(Text)
    TeamBId = Column(Integer)
    TeamBName = Column(Text)
    EventNumber = Column(Integer)
    EventType = Column(Integer)
    EventActionType = Column(Integer)
    Period = Column(Integer)
    RealTime = Column(Text)
    Clock = Column(Text)
    RemainingSeconds = Column(Float)
    Description = Column(Text)
    TeamAScore = Column(Integer)
    TeamBScore = Column(Integer)
    ScoreMargin = Column(Integer)
    ShotValue = Column(Float)
    PersonAType = Column(Integer)
    PlayerAId = Column(Integer)
    PlayerATeamId = Column(Integer)
    PersonBType = Column(Integer)
    PlayerBId = Column(Integer)
    PlayerBTeamId = Column(Integer)
    PersonCType = Column(Integer)
    PlayerCId = Column(Integer)
    PlayerCTeamId = Column(Integer)
    VideoAvailable = Column(Integer)
    CountAsPossession = Column(Integer)
    IsPossessionEndingEvent = Column(Integer)
    SecondsSincePreviousEvent = Column(Float)
    TeamALineupIds = Column(Text)
    TeamBLineupIds = Column(Text)
    TeamAFoulsToGive = Column(Integer)
    TeamBFoulsToGive = Column(Integer)
    PreviousEventNumber = Column(Integer)
    NextEventNumber = Column(Integer)
    EventOrder = Column(Integer)
    RealPossesionNumber = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('GameId', 'EventNumber'),
    )

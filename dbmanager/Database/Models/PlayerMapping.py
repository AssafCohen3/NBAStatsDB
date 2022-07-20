from sqlalchemy import Column
from sqlalchemy import Integer, Text, Date
from dbmanager.base import Base


class PlayerMapping(Base):
    __tablename__ = 'PlayerMapping'
    PlayerNBAId = Column(Integer, primary_key=True)
    PlayerNBAName = Column(Text)
    PlayerNBABirthDate = Column(Date)
    PlayerBREFId = Column(Text)
    PlayerBREFName = Column(Text)
    PlayerBREFBirthDate = Column(Date)

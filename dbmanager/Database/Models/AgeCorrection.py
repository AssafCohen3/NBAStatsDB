from sqlalchemy import Column
from sqlalchemy import Integer, Date
from dbmanager.base import Base


class AgeCorrection(Base):
    __tablename__ = 'AgeCorrection'
    PlayerId = Column(Integer, primary_key=True)
    RealBirthDate = Column(Date)

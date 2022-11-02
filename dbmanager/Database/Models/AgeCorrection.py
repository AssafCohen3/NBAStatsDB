from sqlalchemy import Column
from sqlalchemy import Integer, Date
from dbmanager.base import MyModel


class AgeCorrection(MyModel):
    __tablename__ = 'AgeCorrection'
    PlayerId = Column(Integer, primary_key=True)
    RealBirthDate = Column(Date)

from typing import List

from sqlalchemy import Column
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship

from dbmanager.Database.Models.ActionRecipe import ActionRecipe
from dbmanager.base import Base


class ActionsGroupPreset(Base):
    __tablename__ = 'ActionsGroupPreset'
    ActionsGroupPresetId = Column(Integer, primary_key=True)
    PresetTranslatableNameJson = Column(Text)
    action_recipets: List[ActionRecipe] = relationship('ActionRecipe', order_by='ActionRecipe.Order')
    __table_args__ = {'sqlite_autoincrement': True}

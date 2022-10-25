from typing import List

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship

from dbmanager.Database.Models.ActionRecipeParam import ActionRecipeParam
from dbmanager.base import Base


class ActionRecipe(Base):
    __tablename__ = 'ActionRecipe'
    ActionRecipeId = Column(Integer, primary_key=True)
    ActionsGroupPresetId = Column(Integer, ForeignKey('ActionsGroupPreset.ActionsGroupPresetId'))
    ResourceId = Column(Text)
    ActionId = Column(Text)
    Order = Column(Integer)
    action_params: List[ActionRecipeParam] = relationship('ActionRecipeParam')
    __table_args__ = {'sqlite_autoincrement': True}

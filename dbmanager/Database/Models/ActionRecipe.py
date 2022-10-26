from typing import List

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Text
from sqlalchemy.orm import relationship

from dbmanager.Database.Models.ActionRecipeParam import ActionRecipeParam
from dbmanager.base import Base


class ActionRecipe(Base):
    __tablename__ = 'ActionRecipe'
    ActionRecipeId = Column(Integer, primary_key=True)
    ActionsGroupPresetId = Column(Text, ForeignKey('ActionsGroupPreset.ActionsGroupPresetId', ondelete="CASCADE"), nullable=False)
    ResourceId = Column(Text, nullable=False)
    ActionId = Column(Text, nullable=False)
    Order = Column(Integer, nullable=False)
    action_params: List[ActionRecipeParam] = relationship('ActionRecipeParam', cascade='all, delete', passive_deletes=True)
    __table_args__ = {'sqlite_autoincrement': True}

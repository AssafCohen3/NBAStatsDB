from typing import List

from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from dbmanager.Database.Models.ActionRecipe import ActionRecipe
from dbmanager.base import MyModel


class ActionsGroupPreset(MyModel):
    __tablename__ = 'ActionsGroupPreset'
    ActionsGroupPresetId = Column(Text, primary_key=True)
    PresetTranslatableNameJson = Column(Text, nullable=False)
    action_recipets: List[ActionRecipe] = relationship('ActionRecipe', order_by='ActionRecipe.Order',
                                                       cascade='all, delete',
                                                       passive_deletes=True)

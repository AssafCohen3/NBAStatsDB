from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKey
from sqlalchemy import Integer, Text
from dbmanager.base import MyModel


class ActionRecipeParam(MyModel):
    __tablename__ = 'ActionRecipeParam'
    ActionRecipeId = Column(Integer, ForeignKey('ActionRecipe.ActionRecipeId', ondelete="CASCADE"))
    ParamKey = Column(Text)
    ParamValue = Column(Text)
    __table_args__ = (
        PrimaryKeyConstraint('ActionRecipeId', 'ParamKey'),
    )

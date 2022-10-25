from dataclasses import dataclass
from typing import Dict, Type
from dbmanager.Resources.Actions.ActionAbc import ActionAbc


@dataclass
class ActionRecipeObject:
    preset_id: int
    action_cls: Type[ActionAbc]
    order: int
    params: Dict[str, str]

    def to_dict(self):
        return {
            'action_id': self.action_cls.get_action_id(),
            'action_title': self.action_cls.get_action_spec().get_action_title(),
            'resource_id': self.action_cls.get_action_spec().get_resource().get_id(),
            'resource_name': self.action_cls.get_action_spec().get_resource().get_name(),
            'order': self.order,
            'params': self.params
        }

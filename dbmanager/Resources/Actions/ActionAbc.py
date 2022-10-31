import datetime
import json
from abc import ABC, abstractmethod
from typing import Type, Dict, Any

from sqlalchemy import update
from sqlalchemy.orm import scoped_session
from dbmanager.Database.Models.Resource import Resource
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.tasks.TaskAbc import TaskAbc
from dbmanager.tasks.TaskMessage import TaskMessage


class ActionAbc(TaskAbc, ABC):
    def __init__(self, session: scoped_session, **kwargs):
        super().__init__()
        self.session: scoped_session = session

    @classmethod
    @abstractmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        """
        get action specification
        """

    def get_task_title(self) -> str:
        return self.get_action_spec().get_action_title()

    @classmethod
    def get_action_id(cls) -> str:
        return cls.get_action_spec().get_action_id()

    @classmethod
    def create_action_from_parsed_params(cls, session: scoped_session, parsed_params: Dict[str, Any]) -> 'ActionAbc':
        return cls(session, **parsed_params)

    @classmethod
    def create_action_from_request(cls, session: scoped_session, request_params: Dict[str, str]) -> 'ActionAbc':
        parsed_params = cls.get_action_spec().validate_request(session, request_params)
        return cls.create_action_from_parsed_params(session, parsed_params)

    def to_task_message(self) -> TaskMessage:
        return TaskMessage(
            self.get_task_id(),
            self.get_action_id(),
            self.get_action_spec().get_action_title(),
            self.get_action_spec().get_resource().get_id(),
            self.get_action_spec().get_resource().get_name(),
            self.get_current_subtask_text(),
            self.completed_subtasks(),
            self.subtasks_count(),
            self.current_status(),
            [],
            self.get_task_error_message(),
            self.get_retry_status()
        )

    def update_resource(self):
        stmt = (
            update(Resource)
            .where(Resource.ResourceId == self.get_action_spec().get_resource().get_id())
            .values(LastUpdated=datetime.datetime.now())
        )
        self.session.execute(stmt)
        self.session.commit()

    def after_execution_finished(self):
        if self.completed_subtasks() > 0:
            resources_to_update = [self.get_action_spec().get_resource()]
            data_to_send = [res.get_id() for res in resources_to_update]
            data_to_send = json.dumps(data_to_send)
            self.call_annnouncer_with_data('refresh-resources', data_to_send)

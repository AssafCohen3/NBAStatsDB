from sqlalchemy import select

from dbmanager.Database.Models.Resource import Resource


class ResourceDependentData:
    def __init__(self, fetch_func, depends_on_resources_ids):
        self.data = None
        self.fetch_func = fetch_func
        self.depends_on_resources_ids = depends_on_resources_ids
        self.last_updated = {
            resource_id: None
            for resource_id in depends_on_resources_ids
        }

    def get_data(self, session):
        if not self.data:
            self.fetch_data(session)
        else:
            last_updates_stmt = (
                select(Resource.ResourceId, Resource.LastUpdated).
                where(Resource.ResourceId.in_(self.depends_on_resources_ids))
            )
            last_updates = session.execute(last_updates_stmt).fetchall()
            refresh = False
            for resource_id, resource_last_update in last_updates:
                if self.last_updated[resource_id] != resource_last_update:
                    # TODO check comparison
                    refresh = True
                    break
            if refresh:
                self.fetch_data(session)
        return self.data

    def fetch_data(self, session):
        self.data = self.fetch_func(session)
        last_updates_stmt = (
            select(Resource.ResourceId, Resource.LastUpdated).
            where(Resource.ResourceId.in_(self.depends_on_resources_ids))
        )
        last_updates = session.execute(last_updates_stmt).fetchall()
        for resource_id, resource_last_update in last_updates:
            self.last_updated[resource_id] = resource_last_update

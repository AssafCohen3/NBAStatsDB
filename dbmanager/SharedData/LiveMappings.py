from typing import Dict
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.SharedData.ResourceDependentDataAbs import ResourceDependentDataAbs, T


class LiveMappings(ResourceDependentDataAbs[Dict[str, int]]):
    def __init__(self):
        super().__init__([PlayersMappingsResourceSpecification])

    def _fetch_data(self, session: scoped_session) -> T:
        stmt = select(PlayerMapping.PlayerBREFId, PlayerMapping.PlayerNBAId)
        res = session.execute(stmt).fetchall()
        res = {bref_id: nba_id for bref_id, nba_id in res}
        return res


live_mappings = LiveMappings()

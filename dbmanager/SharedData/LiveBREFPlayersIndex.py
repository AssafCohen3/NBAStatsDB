from dataclasses import dataclass
from typing import Dict, List, Type, Optional
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Resources.ResourceSpecifications.BREFPlayersResourceSpecification import BREFPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.ResourceDependentDataAbs import ResourceDependentDataAbs, T


@dataclass
class BREFPlayerDetails:
    player_id: str
    player_name: str
    from_season: int
    to_season: int


class LiveBREFPlayersIndex(ResourceDependentDataAbs[Dict[str, BREFPlayerDetails]]):
    def _fetch_data(self, session: scoped_session) -> T:
        stmt = select(BREFPlayer.PlayerId, BREFPlayer.PlayerName, BREFPlayer.FromYear, BREFPlayer.ToYear)
        res = session.execute(stmt).fetchall()
        res = {bref_id: BREFPlayerDetails(bref_id, bref_name, from_season, to_season) for bref_id, bref_name, from_season, to_season in res}
        return res

    def get_resource_dependent_list(self) -> List[Type[ResourceSpecificationAbc]]:
        return [
            BREFPlayersResourceSpecification
        ]

    def get_bref_player_by_id(self, session: scoped_session, player_id: str) -> Optional[BREFPlayerDetails]:
        return self.get_data(session).get(player_id)

    def get_bref_player_by_name_and_season(self, session: scoped_session, player_name: str, season: int) -> List[BREFPlayerDetails]:
        relevants = [p for p in self.get_data(session).values() if p.player_name == player_name and p.from_season - 5 <= season <= p.to_season + 5]
        return relevants


live_bref_players_index = LiveBREFPlayersIndex()

import asyncio
from asyncio import Event
from typing import Optional

from dbmanager.constants import STATS_API_DELAY_SECONDS, BREF_DELAY_SECONDS


class StatsLimiter:
    def __init__(self, delay: float):
        self.delay: float = delay
        self._ready: Optional[Event] = None

    def init_async(self):
        self._ready = asyncio.Event()
        self._ready.set()

    async def acquire(self):
        if self._ready is None:
            raise Exception('limiter not initiated')
        while not self._ready.is_set():
            await self._ready.wait()
        self._ready.clear()

    def release_with_delay(self):
        asyncio.get_event_loop().call_later(self.delay, self._ready.set)

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release_with_delay()


# to be initiated in the asyncio thread
stats_limiter = StatsLimiter(STATS_API_DELAY_SECONDS)

bref_limiter = StatsLimiter(BREF_DELAY_SECONDS)

import itertools
from typing import Optional
from requests import Session
from requests.sessions import Request, PreparedRequest
from dbmanager.RequestHandlers.Limiter import stats_limiter, StatsLimiter
from dbmanager.constants import STATS_API_SESSION_MAX_REQUESTS, STATS_HEADERS


class ThreadSafeCounter:
    def __init__(self, start=0):
        self._start = start
        self._counter = itertools.count(start)

    def inc_and_get(self) -> int:
        return next(self._counter)

    def reset_counter(self):
        self._counter = itertools.count(self._start)


class TimeoutSession(Session):
    def __init__(self, timeout: float):
        super().__init__()
        self.timeout: float = timeout

    def send(self, request, *args, **kwargs):
        kwargs["timeout"] = self.timeout
        return super().send(request, *args, **kwargs)


class MyStatsSession(TimeoutSession):

    def __init__(self, timeout: float, max_requests_before_refresh: Optional[int], limiter: StatsLimiter) -> None:
        super().__init__(timeout)
        self.requests_counter: ThreadSafeCounter = ThreadSafeCounter()
        self.max_requests_before_refresh: Optional[int] = max_requests_before_refresh
        self.limiter = limiter

    def reset_session(self):
        self.requests_counter.reset_counter()
        self.cookies.clear()

    def prepare_request(self, request: Request) -> PreparedRequest:
        if self.max_requests_before_refresh and self.requests_counter.inc_and_get() > self.max_requests_before_refresh:
            self.reset_session()
        return super().prepare_request(request)

    async def async_get(self, url, *args, **kwargs):
        async with self.limiter:
            to_ret = self.get(url, headers=STATS_HEADERS, *args, **kwargs)
        return to_ret


stats_session = MyStatsSession(10, STATS_API_SESSION_MAX_REQUESTS, stats_limiter)
bref_session = TimeoutSession(10)
timeout_session = TimeoutSession(10)

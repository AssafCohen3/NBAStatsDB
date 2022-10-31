import asyncio
import itertools
import logging
from typing import Optional

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.sessions import Request, PreparedRequest
from urllib3 import Retry

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


# class TimeoutHTTPAdapter(HTTPAdapter):
#     def __init__(self, *args, **kwargs):
#         if "timeout" in kwargs:
#             self.timeout = kwargs["timeout"]
#             del kwargs["timeout"]
#         else:
#             self.timeout = 10   # or whatever default you want
#         super().__init__(*args, **kwargs)
#
#     def send(self, request, **kwargs):
#         kwargs["timeout"] = self.timeout
#         return super().send(request, **kwargs)


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


# async def call_async_with_retry(func_to_call, retries_number=1):
#     await stats_limiter.acquire()
#     for i in range(0, retries_number + 1):
#         current_request_count = requests_count.inc_and_get()
#         if current_request_count >= STATS_API_SESSION_MAX_REQUESTS:
#             logging.info('Stats requests handler: reached session max requests limit. clearing cookies...')
#             stats_session.cookies.clear()
#             requests_count.reset_counter()
#         try:
#             to_ret = func_to_call()
#             if i > 0:
#                 logging.info('Stats requests handler: recovered successfully!')
#             stats_limiter.release_with_delay()
#             return to_ret
#         except requests.exceptions.ConnectionError:
#             logging.info(f'Stats requests handler: recieved timeout. {"trying to recover..." if i < retries_number else ""}')
#             stats_session.cookies.clear()
#             await asyncio.sleep(10)
#         except requests.exceptions.RetryError:
#             logging.info(f'Stats requests handler: recieved too many timeouts. resting...')
#             stats_session.cookies.clear()
#             await asyncio.sleep(60)
#     logging.info('Stats requests handler: failed to recover.')
#     stats_limiter.release_with_delay()
#     return None


stats_session = MyStatsSession(10, STATS_API_SESSION_MAX_REQUESTS, stats_limiter)
bref_session = TimeoutSession(10)
timeout_session = TimeoutSession(10)
# retries = Retry(total=1, backoff_factor=1, status_forcelist=[502, 503, 504])
# adapter = TimeoutHTTPAdapter(max_retries=retries, timeout=10)
# stats_session.mount('https://', adapter)
# stats_session.mount('http://', adapter)
# requests_count = ThreadSafeCounter()

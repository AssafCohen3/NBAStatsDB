import time

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from http import cookiejar


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        else:
            self.timeout = 10   # or whatever default you want
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


requests_session = requests.Session()
#  requests_session.cookies.set_policy(BlockAll())
retries = Retry(total=1, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = TimeoutHTTPAdapter(max_retries=retries, timeout=10)
requests_session.mount('https://', adapter)
requests_session.mount('http://', adapter)


def call_with_retry(func_to_call, retries_number=1):
    for i in range(0, retries_number + 1):
        try:
            to_ret = func_to_call()
            if i > 0:
                print('recovered successfully!')
            return to_ret
        except requests.exceptions.ConnectionError:
            print(f'recieved timeout. {"trying to recover..." if i < retries_number else ""}')
            requests_session.cookies.clear()
            time.sleep(10)
        except requests.exceptions.RetryError:
            print(f'recieved too many timeouts. resting...')
            requests_session.cookies.clear()
            time.sleep(60)
    print('failed to recover.')
    return None

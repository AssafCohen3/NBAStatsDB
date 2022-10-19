from itertools import tee, islice, chain
from typing import Iterable, TypeVar, Tuple, Optional

R = TypeVar('R')


def iterate_with_next(some_iterable: Iterable[R], last_val=None) -> Iterable[Tuple[R, Optional[R]]]:
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [last_val])
    return zip(items, nexts)

"""단축 링크 리다이렉트를 위한 1차 캐시.

짧은 코드 -> 원본 URL 매핑은 생성된 이후 바뀌지 않지만, 링크가 삭제되면
해당 코드만 정확히 캐시에서 제거해야 하므로 functools.lru_cache 대신
OrderedDict로 직접 LRU를 구현한다 (lru_cache는 특정 키만 지우는 기능이 없다).
"""

import threading
from collections import OrderedDict

from .database import SessionLocal
from .models import Link

CACHE_SIZE = 10_000

_cache: "OrderedDict[str, str]" = OrderedDict()
_lock = threading.Lock()


def get_url(code: str) -> str:
    with _lock:
        url = _cache.get(code)
        if url is not None:
            _cache.move_to_end(code)
            return url

    session = SessionLocal()
    try:
        link = session.query(Link).filter_by(code=code).one_or_none()
    finally:
        session.close()
    if link is None:
        raise KeyError(code)

    with _lock:
        _cache[code] = link.url
        _cache.move_to_end(code)
        if len(_cache) > CACHE_SIZE:
            _cache.popitem(last=False)

    return link.url


def invalidate(code: str) -> None:
    with _lock:
        _cache.pop(code, None)


def clear_all() -> None:
    with _lock:
        _cache.clear()

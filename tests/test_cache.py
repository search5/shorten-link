import os

os.environ.setdefault("SHORTEN_LINK_DB_URL", "sqlite://")

import pytest

from shorten_link import cache
from shorten_link.database import Base, SessionLocal, engine
from shorten_link.models import Link


@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    cache.clear_all()
    session = SessionLocal()
    session.add_all([Link(code="a", url="https://a.example.com"), Link(code="b", url="https://b.example.com")])
    session.commit()
    session.close()


def test_invalidate_removes_only_the_given_code(db):
    assert cache.get_url("a") == "https://a.example.com"
    assert cache.get_url("b") == "https://b.example.com"

    cache.invalidate("a")

    assert "a" not in cache._cache
    assert cache._cache["b"] == "https://b.example.com"


def test_invalidate_missing_code_is_a_no_op(db):
    cache.invalidate("does-not-exist")  # 예외 없이 조용히 무시되어야 함

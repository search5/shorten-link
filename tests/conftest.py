import os

os.environ["SHORTEN_LINK_DB_URL"] = "sqlite://"  # 테스트마다 독립된 인메모리 DB

import pytest
from webtest import TestApp

from shorten_link import cache, make_app
from shorten_link.database import Base, engine


@pytest.fixture
def app():
    Base.metadata.drop_all(engine)
    cache.clear_all()
    wsgi_app = make_app()
    return TestApp(wsgi_app)

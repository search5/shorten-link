import os

os.environ["SHORTEN_LINK_DB_URL"] = "sqlite://"  # 테스트마다 독립된 인메모리 DB
os.environ["SHORTEN_LINK_API_KEY"] = "test-api-key"

import pytest
from webtest import TestApp

from shorten_link import cache, make_app
from shorten_link.database import Base, engine

TEST_API_KEY = os.environ["SHORTEN_LINK_API_KEY"]
AUTH_HEADER = {"HTTP_AUTHORIZATION": f"Bearer {TEST_API_KEY}"}


@pytest.fixture
def app():
    """인증 헤더가 기본으로 붙어 있는 TestApp (관리 API 테스트용)."""
    Base.metadata.drop_all(engine)
    cache.clear_all()
    wsgi_app = make_app()
    return TestApp(wsgi_app, extra_environ=AUTH_HEADER)


@pytest.fixture
def anon_app(app):
    """인증 헤더가 없는 TestApp (인증 실패/공개 리다이렉트 테스트용). 동일 WSGI 앱을 공유한다."""
    return TestApp(app.app)

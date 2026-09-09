from pyramid.config import Configurator

from .database import init_db


def make_app(global_config=None, **settings):
    """Pyramid WSGI 앱 팩토리."""
    init_db()

    with Configurator(settings=settings) as config:
        config.add_route("index", "/")
        config.add_route("create_link", "/api/links")
        config.add_route("get_link", "/api/links/{code}")
        config.add_route("link_stats", "/api/links/{code}/stats")
        config.add_route("redirect", "/{code}")
        config.add_tween("shorten_link.auth.api_key_tween_factory")
        config.scan("shorten_link.views")
        app = config.make_wsgi_app()

    return app


# Pyramid의 egg:shorten_link 진입점과 호환되도록 유지
main = make_app


def run() -> None:
    """`uv run shorten-link` 로 개발 서버를 기동한다."""
    import os

    from waitress import serve

    app = make_app()
    host = os.environ.get("SHORTEN_LINK_HOST", "0.0.0.0")
    port = int(os.environ.get("SHORTEN_LINK_PORT", "6543"))
    print(f"shorten-link 서버 시작: http://{host}:{port}")
    serve(app, host=host, port=port)

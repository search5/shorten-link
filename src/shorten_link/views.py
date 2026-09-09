from urllib.parse import urlparse

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
    HTTPNoContent,
    HTTPNotFound,
)
from pyramid.view import view_config

from . import cache, shortcode
from .access import record_access
from .database import SessionLocal
from .models import AccessLog, Link


def _is_valid_url(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


@view_config(route_name="index", request_method="GET", renderer="json")
def index_view(request):
    return {
        "name": "shorten-link",
        "endpoints": {
            "create": "POST /api/links {\"url\": \"...\"}",
            "get": "GET /api/links/{code}",
            "stats": "GET /api/links/{code}/stats",
            "delete": "DELETE /api/links/{code}",
            "redirect": "GET /{code}",
        },
    }


@view_config(route_name="create_link", request_method="POST", renderer="json")
def create_link_view(request):
    try:
        body = request.json_body
    except ValueError:
        raise HTTPBadRequest(json_body={"error": "요청 본문이 올바른 JSON이 아닙니다."})

    url = body.get("url") if isinstance(body, dict) else None
    if not _is_valid_url(url):
        raise HTTPBadRequest(
            json_body={"error": "url 필드는 http:// 또는 https:// 로 시작하는 유효한 주소여야 합니다."}
        )

    session = SessionLocal()
    try:
        link = Link(url=url)
        session.add(link)
        session.flush()  # id 확보
        link.code = shortcode.encode_id(link.id)
        session.commit()
        result = link.to_dict()
    finally:
        session.close()

    request.response.status_code = 201
    result["short_path"] = f"/{result['code']}"
    return result


@view_config(route_name="get_link", request_method="GET", renderer="json")
def get_link_view(request):
    code = request.matchdict["code"]
    session = SessionLocal()
    try:
        link = session.query(Link).filter_by(code=code).one_or_none()
    finally:
        session.close()

    if link is None:
        raise HTTPNotFound(json_body={"error": "존재하지 않는 코드입니다."})

    return link.to_dict()


@view_config(route_name="get_link", request_method="DELETE")
def delete_link_view(request):
    code = request.matchdict["code"]
    session = SessionLocal()
    try:
        link = session.query(Link).filter_by(code=code).one_or_none()
        if link is None:
            raise HTTPNotFound(json_body={"error": "존재하지 않는 코드입니다."})
        session.delete(link)
        session.commit()
    finally:
        session.close()

    cache.invalidate(code)
    return HTTPNoContent()


@view_config(route_name="link_stats", request_method="GET", renderer="json")
def link_stats_view(request):
    code = request.matchdict["code"]
    session = SessionLocal()
    try:
        link = session.query(Link).filter_by(code=code).one_or_none()
        if link is None:
            raise HTTPNotFound(json_body={"error": "존재하지 않는 코드입니다."})

        last_access = (
            session.query(AccessLog)
            .filter_by(link_id=link.id)
            .order_by(AccessLog.accessed_at.desc())
            .first()
        )
        result = {
            "code": link.code,
            "url": link.url,
            "created_at": link.created_at.isoformat(),
            "hit_count": link.hit_count,
            "last_accessed_at": last_access.accessed_at.isoformat() if last_access else None,
        }
    finally:
        session.close()

    return result


@view_config(route_name="redirect", request_method="GET")
def redirect_view(request):
    code = request.matchdict["code"]
    try:
        url = cache.get_url(code)
    except KeyError:
        raise HTTPNotFound(json_body={"error": "존재하지 않는 코드입니다."})

    record_access(code)
    return HTTPFound(location=url)

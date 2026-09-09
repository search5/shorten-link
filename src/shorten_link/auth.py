"""관리용 API(/api/links*) 보호를 위한 고정 API 키 인증.

`/{code}` 리다이렉트는 누구나 접속해야 하므로 인증 대상에서 제외한다.
"""

import os

from pyramid.httpexceptions import HTTPUnauthorized

PROTECTED_PREFIX = "/api/links"


def _load_api_key() -> str:
    api_key = os.environ.get("SHORTEN_LINK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "SHORTEN_LINK_API_KEY 환경변수가 설정되지 않았습니다. "
            "관리용 API(/api/links*)를 보호할 임의의 토큰 값을 설정해주세요."
        )
    return api_key


def api_key_tween_factory(handler, registry):
    expected = f"Bearer {_load_api_key()}"

    def tween(request):
        if request.path.startswith(PROTECTED_PREFIX) and request.headers.get("Authorization") != expected:
            return HTTPUnauthorized(json_body={"error": "유효한 API 토큰이 필요합니다."})
        return handler(request)

    return tween

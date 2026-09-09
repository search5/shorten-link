# shorten-link

단축 링크 생성/조회/리다이렉트/통계 REST API (Python Pyramid)

## 실행

```bash
uv run shorten-link            # http://0.0.0.0:6543
SHORTEN_LINK_PORT=6544 uv run shorten-link   # 포트 변경
```

## 테스트

```bash
uv run pytest
```

## API

- `POST /api/links` `{"url": "https://example.com"}` → 단축 코드 생성 (base62로 인코딩된 순번 ID)
- `GET /api/links/{code}` → 원본 URL/생성일/조회 수 조회
- `GET /api/links/{code}/stats` → 조회 수, 마지막 접속 시각 등 통계
- `DELETE /api/links/{code}` → 링크 삭제 (해당 코드의 캐시 항목도 함께 제거)
- `GET /{code}` → 원본 URL로 302 리다이렉트 (조회는 1차 캐시 사용)

## 구조

- `src/shorten_link/models.py` — `Link`, `AccessLog` (SQLAlchemy, 기본 SQLite)
- `src/shorten_link/shortcode.py` — id ↔ base62 코드 인코딩/디코딩 (10000번부터 시작)
- `src/shorten_link/cache.py` — 코드 → URL 1차 캐시 (OrderedDict 기반 LRU, 코드 단위 삭제 지원)
- `src/shorten_link/views.py` — REST API / 리다이렉트 뷰

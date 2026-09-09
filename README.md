# shorten-link

단축 링크 생성/조회/삭제/리다이렉트/통계 REST API (Python Pyramid)

## 요구 사항

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (의존성 관리 및 실행)

## 설치

```bash
git clone git@github.com:search5/shorten-link.git
cd shorten-link
uv sync
```

`uv sync`가 `.venv`를 만들고 `pyproject.toml`에 정의된 의존성(pyramid, sqlalchemy, waitress 등)을 설치한다.

## 실행

```bash
uv run shorten-link
```

기본적으로 `http://0.0.0.0:6543` 에서 서버가 뜨고, 실행 위치에 `shorten_link.db` (SQLite)가 생성된다.

### 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `SHORTEN_LINK_HOST` | `0.0.0.0` | 바인딩 호스트 |
| `SHORTEN_LINK_PORT` | `6543` | 바인딩 포트 |
| `SHORTEN_LINK_DB_URL` | `sqlite:///shorten_link.db` | SQLAlchemy 접속 문자열 |

```bash
# 포트를 바꿔서 실행 (예: 6543이 다른 프로세스에서 이미 쓰이는 경우)
SHORTEN_LINK_PORT=6544 uv run shorten-link

# DB 파일 위치나 종류를 바꾸는 경우
SHORTEN_LINK_DB_URL=sqlite:////var/data/shorten_link.db uv run shorten-link
```

## 사용법 (curl 예시)

아래는 서버를 `http://127.0.0.1:6544` 로 띄운 상태를 가정한 전체 흐름이다.

### 1. 단축 링크 생성

```bash
curl -s -X POST http://127.0.0.1:6544/api/links \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.google.com/search?q=pyramid"}'
```

```json
{"code": "2Bi", "url": "https://www.google.com/search?q=pyramid", "created_at": "2026-09-09T06:30:26.473176+00:00", "hit_count": 0, "short_path": "/2Bi"}
```

- `code`는 DB 내부 순번 ID를 base62(0-9, a-z, A-Z)로 인코딩한 값이다. 첫 링크는 10000번부터 시작하므로 `2Bi`가 나온다 (`base62(10000) == "2Bi"`).
- `url`이 없거나 `http://`/`https://`로 시작하지 않으면 `400`이 반환된다.

```bash
curl -s -X POST http://127.0.0.1:6544/api/links \
  -H 'Content-Type: application/json' \
  -d '{"url": "invalid-url"}'
# {"error":"url 필드는 http:// 또는 https:// 로 시작하는 유효한 주소여야 합니다."}
```

### 2. 원본 URL 조회

```bash
curl -s http://127.0.0.1:6544/api/links/2Bi
```

```json
{"code": "2Bi", "url": "https://www.google.com/search?q=pyramid", "created_at": "2026-09-09T06:30:26.473176", "hit_count": 0}
```

존재하지 않는 코드면 `404`와 `{"error": "존재하지 않는 코드입니다."}` 가 반환된다.

### 3. 단축 링크 접속 (리다이렉트)

```bash
curl -s -D - -o /dev/null http://127.0.0.1:6544/2Bi
```

```
HTTP/1.1 302 Found
Location: https://www.google.com/search?q=pyramid
```

- 코드 → URL 조회는 in-memory 1차 캐시(`src/shorten_link/cache.py`)를 먼저 확인하므로, 캐시 히트 시 DB 조회 없이 바로 이동한다.
- 접속마다 `hit_count`가 1 증가하고 `access_logs`에 접속 기록이 1건 남는다.
- 브라우저로 직접 `http://127.0.0.1:6544/2Bi` 를 열어도 원본 URL로 이동한다.

### 4. 접속 통계 조회

```bash
curl -s http://127.0.0.1:6544/api/links/2Bi/stats
```

```json
{"code": "2Bi", "url": "https://www.google.com/search?q=pyramid", "created_at": "2026-09-09T06:30:26.473176", "hit_count": 1, "last_accessed_at": "2026-09-09T06:30:26.551619"}
```

### 5. 단축 링크 삭제

```bash
curl -s -D - -o /dev/null -X DELETE http://127.0.0.1:6544/api/links/2Bi
```

```
HTTP/1.1 204 No Content
```

- 삭제 시 DB 레코드(및 연관 `access_logs`)와 해당 코드의 캐시 항목이 함께 제거된다 (다른 코드의 캐시는 영향 없음).
- 삭제 후 같은 코드로 조회/리다이렉트하면 모두 `404`가 반환된다.

```bash
curl -s http://127.0.0.1:6544/api/links/2Bi
# {"error":"존재하지 않는 코드입니다."}
```

## API 요약

| Method | Path | 설명 |
|---|---|---|
| POST | `/api/links` | 단축 링크 생성. 본문: `{"url": "https://..."}` |
| GET | `/api/links/{code}` | 원본 URL/생성일/조회 수 조회 |
| GET | `/api/links/{code}/stats` | 조회 수, 마지막 접속 시각 등 통계 |
| DELETE | `/api/links/{code}` | 링크 삭제 (캐시 항목도 함께 제거) |
| GET | `/{code}` | 원본 URL로 302 리다이렉트 |
| GET | `/` | 사용 가능한 엔드포인트 목록 |

## 테스트

```bash
uv run pytest
```

## 구조

- `src/shorten_link/models.py` — `Link`, `AccessLog` (SQLAlchemy, 기본 SQLite)
- `src/shorten_link/shortcode.py` — id ↔ base62 코드 인코딩/디코딩 (10000번부터 시작)
- `src/shorten_link/cache.py` — 코드 → URL 1차 캐시 (OrderedDict 기반 LRU, 코드 단위 삭제 지원)
- `src/shorten_link/access.py` — 리다이렉트 시 조회 수/접속 로그 기록
- `src/shorten_link/views.py` — REST API / 리다이렉트 뷰

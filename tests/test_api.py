from shorten_link import shortcode


def test_create_and_get_link(app):
    resp = app.post_json("/api/links", {"url": "https://example.com/page"})
    assert resp.status_code == 201
    data = resp.json
    code = data["code"]
    assert code == shortcode.encode_id(1)  # 첫 링크 -> id=1 -> base62(10000)
    assert data["url"] == "https://example.com/page"
    assert data["hit_count"] == 0

    resp2 = app.get(f"/api/links/{code}")
    assert resp2.status_code == 200
    assert resp2.json["url"] == "https://example.com/page"


def test_codes_start_at_10000_and_are_sequential(app):
    codes = [app.post_json("/api/links", {"url": "https://example.com"}).json["code"] for _ in range(3)]
    assert codes == [shortcode.encode_id(1), shortcode.encode_id(2), shortcode.encode_id(3)]
    assert shortcode.decode(codes[0]) == shortcode.START_ID


def test_create_link_rejects_invalid_url(app):
    resp = app.post_json("/api/links", {"url": "not-a-url"}, expect_errors=True)
    assert resp.status_code == 400

    resp2 = app.post_json("/api/links", {}, expect_errors=True)
    assert resp2.status_code == 400


def test_get_unknown_code_is_404(app):
    resp = app.get("/api/links/doesnotexist", expect_errors=True)
    assert resp.status_code == 404


def test_redirect_and_stats(app):
    created = app.post_json("/api/links", {"url": "https://example.com/target"}).json
    code = created["code"]

    resp = app.get(f"/{code}")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com/target"

    app.get(f"/{code}")
    app.get(f"/{code}")

    stats = app.get(f"/api/links/{code}/stats").json
    assert stats["hit_count"] == 3
    assert stats["last_accessed_at"] is not None


def test_redirect_unknown_code_is_404(app):
    resp = app.get("/doesnotexist", expect_errors=True)
    assert resp.status_code == 404


def test_delete_link_removes_it_and_its_cache_entry(app):
    created = app.post_json("/api/links", {"url": "https://example.com/delete-me"}).json
    code = created["code"]

    # 캐시를 먼저 데워둔 뒤 삭제해도 이후 리다이렉트는 404여야 한다
    assert app.get(f"/{code}").status_code == 302

    resp = app.delete(f"/api/links/{code}")
    assert resp.status_code == 204

    assert app.get(f"/api/links/{code}", expect_errors=True).status_code == 404
    assert app.get(f"/api/links/{code}/stats", expect_errors=True).status_code == 404
    assert app.get(f"/{code}", expect_errors=True).status_code == 404


def test_deleting_one_link_does_not_evict_others_from_cache(app):
    a = app.post_json("/api/links", {"url": "https://a.example.com"}).json["code"]
    b = app.post_json("/api/links", {"url": "https://b.example.com"}).json["code"]

    app.get(f"/{a}")
    app.get(f"/{b}")

    app.delete(f"/api/links/{a}")

    resp = app.get(f"/{b}")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://b.example.com"


def test_delete_unknown_code_is_404(app):
    resp = app.delete("/api/links/doesnotexist", expect_errors=True)
    assert resp.status_code == 404

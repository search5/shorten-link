def test_management_api_requires_token(anon_app):
    resp = anon_app.post_json("/api/links", {"url": "https://example.com"}, expect_errors=True)
    assert resp.status_code == 401


def test_management_api_rejects_wrong_token(app):
    from webtest import TestApp

    wrong_token_app = TestApp(app.app, extra_environ={"HTTP_AUTHORIZATION": "Bearer wrong-token"})
    resp = wrong_token_app.post_json("/api/links", {"url": "https://example.com"}, expect_errors=True)
    assert resp.status_code == 401


def test_management_api_accepts_correct_token(app):
    resp = app.post_json("/api/links", {"url": "https://example.com"})
    assert resp.status_code == 201


def test_redirect_does_not_require_token(app, anon_app):
    code = app.post_json("/api/links", {"url": "https://example.com/no-auth-needed"}).json["code"]

    resp = anon_app.get(f"/{code}")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com/no-auth-needed"


def test_index_does_not_require_token(anon_app):
    resp = anon_app.get("/")
    assert resp.status_code == 200

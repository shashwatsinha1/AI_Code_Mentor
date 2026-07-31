async def _login(client) -> dict[str, str]:
    await client.post(
        "/auth/signup",
        json={"email": "workspace@example.com", "password": "correct-horse"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "workspace@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 200
    return response.json()


async def test_draft_can_be_saved_read_and_updated(client):
    tokens = await _login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    missing = await client.get("/drafts/python", headers=headers)
    assert missing.status_code == 200
    assert missing.json() is None

    saved = await client.put(
        "/drafts",
        headers=headers,
        json={"language": "python", "code": "print('hello')"},
    )
    assert saved.status_code == 200
    assert saved.json()["code"] == "print('hello')"

    updated = await client.put(
        "/drafts",
        headers=headers,
        json={"language": "python", "code": "print('updated')"},
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == saved.json()["id"]

    loaded = await client.get("/drafts/python", headers=headers)
    assert loaded.status_code == 200
    assert loaded.json()["code"] == "print('updated')"


async def test_draft_accepts_cpp_alias(client):
    tokens = await _login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    saved = await client.put(
        "/drafts",
        headers=headers,
        json={"language": "c++", "code": "int main() { return 0; }"},
    )
    assert saved.status_code == 200
    assert saved.json()["language"] == "cpp"

    loaded = await client.get("/drafts/c++", headers=headers)
    assert loaded.status_code == 200
    assert loaded.json()["language"] == "cpp"


async def test_execute_requires_auth(client):
    response = await client.post(
        "/execute",
        json={"language": "python", "code": "print('hello')"},
    )
    assert response.status_code == 401


async def test_execute_uses_judge0_executor(client, monkeypatch):
    from app.api.routes import execute as execute_route
    from app.schemas.execute import ExecuteRequest, ExecuteResponse

    async def fake_execute(payload: ExecuteRequest) -> ExecuteResponse:
        assert payload.language == "python"
        assert payload.code == "print('hello')"
        assert payload.stdin == "input text"
        return ExecuteResponse(stdout="hello\n", stderr="", exit_code=0)

    monkeypatch.setattr(execute_route.judge0_executor, "execute", fake_execute)

    tokens = await _login(client)
    response = await client.post(
        "/execute",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": "print('hello')", "stdin": "input text"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "stdout": "hello\n",
        "stderr": "",
        "exit_code": 0,
        "timed_out": False,
    }

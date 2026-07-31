from app.services.ai_mentor import AIMentorService


async def _login(client) -> dict[str, str]:
    await client.post(
        "/auth/signup",
        json={"email": "mentor@example.com", "password": "correct-horse"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "mentor@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 200
    return response.json()


async def test_mentor_endpoints_require_auth(client):
    response = await client.post("/explain", json={"language": "python", "code": "print('x')"})
    assert response.status_code == 401


async def test_explain_returns_local_response(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/explain",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": "for i in range(3):\n    print(i)"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local"
    assert "loop" in payload["result"]


async def test_explain_simple_print_is_specific(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/explain",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": "print('hello')", "stdout": "hello\n", "exit_code": 0},
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert "standard output" in result
    assert "print" in result
    assert "stdout: hello" in result


async def test_hint_never_returns_solution_code(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/hint",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": "print('todo')", "hint_level": 2},
    )
    assert response.status_code == 200
    assert response.json()["source"] == "local"


async def test_bug_detection_uses_latest_run_context(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/detect-bugs",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "language": "python",
            "code": "print(unknown_name)",
            "stderr": "NameError: name 'unknown_name' is not defined",
            "exit_code": 1,
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert "exited with code 1" in result
    assert "stderr" in result


async def test_optimize_returns_local_guidance(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/optimize",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "language": "python",
            "problem_statement": "Find whether a value exists in a list.",
            "code": "nums = list(map(int, input().split()))\nfor q in nums:\n    print(q in nums)",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "local"
    assert "Optimization guidance" in payload["result"]


async def test_code_with_curly_braces_renders_without_formatting_error(client, monkeypatch):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    code_with_braces = "d = {'key': 'value', 'items': [1, 2]}\nprint(f'data: {d}')"
    response = await client.post(
        "/explain",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": code_with_braces},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "result" in payload


async def test_explain_median_of_two_sorted_arrays_returns_specific_dsa_approach(
    client, monkeypatch
):
    monkeypatch.setattr(AIMentorService, "api_key", property(lambda self: None))
    tokens = await _login(client)
    response = await client.post(
        "/explain",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "language": "python",
            "problem_statement": "Median of Two Sorted Arrays - Find median of two combined sorted arrays in O(log(min(N,M)))",
            "code": "# Python starter template\ndef findMedianSortedArrays(nums1, nums2):\n    pass",
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert "Median of Two Sorted Arrays" in result
    assert "O(log(min(N,M)))" in result or "O(log(min(N, M)))" in result
    assert "Binary Search on Partitioning" in result or "Binary Search" in result
    assert "Understanding Arrays (Data Structures)" not in result

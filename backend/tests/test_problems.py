async def _login(client) -> dict[str, str]:
    await client.post(
        "/auth/signup",
        json={"email": "problems@example.com", "password": "correct-horse"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "problems@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 200
    return response.json()


async def test_problem_list_requires_auth(client):
    response = await client.get("/problems")
    assert response.status_code == 401


async def test_problem_list_and_detail(client):
    tokens = await _login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    list_response = await client.get("/problems", headers=headers)
    assert list_response.status_code == 200
    problems = list_response.json()
    assert len(problems) >= 30
    assert any(problem["slug"] == "two-sum" for problem in problems)

    detail_response = await client.get("/problems/two-sum", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["title"] == "Two Sum"
    assert detail["test_cases"]
    assert detail["test_cases"][0]["stdin"].startswith("4\n")
    assert "python" in detail["starter_code"]

    binary_response = await client.get("/problems/binary-search", headers=headers)
    assert binary_response.status_code == 200
    binary_detail = binary_response.json()
    assert binary_detail["test_cases"][0]["stdin"].startswith("6\n")
    assert "vector<int> nums" in binary_detail["starter_code"]["cpp"]
    assert "int target" in binary_detail["starter_code"]["cpp"]
    assert "int[] nums" in binary_detail["starter_code"]["java"]
    assert "int target" in binary_detail["starter_code"]["java"]

    islands_response = await client.get("/problems/number-of-islands", headers=headers)
    assert islands_response.status_code == 200
    islands_detail = islands_response.json()
    assert "int rows, cols" in islands_detail["starter_code"]["cpp"]
    assert "vector<string> grid" in islands_detail["starter_code"]["cpp"]
    assert "char[][] grid" in islands_detail["starter_code"]["java"]

    median_response = await client.get("/problems/median-of-two-sorted-arrays", headers=headers)
    assert median_response.status_code == 200
    median_detail = median_response.json()
    assert "vector<int> a" in median_detail["starter_code"]["cpp"]
    assert "vector<int> b" in median_detail["starter_code"]["cpp"]
    assert "int[] a" in median_detail["starter_code"]["java"]
    assert "int[] b" in median_detail["starter_code"]["java"]

    for problem in problems:
        response = await client.get(f"/problems/{problem['slug']}", headers=headers)
        assert response.status_code == 200
        detail = response.json()
        assert len(detail["test_cases"]) >= 2
        assert {"python", "cpp", "java"}.issubset(detail["starter_code"])


async def test_problem_filters(client):
    tokens = await _login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.get("/problems?difficulty=easy&tag=stack", headers=headers)
    assert response.status_code == 200
    problems = response.json()
    assert [problem["slug"] for problem in problems] == ["valid-parentheses"]

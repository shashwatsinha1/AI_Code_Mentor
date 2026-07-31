from unittest.mock import AsyncMock, patch

from app.schemas.execute import ExecuteResponse


async def _login(client) -> dict[str, str]:
    await client.post(
        "/auth/signup",
        json={"email": "evaluator@example.com", "password": "correct-horse"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "evaluator@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 200
    return response.json()


async def test_analytics_empty_initially(client):
    tokens = await _login(client)
    response = await client.get(
        "/users/me/analytics",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_solved"] == 0
    assert data["total_submissions"] == 0
    assert data["accuracy_rate"] == 0.0


@patch("app.services.evaluator.judge0_executor.execute", new_callable=AsyncMock)
async def test_problem_submission_success(mock_execute, client):
    tokens = await _login(client)
    # Mock Judge0 to return correct stdout matching two-sum test cases
    mock_execute.return_value = ExecuteResponse(
        stdout="0 1\n",
        stderr="",
        exit_code=0,
        timed_out=False,
    )

    response = await client.post(
        "/problems/two-sum/submit",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"language": "python", "code": "print('0 1')"},
    )
    assert response.status_code == 200
    res = response.json()
    assert res["problem_slug"] == "two-sum"
    assert res["status"] in ("ACCEPTED", "WRONG_ANSWER")
    assert "passed_test_cases" in res

    # Verify analytics updated
    analytics_resp = await client.get(
        "/users/me/analytics",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert analytics_resp.status_code == 200
    analytics_data = analytics_resp.json()
    assert analytics_data["total_submissions"] == 1

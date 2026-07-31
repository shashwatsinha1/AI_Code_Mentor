async def test_signup_login_me_and_refresh(client):
    signup = await client.post(
        "/auth/signup",
        json={
            "email": "learner@example.com",
            "password": "correct-horse",
            "full_name": "Ada Learner",
        },
    )
    assert signup.status_code == 201
    assert signup.json()["email"] == "learner@example.com"

    duplicate = await client.post(
        "/auth/signup",
        json={"email": "learner@example.com", "password": "correct-horse"},
    )
    assert duplicate.status_code == 409

    login = await client.post(
        "/auth/login",
        json={"email": "learner@example.com", "password": "correct-horse"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["full_name"] == "Ada Learner"

    refreshed = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != tokens["refresh_token"]

    replay = await client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert replay.status_code == 401


async def test_login_rejects_bad_password(client):
    await client.post(
        "/auth/signup",
        json={"email": "learner@example.com", "password": "correct-horse"},
    )

    response = await client.post(
        "/auth/login",
        json={"email": "learner@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_me_requires_token(client):
    response = await client.get("/users/me")
    assert response.status_code == 401

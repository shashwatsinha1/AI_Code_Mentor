async def _login(client) -> dict[str, str]:
    await client.post(
        "/auth/signup",
        json={"email": "sheets@example.com", "password": "correct-horse"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "sheets@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 200
    return response.json()


async def test_list_sheets(client):
    tokens = await _login(client)
    response = await client.get(
        "/sheets",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    sheets = response.json()
    assert len(sheets) >= 2
    slugs = [s["slug"] for s in sheets]
    assert "strivers-sde-pattern-sheet" in slugs


async def test_get_sheet_detail_grouped_by_patterns(client):
    tokens = await _login(client)
    response = await client.get(
        "/sheets/strivers-sde-pattern-sheet",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    sheet = response.json()
    assert sheet["slug"] == "strivers-sde-pattern-sheet"
    assert len(sheet["patterns"]) > 0

    pattern_names = [p["pattern"] for p in sheet["patterns"]]
    assert any("Day" in p or "Two Pointers" in p for p in pattern_names)
    assert any("Day" in p or "Sliding Window" in p for p in pattern_names)


async def test_toggle_sheet_item_completion(client):
    tokens = await _login(client)
    # First get detail to get an item_id
    detail_res = await client.get(
        "/sheets/strivers-sde-pattern-sheet",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    sheet = detail_res.json()
    first_item = sheet["patterns"][0]["items"][0]
    item_id = first_item["id"]

    # Toggle completed ON
    toggle1 = await client.post(
        f"/sheets/strivers-sde-pattern-sheet/items/{item_id}/toggle",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert toggle1.status_code == 200
    res1 = toggle1.json()
    assert res1["is_completed"] is True
    assert res1["completed_questions"] == 1

    # Toggle completed OFF
    toggle2 = await client.post(
        f"/sheets/strivers-sde-pattern-sheet/items/{item_id}/toggle",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert toggle2.status_code == 200
    res2 = toggle2.json()
    assert res2["is_completed"] is False
    assert res2["completed_questions"] == 0

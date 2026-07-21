async def test_create_quiz(client, host):
    resp = await client.post("/api/v1/quizzes", json={"title": "My Quiz"}, headers=host)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Quiz"
    assert data["status"] == "draft"
    assert data["is_public"] is False
    assert "points_per_correct" not in data


async def test_create_quiz_rejects_blank_title(client, host):
    resp = await client.post("/api/v1/quizzes", json={"title": "   "}, headers=host)
    assert resp.status_code == 400


async def test_create_quiz_requires_auth(client):
    resp = await client.post("/api/v1/quizzes", json={"title": "No Auth Quiz"})
    assert resp.status_code == 401


async def test_list_my_quizzes_only_shows_owner_quizzes(client, auth_headers):
    owner_headers, _ = await auth_headers(email="owner@example.com", nickname="owner1")
    other_headers, _ = await auth_headers(email="other@example.com", nickname="other1")

    await client.post("/api/v1/quizzes", json={"title": "Owner Quiz"}, headers=owner_headers)
    await client.post("/api/v1/quizzes", json={"title": "Other Quiz"}, headers=other_headers)

    resp = await client.get("/api/v1/quizzes", headers=owner_headers)
    assert resp.status_code == 200
    titles = [q["title"] for q in resp.json()]
    assert titles == ["Owner Quiz"]


async def test_get_quiz_owner_can_see_draft(client, host):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "Draft Quiz"}, headers=host)
    quiz_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=host)
    assert resp.status_code == 200


async def test_get_quiz_other_user_cannot_see_draft(client, host, auth_headers):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "Draft Quiz"}, headers=host)
    quiz_id = create_resp.json()["id"]

    other_headers, _ = await auth_headers(email="viewer@example.com", nickname="viewer1")
    resp = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=other_headers)
    assert resp.status_code == 403


async def test_get_quiz_public_ready_visible_without_auth(client, ready_quiz):
    quiz_id = ready_quiz["quiz"]["id"]
    resp = await client.get(f"/api/v1/quizzes/{quiz_id}")
    assert resp.status_code == 200


async def test_get_quiz_private_draft_not_visible_without_auth(client, host):
    create_resp = await client.post(
        "/api/v1/quizzes", json={"title": "Private Draft", "is_public": False}, headers=host
    )
    quiz_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/quizzes/{quiz_id}")
    assert resp.status_code == 403


async def test_get_quiz_not_found(client, host):
    resp = await client.get("/api/v1/quizzes/999999", headers=host)
    assert resp.status_code == 404


async def test_update_quiz(client, host):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "Old Title"}, headers=host)
    quiz_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/v1/quizzes/{quiz_id}", json={"title": "New Title"}, headers=host)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


async def test_update_quiz_rejects_blank_title(client, host):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "Has A Title"}, headers=host)
    quiz_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/v1/quizzes/{quiz_id}", json={"title": "   "}, headers=host)
    assert resp.status_code == 400

    unchanged = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=host)
    assert unchanged.json()["title"] == "Has A Title"


async def test_update_quiz_forbidden_for_non_owner(client, host, auth_headers):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "Owned"}, headers=host)
    quiz_id = create_resp.json()["id"]

    other_headers, _ = await auth_headers(email="notowner@example.com", nickname="notowner1")
    resp = await client.patch(f"/api/v1/quizzes/{quiz_id}", json={"title": "Hijacked"}, headers=other_headers)
    assert resp.status_code == 403


async def test_delete_quiz(client, host):
    create_resp = await client.post("/api/v1/quizzes", json={"title": "To Delete"}, headers=host)
    quiz_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/quizzes/{quiz_id}", headers=host)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=host)
    assert resp.status_code == 404


async def test_discover_hides_private_quiz_sessions(client, host):
    create_resp = await client.post(
        "/api/v1/quizzes", json={"title": "Private Quiz", "is_public": False}, headers=host
    )
    quiz_id = create_resp.json()["id"]
    await client.patch(f"/api/v1/quizzes/{quiz_id}", json={"status": "ready"}, headers=host)
    await client.post(f"/api/v1/quizzes/{quiz_id}/sessions", json={}, headers=host)

    resp = await client.get("/api/v1/quizzes/discover")
    assert resp.status_code == 200
    assert all(item["quiz_id"] != quiz_id for item in resp.json())

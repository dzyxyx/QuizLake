async def test_create_session_requires_ready_quiz(client, host):
    resp = await client.post("/api/v1/quizzes", json={"title": "Draft Quiz"}, headers=host)
    quiz_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/quizzes/{quiz_id}/sessions", json={}, headers=host)
    assert resp.status_code == 400


async def test_create_session_success(client, ready_quiz):
    resp = await client.post(
        f"/api/v1/quizzes/{ready_quiz['quiz']['id']}/sessions",
        json={},
        headers=ready_quiz["host_headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "waiting"
    assert len(data["room_code"]) == 8


async def test_get_session_by_room_code(client, created_session):
    resp = await client.get(f"/api/v1/sessions/{created_session['room_code']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created_session["id"]


async def test_get_session_by_unknown_code(client):
    resp = await client.get("/api/v1/sessions/NOPE0000")
    assert resp.status_code == 404


async def test_join_as_guest(client, created_session):
    resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Guest One"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["display_name"] == "Guest One"
    assert data["user_id"] is None


async def test_join_as_registered_user_twice_is_rejected(client, created_session, auth_headers):
    player_headers, _ = await auth_headers(email="player@example.com", nickname="player1")

    resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Player"},
        headers=player_headers,
    )
    assert resp.status_code == 201

    resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Player Again"},
        headers=player_headers,
    )
    assert resp.status_code == 400


async def test_get_participants(client, created_session):
    await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Guest One"},
    )
    resp = await client.get(f"/api/v1/sessions/{created_session['id']}/participants")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_next_question_starts_and_then_runs_out(client, ready_quiz, created_session):
    session_id = created_session["id"]
    host_headers = ready_quiz["host_headers"]

    resp = await client.post(f"/api/v1/sessions/{session_id}/next-question", headers=host_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == ready_quiz["question"]["id"]

    resp = await client.get(f"/api/v1/sessions/{created_session['room_code']}")
    assert resp.json()["status"] == "active"

    resp = await client.post(f"/api/v1/sessions/{session_id}/next-question", headers=host_headers)
    assert resp.status_code == 400


async def test_next_question_forbidden_for_non_host(client, ready_quiz, created_session, auth_headers):
    other_headers, _ = await auth_headers(email="notthehost@example.com", nickname="notthehost1")
    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/next-question", headers=other_headers
    )
    assert resp.status_code == 403


async def test_discover_feed_shows_waiting_session(client, created_session):
    resp = await client.get("/api/v1/quizzes/discover")
    assert resp.status_code == 200
    session_ids = [item["session_id"] for item in resp.json()]
    assert created_session["id"] in session_ids


async def test_leave_session_removes_participant(client, created_session):
    join_resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Leaver"},
    )
    participant_id = join_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}"
    )
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/sessions/{created_session['id']}/participants")
    assert resp.json() == []


async def test_leave_session_not_allowed_after_start(client, ready_quiz, created_session):
    join_resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Late Leaver"},
    )
    participant_id = join_resp.json()["id"]

    await client.post(
        f"/api/v1/sessions/{created_session['id']}/next-question",
        headers=ready_quiz["host_headers"],
    )

    resp = await client.delete(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}"
    )
    assert resp.status_code == 400


async def test_cancel_session_by_host(client, ready_quiz, created_session):
    resp = await client.delete(
        f"/api/v1/sessions/{created_session['id']}", headers=ready_quiz["host_headers"]
    )
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/sessions/{created_session['room_code']}")
    assert resp.json()["status"] == "cancelled"


async def test_cancel_session_forbidden_for_non_host(client, created_session, auth_headers):
    other_headers, _ = await auth_headers(email="notthehost2@example.com", nickname="notthehost2")
    resp = await client.delete(f"/api/v1/sessions/{created_session['id']}", headers=other_headers)
    assert resp.status_code == 403

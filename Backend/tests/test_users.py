async def test_get_me(client, host):
    resp = await client.get("/api/v1/users/me", headers=host)
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "host1"


async def test_get_me_requires_auth(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_update_me(client, host):
    resp = await client.patch("/api/v1/users/me", json={"first_name": "Updated"}, headers=host)
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"


async def test_update_me_duplicate_nickname_rejected(client, host, auth_headers):
    await auth_headers(email="taken@example.com", nickname="takennick")

    resp = await client.patch("/api/v1/users/me", json={"nickname": "takennick"}, headers=host)
    assert resp.status_code == 400


async def test_stats_are_zero_before_playing(client, host):
    resp = await client.get("/api/v1/users/me/stats", headers=host)
    assert resp.status_code == 200
    assert resp.json() == {
        "played": 0,
        "wins": 0,
        "created": 0,
        "hosted_sessions_count": 0,
        "avg_score_percent": 0,
    }


async def test_stats_and_history_after_finished_game(client, ready_quiz, created_session, auth_headers):
    player_headers, _ = await auth_headers(email="statsplayer@example.com", nickname="statsplayer1")
    join_resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Stats Player"},
        headers=player_headers,
    )
    participant_id = join_resp.json()["id"]

    host_headers = ready_quiz["host_headers"]
    session_id = created_session["id"]

    await client.post(f"/api/v1/sessions/{session_id}/next-question", headers=host_headers)
    await client.post(
        f"/api/v1/sessions/{session_id}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [ready_quiz["correct_option_id"]]},
        headers=player_headers,
    )
    await client.post(f"/api/v1/sessions/{session_id}/reveal-answer", headers=host_headers)
    await client.post(f"/api/v1/sessions/{session_id}/end-game", headers=host_headers)

    stats_resp = await client.get("/api/v1/users/me/stats", headers=player_headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["played"] == 1
    assert stats["wins"] == 1
    assert stats["avg_score_percent"] == 100

    history_resp = await client.get("/api/v1/users/me/participation-history", headers=player_headers)
    history = history_resp.json()
    assert len(history) == 1
    assert history[0]["quiz_title"] == ready_quiz["quiz"]["title"]
    assert history[0]["final_rank"] == 1
    assert history[0]["room_code"] == created_session["room_code"]

    hosted_resp = await client.get("/api/v1/users/me/hosted-history", headers=host_headers)
    hosted = hosted_resp.json()
    assert len(hosted) == 1
    assert hosted[0]["participants_count"] == 1

    host_stats_resp = await client.get("/api/v1/users/me/stats", headers=host_headers)
    host_stats = host_stats_resp.json()
    assert host_stats["created"] == 1
    assert host_stats["hosted_sessions_count"] == 1


async def test_deleting_played_quiz_archives_it_and_keeps_history(
    client, ready_quiz, created_session, auth_headers
):
    player_headers, _ = await auth_headers(email="archiveplayer@example.com", nickname="archiveplayer1")
    join_resp = await client.post(
        f"/api/v1/sessions/{created_session['room_code']}/join",
        json={"display_name": "Archive Player"},
        headers=player_headers,
    )
    participant_id = join_resp.json()["id"]

    host_headers = ready_quiz["host_headers"]
    session_id = created_session["id"]
    quiz_id = ready_quiz["quiz"]["id"]

    await client.post(f"/api/v1/sessions/{session_id}/next-question", headers=host_headers)
    await client.post(
        f"/api/v1/sessions/{session_id}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [ready_quiz["correct_option_id"]]},
        headers=player_headers,
    )
    await client.post(f"/api/v1/sessions/{session_id}/reveal-answer", headers=host_headers)
    await client.post(f"/api/v1/sessions/{session_id}/end-game", headers=host_headers)

    del_resp = await client.delete(f"/api/v1/quizzes/{quiz_id}", headers=host_headers)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/quizzes/{quiz_id}", headers=host_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "archived"

    list_resp = await client.get("/api/v1/quizzes", headers=host_headers)
    assert quiz_id not in [q["id"] for q in list_resp.json()]

    hosted_resp = await client.get("/api/v1/users/me/hosted-history", headers=host_headers)
    assert len(hosted_resp.json()) == 1

    participation_resp = await client.get("/api/v1/users/me/participation-history", headers=player_headers)
    assert len(participation_resp.json()) == 1

    host_stats = (await client.get("/api/v1/users/me/stats", headers=host_headers)).json()
    assert host_stats["created"] == 1
    assert host_stats["hosted_sessions_count"] == 1


async def test_created_counts_only_finished_sessions_not_drafts(client, host, ready_quiz, created_session):
    resp = await client.get("/api/v1/users/me/stats", headers=host)
    assert resp.json()["created"] == 0

    draft_resp = await client.post("/api/v1/quizzes", json={"title": "Черновик"}, headers=host)
    assert draft_resp.status_code == 201

    resp = await client.get("/api/v1/users/me/stats", headers=host)
    assert resp.json()["created"] == 0

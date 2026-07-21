async def _join(client, room_code, display_name="Player"):
    resp = await client.post(f"/api/v1/sessions/{room_code}/join", json={"display_name": display_name})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _start_game(client, session_id, host_headers):
    resp = await client.post(f"/api/v1/sessions/{session_id}/next-question", headers=host_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


async def test_submit_no_active_question_returns_400(client, created_session):
    participant_id = await _join(client, created_session["room_code"])
    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [1]},
    )
    assert resp.status_code == 400


async def test_submit_correct_answer_scores_points(client, ready_quiz, created_session):
    participant_id = await _join(client, created_session["room_code"])
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])

    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [ready_quiz["correct_option_id"]]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_correct"] is True
    assert data["points_awarded"] > 0


async def test_submit_wrong_answer_scores_zero(client, ready_quiz, created_session):
    wrong_option_id = next(
        o["id"] for o in ready_quiz["question"]["answer_options"] if not o["is_correct"]
    )
    participant_id = await _join(client, created_session["room_code"])
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])

    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [wrong_option_id]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_correct"] is False
    assert data["points_awarded"] == 0


async def test_submit_answer_twice_is_rejected(client, ready_quiz, created_session):
    participant_id = await _join(client, created_session["room_code"])
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])

    url = f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer"
    body = {"selected_option_ids": [ready_quiz["correct_option_id"]]}

    first = await client.post(url, json=body)
    assert first.status_code == 201

    second = await client.post(url, json=body)
    assert second.status_code == 400


async def test_reveal_answer_returns_option_stats_and_leaderboard(client, ready_quiz, created_session):
    participant_id = await _join(client, created_session["room_code"])
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])

    await client.post(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [ready_quiz["correct_option_id"]]},
    )

    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/reveal-answer",
        headers=ready_quiz["host_headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert ready_quiz["correct_option_id"] in data["correct_option_ids"]
    correct_stat = next(o for o in data["option_stats"] if o["option_id"] == ready_quiz["correct_option_id"])
    assert correct_stat["selected_count"] == 1
    assert correct_stat["selected_percent"] == 100
    assert data["leaderboard"][0]["participant_id"] == participant_id


async def test_reveal_answer_forbidden_for_non_host(client, ready_quiz, created_session, auth_headers):
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])
    other_headers, _ = await auth_headers(email="revealer@example.com", nickname="revealer1")

    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/reveal-answer", headers=other_headers
    )
    assert resp.status_code == 403


async def test_end_game_sets_final_rank_and_finishes_session(client, ready_quiz, created_session):
    participant_id = await _join(client, created_session["room_code"])
    await _start_game(client, created_session["id"], ready_quiz["host_headers"])
    await client.post(
        f"/api/v1/sessions/{created_session['id']}/participants/{participant_id}/submit-answer",
        json={"selected_option_ids": [ready_quiz["correct_option_id"]]},
    )
    await client.post(
        f"/api/v1/sessions/{created_session['id']}/reveal-answer",
        headers=ready_quiz["host_headers"],
    )

    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/end-game",
        headers=ready_quiz["host_headers"],
    )
    assert resp.status_code == 200
    leaderboard = resp.json()["leaderboard"]
    assert leaderboard[0]["participant_id"] == participant_id
    assert leaderboard[0]["final_rank"] == 1

    resp = await client.get(f"/api/v1/sessions/{created_session['room_code']}")
    assert resp.json()["status"] == "finished"


async def test_end_game_forbidden_for_non_host(client, ready_quiz, created_session, auth_headers):
    other_headers, _ = await auth_headers(email="ender@example.com", nickname="ender1")
    resp = await client.post(
        f"/api/v1/sessions/{created_session['id']}/end-game", headers=other_headers
    )
    assert resp.status_code == 403

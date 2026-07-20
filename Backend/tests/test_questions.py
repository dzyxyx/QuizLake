async def _create_quiz(client, headers, title="Quiz"):
    resp = await client.post("/api/v1/quizzes", json={"title": title}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_create_question_with_options(client, host):
    quiz_id = await _create_quiz(client, host)

    resp = await client.post(
        f"/api/v1/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Capital of France?",
            "question_type": "single",
            "order_index": 1,
            "answer_options": [
                {"option_text": "Paris", "is_correct": True, "order_index": 1},
                {"option_text": "London", "is_correct": False, "order_index": 2},
            ],
        },
        headers=host,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["question_text"] == "Capital of France?"
    assert len(data["answer_options"]) == 2


async def test_create_question_forbidden_for_non_owner(client, host, auth_headers):
    quiz_id = await _create_quiz(client, host)
    other_headers, _ = await auth_headers(email="intruder@example.com", nickname="intruder1")

    resp = await client.post(
        f"/api/v1/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Hijack?",
            "order_index": 1,
            "answer_options": [
                {"option_text": "Yes", "is_correct": True, "order_index": 1},
                {"option_text": "No", "is_correct": False, "order_index": 2},
            ],
        },
        headers=other_headers,
    )
    assert resp.status_code == 403


async def test_create_question_duplicate_order_index(client, host):
    quiz_id = await _create_quiz(client, host)
    body = {
        "question_text": "Q1",
        "order_index": 1,
        "answer_options": [
            {"option_text": "A", "is_correct": True, "order_index": 1},
            {"option_text": "B", "is_correct": False, "order_index": 2},
        ],
    }
    resp = await client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=body, headers=host)
    assert resp.status_code == 201

    body["question_text"] = "Q1 again"
    resp = await client.post(f"/api/v1/quizzes/{quiz_id}/questions", json=body, headers=host)
    assert resp.status_code == 400


async def test_list_questions_ordered(client, host):
    quiz_id = await _create_quiz(client, host)
    for order_index, text in [(2, "Second"), (1, "First")]:
        await client.post(
            f"/api/v1/quizzes/{quiz_id}/questions",
            json={
                "question_text": text,
                "order_index": order_index,
                "answer_options": [
                    {"option_text": "A", "is_correct": True, "order_index": 1},
                    {"option_text": "B", "is_correct": False, "order_index": 2},
                ],
            },
            headers=host,
        )

    resp = await client.get(f"/api/v1/quizzes/{quiz_id}/questions", headers=host)
    assert resp.status_code == 200
    texts = [q["question_text"] for q in resp.json()]
    assert texts == ["First", "Second"]


async def test_update_question_replaces_answer_options(client, host):
    quiz_id = await _create_quiz(client, host)
    create_resp = await client.post(
        f"/api/v1/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Original",
            "order_index": 1,
            "answer_options": [
                {"option_text": "A", "is_correct": True, "order_index": 1},
                {"option_text": "B", "is_correct": False, "order_index": 2},
            ],
        },
        headers=host,
    )
    question_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/quizzes/{quiz_id}/questions/{question_id}",
        json={
            "answer_options": [
                {"option_text": "C", "is_correct": True, "order_index": 1},
                {"option_text": "D", "is_correct": False, "order_index": 2},
                {"option_text": "E", "is_correct": False, "order_index": 3},
            ],
        },
        headers=host,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["answer_options"]) == 3
    assert {o["option_text"] for o in data["answer_options"]} == {"C", "D", "E"}


async def test_delete_question(client, host):
    quiz_id = await _create_quiz(client, host)
    create_resp = await client.post(
        f"/api/v1/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Bye",
            "order_index": 1,
            "answer_options": [
                {"option_text": "A", "is_correct": True, "order_index": 1},
                {"option_text": "B", "is_correct": False, "order_index": 2},
            ],
        },
        headers=host,
    )
    question_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/quizzes/{quiz_id}/questions/{question_id}", headers=host)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/quizzes/{quiz_id}/questions", headers=host)
    assert resp.json() == []

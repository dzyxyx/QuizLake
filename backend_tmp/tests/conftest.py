import os

os.environ.setdefault("POSTGRES_DB", "quizlake_test_db")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.db.base import Base
from app.db.session import engine
from app.db import models as _app_models  # noqa: F401
from app.main import app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def register_user(client):
    async def _factory(
        email="user1@example.com",
        nickname="user1",
        password="secret123",
        first_name="Test",
        last_name="User",
    ):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "nickname": nickname,
                "email": email,
                "password": password,
            },
        )
        assert resp.status_code == 201, resp.text
        return resp.json()

    return _factory


@pytest_asyncio.fixture
def login_user(client):
    async def _factory(email="user1@example.com", password="secret123", remember_me=False):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password, "remember_me": remember_me},
        )
        assert resp.status_code == 200, resp.text
        return resp.json()

    return _factory


@pytest_asyncio.fixture
def auth_headers(register_user, login_user):
    async def _factory(email="user1@example.com", nickname="user1", password="secret123"):
        await register_user(email=email, nickname=nickname, password=password)
        tokens = await login_user(email=email, password=password)
        return {"Authorization": f"Bearer {tokens['access_token']}"}, tokens

    return _factory


@pytest_asyncio.fixture
async def host(auth_headers):
    headers, _tokens = await auth_headers(email="host@example.com", nickname="host1")
    return headers


@pytest_asyncio.fixture
async def ready_quiz(client, host):
    resp = await client.post(
        "/api/v1/quizzes",
        json={"title": "Test Quiz", "is_public": True},
        headers=host,
    )
    assert resp.status_code == 201, resp.text
    quiz = resp.json()

    resp = await client.post(
        f"/api/v1/quizzes/{quiz['id']}/questions",
        json={
            "question_text": "2+2?",
            "question_type": "single",
            "order_index": 1,
            "time_limit_sec": 30,
            "points": 100,
            "answer_options": [
                {"option_text": "4", "is_correct": True, "order_index": 1},
                {"option_text": "5", "is_correct": False, "order_index": 2},
            ],
        },
        headers=host,
    )
    assert resp.status_code == 201, resp.text
    question = resp.json()

    resp = await client.patch(f"/api/v1/quizzes/{quiz['id']}", json={"status": "ready"}, headers=host)
    assert resp.status_code == 200, resp.text
    quiz = resp.json()

    correct_option = next(o for o in question["answer_options"] if o["is_correct"])

    return {
        "quiz": quiz,
        "question": question,
        "correct_option_id": correct_option["id"],
        "host_headers": host,
    }


@pytest_asyncio.fixture
async def created_session(client, ready_quiz):
    resp = await client.post(
        f"/api/v1/quizzes/{ready_quiz['quiz']['id']}/sessions",
        json={"scheduled_start_at": None},
        headers=ready_quiz["host_headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()

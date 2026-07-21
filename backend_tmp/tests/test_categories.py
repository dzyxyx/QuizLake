async def test_get_categories_public(client):
    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

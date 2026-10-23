def test_get_expenses_returns_list(client):
    response = client.get("/expense/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
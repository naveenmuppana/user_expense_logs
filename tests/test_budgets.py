from datetime import datetime, timezone


def _create(client, amount="10.00", category="Food"):
    response = client.post(
        "/expense/",
        json={"title": "x", "amount": amount, "category": category},
    )
    assert response.status_code == 201


def _second_user_headers(client):
    client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "seconduser@example.com",
            "password": "SecondPassword123",
        },
    )
    token = client.post(
        "/auth/login",
        json={
            "email": "seconduser@example.com",
            "password": "SecondPassword123",
        },
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_set_budget_creates_and_normalizes_category(client):
    response = client.put("/budget/Food", json={"amount": "100.00"})

    assert response.status_code == 200
    assert response.json() == {"category": "food", "amount": "100.00"}


def test_set_budget_updates_existing(client):
    client.put("/budget/food", json={"amount": "100.00"})
    client.put("/budget/FOOD", json={"amount": "250.00"})

    budgets = client.get("/budget/").json()

    assert budgets == [{"category": "food", "amount": "250.00"}]


def test_set_budget_rejects_invalid_amount(client):
    for amount in ("0", "-5", "1.234"):
        response = client.put("/budget/food", json={"amount": amount})
        assert response.status_code == 422


def test_delete_budget(client):
    client.put("/budget/food", json={"amount": "100.00"})

    assert client.delete("/budget/Food").status_code == 204
    assert client.get("/budget/").json() == []


def test_delete_missing_budget_returns_404(client):
    response = client.delete("/budget/nothing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget not found"}


def test_budgets_are_isolated_per_user(client):
    client.put("/budget/food", json={"amount": "100.00"})
    headers = _second_user_headers(client)

    assert client.get("/budget/", headers=headers).json() == []
    assert client.delete("/budget/food", headers=headers).status_code == 404


def test_budgets_require_authentication(client):
    client.headers.pop("Authorization", None)

    assert client.get("/budget/").status_code == 401
    assert client.get("/budget/status").status_code == 401
    assert client.put("/budget/food", json={"amount": "1"}).status_code == 401


def test_budget_status_under_budget(client):
    client.put("/budget/food", json={"amount": "100.00"})
    _create(client, amount="30.00", category="Food")
    _create(client, amount="20.00", category="food")
    _create(client, amount="500.00", category="Travel")

    data = client.get("/budget/status").json()

    assert len(data) == 1
    row = data[0]
    assert row["category"] == "food"
    assert float(row["spent"]) == 50.00
    assert float(row["remaining"]) == 50.00
    assert row["over_budget"] is False


def test_budget_status_over_budget(client):
    client.put("/budget/food", json={"amount": "40.00"})
    _create(client, amount="55.00", category="Food")

    row = client.get("/budget/status").json()[0]

    assert float(row["remaining"]) == -15.00
    assert row["over_budget"] is True


def test_budget_status_with_no_spending(client):
    client.put("/budget/food", json={"amount": "40.00"})

    row = client.get("/budget/status").json()[0]

    assert float(row["spent"]) == 0
    assert float(row["remaining"]) == 40.00
    assert row["over_budget"] is False


def test_budget_status_only_counts_requested_month(client):
    client.put("/budget/food", json={"amount": "40.00"})
    _create(client, amount="10.00", category="Food")
    now = datetime.now(timezone.utc)

    this_month = f"{now.year}-{now.month:02d}"
    other_year = f"{now.year - 1}-{now.month:02d}"

    def spent(month):
        response = client.get("/budget/status", params={"month": month})
        return float(response.json()[0]["spent"])

    assert spent(this_month) == 10.00
    assert spent(other_year) == 0


def test_budget_status_rejects_bad_month(client):
    for month in ("2026-13", "2026-00", "26-01", "abc", "1969-12"):
        response = client.get("/budget/status", params={"month": month})
        assert response.status_code == 422, month


def test_budget_status_december_rolls_into_next_year(client):
    client.put("/budget/food", json={"amount": "40.00"})

    response = client.get("/budget/status", params={"month": "2026-12"})

    assert response.status_code == 200

import csv
import io
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def _create(client, title="Lunch", amount="10.00", category="Food"):
    response = client.post(
        "/expense/",
        json={"title": title, "amount": amount, "category": category},
    )
    assert response.status_code == 201
    return response.json()


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


# --- GET /auth/me ---------------------------------------------------------

def test_me_returns_current_user(client):
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"
    assert "hashed_password" not in response.json()


def test_me_requires_authentication(client):
    client.headers.pop("Authorization", None)

    assert client.get("/auth/me").status_code == 401


# --- GET /expense/{id} ----------------------------------------------------

def test_get_expense_by_id(client):
    created = _create(client, title="Coffee", amount="3.50")

    response = client.get(f"/expense/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Coffee"


def test_get_expense_by_id_not_found(client):
    response = client.get("/expense/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}


def test_get_expense_by_id_hides_other_users_expense(client):
    created = _create(client)
    headers = _second_user_headers(client)

    response = client.get(f"/expense/{created['id']}", headers=headers)

    assert response.status_code == 404


# --- listing: pagination, dates, wildcards, precision ---------------------

def test_get_expenses_pagination_offset(client):
    for i in range(3):
        _create(client, title=f"E{i}", amount=f"{i + 1}.00")

    response = client.get(
        "/expense/?sort_by=amount&sort_order=asc&limit=1&offset=1"
    )

    assert [float(e["amount"]) for e in response.json()] == [2.00]


def test_get_expenses_date_filters(client):
    _create(client)
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    after = client.get("/expense/", params={"start_date": tomorrow})
    before = client.get("/expense/", params={"end_date": yesterday})
    within = client.get(
        "/expense/", params={"start_date": yesterday, "end_date": tomorrow}
    )

    assert after.json() == []
    assert before.json() == []
    assert len(within.json()) == 1


def test_category_filter_treats_wildcards_literally(client):
    _create(client, category="Food")
    _create(client, category="Fo_d")

    for pattern in ("%", "F%", "Fo_d"):
        response = client.get("/expense/", params={"category": pattern})
        assert response.status_code == 200

    assert len(client.get("/expense/", params={"category": "%"}).json()) == 0
    assert len(client.get("/expense/", params={"category": "F%"}).json()) == 0
    only = client.get("/expense/", params={"category": "Fo_d"}).json()
    assert [e["category"] for e in only] == ["Fo_d"]


def test_amount_rejects_more_than_two_decimals(client):
    response = client.post(
        "/expense/",
        json={"title": "x", "amount": "1.234", "category": "Food"},
    )

    assert response.status_code == 422


def test_patch_rejects_invalid_values(client):
    created = _create(client)

    for body in ({"amount": "0"}, {"title": ""}, {"amount": "1.234"}):
        response = client.patch(f"/expense/{created['id']}", json=body)
        assert response.status_code == 422


# --- summaries ------------------------------------------------------------

def test_monthly_summary(client):
    _create(client, amount="10.00")
    _create(client, amount="5.50")
    year = datetime.now(timezone.utc).year

    response = client.get("/expense/summary/monthly", params={"year": year})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert float(data[0]["total"]) == 15.50
    assert data[0]["count"] == 2


def test_monthly_summary_requires_year(client):
    assert client.get("/expense/summary/monthly").status_code == 422


def test_category_summary_groups_case_insensitively(client):
    _create(client, amount="10.00", category="Food")
    _create(client, amount="5.00", category="food")
    _create(client, amount="100.00", category="Travel")

    response = client.get("/expense/summary/categories")

    assert response.status_code == 200
    data = response.json()
    assert [row["category"] for row in data] == ["travel", "food"]
    assert float(data[1]["total"]) == 15.00
    assert data[1]["count"] == 2


def test_category_summary_isolated_per_user(client):
    _create(client)
    headers = _second_user_headers(client)

    response = client.get("/expense/summary/categories", headers=headers)

    assert response.json() == []


def test_category_summary_rejects_invalid_date_range(client):
    response = client.get(
        "/expense/summary/categories",
        params={
            "start_date": "2026-10-25T12:00:00",
            "end_date": "2026-10-24T12:00:00",
        },
    )

    assert response.status_code == 422


# --- export ---------------------------------------------------------------

def test_export_returns_csv(client):
    _create(client, title="Lunch", amount="10.00", category="Food")

    response = client.get("/expense/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    rows = list(csv.reader(io.StringIO(response.text)))
    assert rows[0] == ["id", "title", "amount", "category", "created_at"]
    assert rows[1][1:4] == ["Lunch", "10.00", "Food"]


def test_export_neutralises_formula_injection(client):
    _create(client, title="=SUM(A1)", category="Food")

    rows = list(csv.reader(io.StringIO(client.get("/expense/export").text)))

    assert rows[1][1] == "'=SUM(A1)"


def test_export_only_includes_own_expenses(client):
    _create(client)
    headers = _second_user_headers(client)

    response = client.get("/expense/export", headers=headers)

    assert len(list(csv.reader(io.StringIO(response.text)))) == 1


def test_export_rejects_invalid_amount_range(client):
    response = client.get("/expense/export?min_amount=500&max_amount=100")

    assert response.status_code == 422


# --- auth gaps ------------------------------------------------------------

def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "Whatever123"},
    )

    assert response.status_code == 401


def test_expense_rejects_expired_token(client):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "1", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.get(
        "/expense/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"
    assert "hashed_password" not in response.json()


def test_register_duplicate_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 409


def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_expense_requires_authentication(client):
    client.headers.pop("Authorization", None)

    response = client.get("/expense/")

    assert response.status_code == 401


def test_expense_rejects_invalid_token(client):
    response = client.get(
        "/expense/",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_user_cannot_access_another_users_expenses(client):
    # User 1 creates an expense using the default test token.
    create_response = client.post(
        "/expense/",
        json={
            "title": "User One Expense",
            "amount": "500.00",
            "category": "Food",
        },
    )

    assert create_response.status_code == 201

    # Register User 2.
    register_response = client.post(
        "/auth/register",
        json={
            "username": "seconduser",
            "email": "seconduser@example.com",
            "password": "SecondPassword123",
        },
    )

    assert register_response.status_code == 201

    # Log in as User 2.
    login_response = client.post(
        "/auth/login",
        json={
            "email": "seconduser@example.com",
            "password": "SecondPassword123",
        },
    )

    assert login_response.status_code == 200

    second_user_token = login_response.json()["access_token"]

    # User 2 attempts to retrieve expenses.
    response = client.get(
        "/expense/",
        headers={
            "Authorization": f"Bearer {second_user_token}"
        },
    )

    assert response.status_code == 200
    assert response.json() == []

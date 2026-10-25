def test_get_expenses_returns_list(client):
    response = client.get("/expense/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    

def test_create_expense(client):
    payload = {
        "title": "Lunch",
        "amount": "250.00",
        "category": "Food"
    }

    response = client.post("/expense/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Lunch"
    assert float(data["amount"]) == 250.00
    assert data["category"] == "Food"
    assert "id" in data



def test_create_expense_rejects_zero_amount(client):
    payload = {
        "title": "Invalid Expense",
        "amount": "0.00",
        "category": "Food"
    }

    response = client.post("/expense/", json=payload)

    assert response.status_code == 422


def test_get_expenses_respects_limit(client):
    response = client.get("/expense/?limit=1&offset=0")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 1



# def test_get_expenses_filters_by_category(client):
#     response = client.get("/expense/?category=Food")

#     assert response.status_code == 200

#     expenses = response.json()
#     assert isinstance(expenses, list)

#     for expense in expenses:
#         assert expense["category"].lower() == "food"



# def test_get_expenses_filters_by_amount(client):
#     response = client.get(
#         "/expense/?min_amount=100&max_amount=500"
#     )

#     assert response.status_code == 200

#     expenses = response.json()
#     assert isinstance(expenses, list)

#     for expense in expenses:
#         amount = float(expense["amount"])
#         assert amount >= 100
#         assert amount <= 500




def test_get_expenses_filters_by_amount(client):
    test_expenses = [
        {"title": "Cheap", "amount": "50.00", "category": "Testing"},
        {"title": "Medium", "amount": "250.00", "category": "Testing"},
        {"title": "Expensive", "amount": "600.00", "category": "Testing"},
    ]

    for payload in test_expenses:
        response = client.post("/expense/", json=payload)
        assert response.status_code == 201

    response = client.get(
        "/expense/?min_amount=100&max_amount=500"
    )

    assert response.status_code == 200

    expenses = response.json()
    amounts = [float(expense["amount"]) for expense in expenses]

    assert amounts == [250.00]



def test_get_expenses_sorts_by_amount_ascending(client):
    for title, amount in [
        ("Expense C", "300.00"),
        ("Expense A", "100.00"),
        ("Expense B", "200.00"),
    ]:
        response = client.post(
            "/expense/",
            json={
                "title": title,
                "amount": amount,
                "category": "Testing",
            },
        )
        assert response.status_code == 201

    response = client.get(
        "/expense/?sort_by=amount&sort_order=asc"
    )

    assert response.status_code == 200

    expenses = response.json()
    amounts = [float(expense["amount"]) for expense in expenses]

    assert amounts == [100.00, 200.00, 300.00]




def test_get_expenses_filters_by_category(client):
    test_expenses = [
        {"title": "Lunch", "amount": "250.00", "category": "Food"},
        {"title": "Bus", "amount": "50.00", "category": "Travel"},
        {"title": "Dinner", "amount": "300.00", "category": "Food"},
    ]

    for payload in test_expenses:
        response = client.post("/expense/", json=payload)
        assert response.status_code == 201

    response = client.get("/expense/?category=Food")

    assert response.status_code == 200

    expenses = response.json()
    assert len(expenses) == 2
    assert all(item["category"].lower() == "food" for item in expenses)

def test_put_replaces_expense(client):
    # Arrange: create an expense
    create_response = client.post(
        "/expense/",
        json={
            "title": "Old Lunch",
            "amount": "100.00",
            "category": "Food",
        },
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    # Act: replace all editable fields
    response = client.put(
        f"/expense/{expense_id}",
        json={
            "title": "New Lunch",
            "amount": "200.00",
            "category": "Dining",
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Lunch"
    assert float(data["amount"]) == 200.00
    assert data["category"] == "Dining"


def test_put_returns_404_for_missing_expense(client):
    response = client.put(
        "/expense/999999",
        json={
            "title": "Updated",
            "amount": "200.00",
            "category": "Food",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


def test_patch_updates_only_provided_fields(client):
    # Arrange
    create_response = client.post(
        "/expense/",
        json={
            "title": "Bus Ticket",
            "amount": "50.00",
            "category": "Travel",
        },
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    # Act: change only the amount
    response = client.patch(
        f"/expense/{expense_id}",
        json={"amount": "75.00"},
    )

    # Assert: other fields remain unchanged
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Bus Ticket"
    assert float(data["amount"]) == 75.00
    assert data["category"] == "Travel"


def test_patch_returns_404_for_missing_expense(client):
    response = client.patch(
        "/expense/999999",
        json={"title": "Updated"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


# def test_delete_expense(client):
#     # Arrange
#     create_response = client.post(
#         "/expense/",
#         json={
#             "title": "Movie Ticket",
#             "amount": "300.00",
#             "category": "Entertainment",
#         },
#     )
#     assert create_response.status_code == 201
#     expense_id = create_response.json()["id"]

#     # Act
#     response = client.delete(f"/expense/{expense_id}")

#     # Assert
#     assert response.status_code == 204
#     assert response.content == b""

#     # Verify the expense is actually gone
#     get_response = client.get(f"/expense/{expense_id}")
#     assert get_response.status_code == 404



def test_delete_expense(client):
    # Arrange: create an expense
    create_response = client.post(
        "/expense/",
        json={
            "title": "Movie Ticket",
            "amount": "300.00",
            "category": "Entertainment",
        },
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    # Act: delete the expense
    response = client.delete(f"/expense/{expense_id}")

    # Assert: deletion succeeded with no response body
    assert response.status_code == 204
    assert response.content == b""

    # Verify: the deleted expense is absent from the list
    list_response = client.get("/expense/?limit=100")
    assert list_response.status_code == 200

    returned_ids = [item["id"] for item in list_response.json()]
    assert expense_id not in returned_ids

def test_delete_expense_not_found(client):
    response = client.delete("/expense/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Expense not found"
    }

def test_get_expenses_rejects_invalid_amount_range(client):
    response = client.get(
        "/expense/?min_amount=500&max_amount=100"
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "min_amount cannot exceed max_amount"
    )


def test_get_expenses_rejects_invalid_date_range(client):
    response = client.get(
        "/expense/"
        "?start_date=2026-10-25T12:00:00"
        "&end_date=2026-10-24T12:00:00"
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "start_date cannot be later than end_date"
    )


def test_get_expenses_rejects_limit_above_maximum(client):
    response = client.get("/expense/?limit=101")

    assert response.status_code == 422


def test_get_expenses_rejects_invalid_sort_field(client):
    response = client.get("/expense/?sort_by=category")

    assert response.status_code == 422




from app.ai.predictor import predict_category


VALID_CATEGORIES = {
    "technical_issue",
    "billing",
    "account_access",
    "general_inquiry",
}


def test_predict_category_returns_valid_result():
    result = predict_category(
        title="Payment deducted twice",
        description=(
            "My bank account was charged twice "
            "for the same monthly subscription."
        ),
    )

    assert result["category"] in VALID_CATEGORIES
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_category_returns_numeric_confidence():
    result = predict_category(
        title="Cannot log into my account",
        description=(
            "I enter my correct password but "
            "cannot access my account."
        ),
    )

    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_category_handles_empty_text():
    result = predict_category(
        title="",
        description="",
    )

    assert result["category"] in VALID_CATEGORIES


def test_predict_category_endpoint(client):
    response = client.post(
        "/ai/predict-category",
        json={
            "title": "Payment deducted twice",
            "description": (
                "My bank account was charged twice "
                "for the same monthly subscription."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["category"] in VALID_CATEGORIES
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_category_endpoint_rejects_invalid_input(client):
    response = client.post(
        "/ai/predict-category",
        json={
            "title": "Hi",
            "description": "Too short",
        },
    )

    assert response.status_code == 422

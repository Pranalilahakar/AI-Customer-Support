
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
from app.core.security import create_access_token
from app.models import Ticket, User


def _create_ai_test_user(db_session, email, role):
    user = User(
        full_name=f"AI Test {role}",
        email=email,
        password_hash="not-used-for-token-tests",
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _ai_auth_headers(user):
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def test_ticket_summary_requires_authentication(client):
    response = client.get("/ai/tickets/1/summary")
    assert response.status_code in (401, 403)


def test_ticket_summary_returns_ticket_content(client, db_session):
    customer = _create_ai_test_user(
        db_session, "ai-summary-customer@example.com", "customer"
    )
    ticket = Ticket(
        title="Payment issue",
        description="My payment was charged twice for one order.",
        priority="high",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    headers = _ai_auth_headers(customer)
    comment_response = client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={"body": "I checked my bank statement."},
    )
    assert comment_response.status_code == 201

    response = client.get(
        f"/ai/tickets/{ticket.id}/summary",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket.id
    assert "Payment issue" in data["summary"]
    assert "charged twice" in data["summary"]
    assert data["comment_count"] == 1
    assert "bank statement" in data["summary"]


def test_customer_cannot_request_reply_suggestion(client, db_session):
    customer = _create_ai_test_user(
        db_session, "ai-reply-customer@example.com", "customer"
    )
    ticket = Ticket(
        title="Login problem",
        description="I cannot log into my account after a password reset.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/suggest-reply",
        headers=_ai_auth_headers(customer),
    )

    assert response.status_code == 403


def test_agent_can_request_reply_suggestion(client, db_session):
    customer = _create_ai_test_user(
        db_session, "ai-reply-owner@example.com", "customer"
    )
    agent = _create_ai_test_user(
        db_session, "ai-reply-agent@example.com", "agent"
    )
    ticket = Ticket(
        title="Cannot sign in",
        description="I cannot sign in after resetting my password.",
        priority="high",
        status="open",
        created_by=customer.id,
        assigned_to=agent.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/suggest-reply",
        headers=_ai_auth_headers(agent),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket.id
    assert data["generated_by"] == "template"
    assert data["requires_agent_review"] is True
    assert "Cannot sign in" in data["draft"]


def test_ticket_summary_rejects_inaccessible_ticket(client, db_session):
    owner = _create_ai_test_user(
        db_session, "ai-summary-owner@example.com", "customer"
    )
    other_customer = _create_ai_test_user(
        db_session, "ai-summary-other@example.com", "customer"
    )
    ticket = Ticket(
        title="Private ticket",
        description="This ticket belongs to another customer.",
        priority="low",
        status="open",
        created_by=owner.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/summary",
        headers=_ai_auth_headers(other_customer),
    )

    assert response.status_code == 403


def test_knowledge_search_requires_authentication(client):
    response = client.get(
        "/ai/knowledge-search",
        params={"q": "duplicate charge refund"},
    )

    assert response.status_code in (401, 403)


def test_knowledge_search_returns_relevant_guidance(client, db_session):
    user = _create_ai_test_user(
        db_session, "ai-knowledge-user@example.com", "customer"
    )

    response = client.get(
        "/ai/knowledge-search",
        params={"q": "duplicate charge refund"},
        headers=_ai_auth_headers(user),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "duplicate charge refund"
    assert len(data["results"]) >= 1

    first_result = data["results"][0]
    assert first_result["source"].endswith(".md")
    assert first_result["passage"]
    assert first_result["score"] > 0
    assert "Verify guidance" in data["message"]


def test_knowledge_search_rejects_empty_query(client, db_session):
    user = _create_ai_test_user(
        db_session, "ai-knowledge-validation@example.com", "agent"
    )

    response = client.get(
        "/ai/knowledge-search",
        params={"q": ""},
        headers=_ai_auth_headers(user),
    )

    assert response.status_code == 422


def test_priority_recommendation_requires_authentication(client, db_session):
    customer = _create_ai_test_user(
        db_session, "ai-priority-auth@example.com", "customer"
    )

    ticket = Ticket(
        title="Production outage",
        description="All users cannot access the service.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/priority-recommendation"
    )

    assert response.status_code in (401, 403)


def test_priority_recommendation_returns_explanation(client, db_session):
    customer = _create_ai_test_user(
        db_session, "ai-priority-owner@example.com", "customer"
    )

    ticket = Ticket(
        title="Production outage",
        description="All users cannot access the service.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/priority-recommendation",
        headers=_ai_auth_headers(customer),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recommended_priority"] == "urgent"
    assert data["method"] == "keyword_rules"
    assert data["requires_human_review"] is True
    assert data["reasons"]
    assert "not a prediction" in data["notice"]

    # A recommendation must not automatically modify the ticket.
    db_session.refresh(ticket)
    assert ticket.priority == "medium"


def test_priority_recommendation_rejects_inaccessible_ticket(
    client, db_session
):
    owner = _create_ai_test_user(
        db_session, "ai-priority-private-owner@example.com", "customer"
    )
    other_customer = _create_ai_test_user(
        db_session, "ai-priority-private-other@example.com", "customer"
    )

    ticket = Ticket(
        title="Production outage",
        description="All users cannot access the service.",
        priority="high",
        status="open",
        created_by=owner.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/ai/tickets/{ticket.id}/priority-recommendation",
        headers=_ai_auth_headers(other_customer),
    )

    assert response.status_code == 403

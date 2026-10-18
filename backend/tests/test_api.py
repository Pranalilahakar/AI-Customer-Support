
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.models import User, Ticket


def register_customer(client: TestClient, email="customer@example.com"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Customer",
            "email": email,
            "password": "TestPass123!",
        },
    )
    return response


def login_customer(client: TestClient, email="customer@example.com"):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_user(db_session, email, role):
    user = User(
        full_name=f"Test {role.title()}",
        email=email,
        password_hash=hash_password("TestPass123!"),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_headers(user):
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def create_test_ticket(client, token):
    response = client.post(
        "/tickets/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Cannot access my account",
            "description": "I cannot log in to my account after resetting my password.",
            "category": "Account",
            "priority": "high",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_customer_registration(client):
    response = register_customer(client)

    assert response.status_code == 201
    assert response.json()["email"] == "customer@example.com"
    assert response.json()["role"] == "customer"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_duplicate_registration_is_rejected(client):
    register_customer(client)

    response = register_customer(client)

    assert response.status_code == 409


def test_login_and_current_user(client):
    register_customer(client)
    token = login_customer(client)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "customer@example.com"


def test_current_user_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_customer_can_create_and_view_own_ticket(client):
    register_customer(client)
    token = login_customer(client)

    ticket = create_test_ticket(client, token)

    assert ticket["title"] == "Cannot access my account"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "open"

    response = client.get(
        "/tickets/my-tickets",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert any(item["id"] == ticket["id"] for item in response.json())


def test_customer_cannot_update_ticket_status(client):
    register_customer(client)
    token = login_customer(client)
    ticket = create_test_ticket(client, token)

    response = client.patch(
        f"/tickets/{ticket['id']}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "in_progress"},
    )

    assert response.status_code == 403


def test_customer_can_add_and_read_ticket_comments(client):
    register_customer(client)
    token = login_customer(client)
    ticket = create_test_ticket(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        f"/tickets/{ticket['id']}/comments",
        headers=headers,
        json={"body": "I have already tried resetting my password."},
    )

    assert create_response.status_code == 201
    assert create_response.json()["body"] == (
        "I have already tried resetting my password."
    )

    read_response = client.get(
        f"/tickets/{ticket['id']}/comments",
        headers=headers,
    )

    assert read_response.status_code == 200
    assert len(read_response.json()) == 1


def test_agent_can_update_assigned_ticket(client, db_session):
    customer = create_user(
        db_session, "owner@example.com", "customer"
    )
    agent = create_user(
        db_session, "agent@example.com", "agent"
    )

    ticket = Ticket(
        title="Test assigned ticket",
        description="This is a test ticket assigned to an agent.",
        priority="medium",
        status="open",
        created_by=customer.id,
        assigned_to=agent.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.patch(
        f"/tickets/{ticket.id}/status",
        headers=auth_headers(agent),
        json={"status": "in_progress"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "in_progress"


def test_admin_can_assign_ticket_to_agent(client, db_session):
    customer = create_user(
        db_session, "owner2@example.com", "customer"
    )
    admin = create_user(
        db_session, "admin@example.com", "admin"
    )
    agent = create_user(
        db_session, "agent2@example.com", "agent"
    )

    ticket = Ticket(
        title="Ticket awaiting assignment",
        description="This ticket needs to be assigned to a support agent.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.post(
        f"/tickets/{ticket.id}/assign",
        headers=auth_headers(admin),
        json={"assigned_to": agent.id},
    )

    assert response.status_code == 200, response.text
    assert response.json()["assigned_to"] == agent.id


def test_invalid_login_is_rejected(client):
    register_customer(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "customer@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_inactive_user_cannot_login(client, db_session):
    user = create_user(
        db_session, "inactive@example.com", "customer"
    )
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 403


def test_agent_cannot_update_unassigned_ticket(client, db_session):
    customer = create_user(
        db_session, "owner3@example.com", "customer"
    )
    agent = create_user(
        db_session, "agent3@example.com", "agent"
    )

    ticket = Ticket(
        title="Unassigned ticket",
        description="This ticket is not assigned to this agent.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.patch(
        f"/tickets/{ticket.id}/status",
        headers=auth_headers(agent),
        json={"status": "in_progress"},
    )

    assert response.status_code == 403


def test_customer_cannot_access_another_customers_comments(
    client, db_session
):
    owner = create_user(
        db_session, "owner4@example.com", "customer"
    )
    other_customer = create_user(
        db_session, "other@example.com", "customer"
    )

    ticket = Ticket(
        title="Private customer ticket",
        description="Only its owner and authorized staff can access it.",
        priority="medium",
        status="open",
        created_by=owner.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        f"/tickets/{ticket.id}/comments",
        headers=auth_headers(other_customer),
    )

    assert response.status_code == 403


def test_admin_cannot_assign_ticket_to_customer(
    client, db_session
):
    customer = create_user(
        db_session, "owner5@example.com", "customer"
    )
    admin = create_user(
        db_session, "admin2@example.com", "admin"
    )
    target_customer = create_user(
        db_session, "target@example.com", "customer"
    )

    ticket = Ticket(
        title="Assignment validation",
        description="This ticket is used to validate assignment rules.",
        priority="medium",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.post(
        f"/tickets/{ticket.id}/assign",
        headers=auth_headers(admin),
        json={"assigned_to": target_customer.id},
    )

    assert response.status_code == 422


def test_whitespace_only_comment_is_rejected(client):
    register_customer(client)
    token = login_customer(client)
    ticket = create_test_ticket(client, token)

    response = client.post(
        f"/tickets/{ticket['id']}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"body": "   "},
    )

    assert response.status_code == 422

def test_admin_can_view_all_customer_tickets(client, db_session):
    customer = create_user(
        db_session, "admin-list-owner@example.com", "customer"
    )
    admin = create_user(
        db_session, "admin-list@example.com", "admin"
    )

    ticket = Ticket(
        title="Customer ticket for admin",
        description="This ticket must appear in the admin ticket list.",
        priority="high",
        status="open",
        created_by=customer.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    response = client.get(
        "/tickets/admin/all",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200, response.text
    assert any(item["id"] == ticket.id for item in response.json())


def test_customer_cannot_view_admin_ticket_list(client):
    register_customer(client)
    token = login_customer(client)

    response = client.get(
        "/tickets/admin/all",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_list_active_agents(client, db_session):
    admin = create_user(
        db_session, "agent-directory-admin@example.com", "admin"
    )
    active_agent = create_user(
        db_session, "active-agent@example.com", "agent"
    )
    inactive_agent = create_user(
        db_session, "inactive-agent@example.com", "agent"
    )
    inactive_agent.is_active = False
    db_session.commit()

    response = client.get(
        "/tickets/agents",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200, response.text
    agents = response.json()

    assert any(item["id"] == active_agent.id for item in agents)
    assert all(item["id"] != inactive_agent.id for item in agents)
    assert all("password_hash" not in item for item in agents)


def test_non_admin_cannot_list_agents(client):
    register_customer(client)
    token = login_customer(client)

    response = client.get(
        "/tickets/agents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
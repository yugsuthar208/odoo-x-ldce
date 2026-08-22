import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session_factory
from app.models.user import User
from app.models.trip import Trip
from app.models.trip_collaborator import TripCollaborator
from app.middleware.auth import create_access_token, hash_password


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_users():
    """Creates owner, editor, and viewer test users with JWT tokens."""
    async with async_session_factory() as session:
        owner = User(
            id=str(uuid.uuid4()),
            email=f"owner_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=hash_password("OwnerPassword123!"),
            name="Alice Owner",
        )
        editor = User(
            id=str(uuid.uuid4()),
            email=f"editor_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=hash_password("EditorPassword123!"),
            name="Bob Editor",
        )
        viewer = User(
            id=str(uuid.uuid4()),
            email=f"viewer_{uuid.uuid4().hex[:6]}@example.com",
            password_hash=hash_password("ViewerPassword123!"),
            name="Charlie Viewer",
        )
        session.add_all([owner, editor, viewer])
        await session.commit()

        owner_token = create_access_token({"sub": owner.id, "email": owner.email})
        editor_token = create_access_token({"sub": editor.id, "email": editor.email})
        viewer_token = create_access_token({"sub": viewer.id, "email": viewer.email})

        return {
            "owner": owner,
            "owner_token": owner_token,
            "editor": editor,
            "editor_token": editor_token,
            "viewer": viewer,
            "viewer_token": viewer_token,
        }


@pytest.mark.anyio
async def test_observability_correlation_id_and_metrics(client: AsyncClient):
    """Verifies correlation ID is returned in headers and /metrics exposes Prometheus stats."""
    # 1. Test correlation ID generation
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert "x-correlation-id" in resp.headers
    assert len(resp.headers["x-correlation-id"]) > 10

    # 2. Test Prometheus /metrics endpoint
    metrics_resp = await client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert "text/plain" in metrics_resp.headers["content-type"]
    assert b"globetrotter_" in metrics_resp.content


@pytest.mark.anyio
async def test_oauth_social_endpoints(client: AsyncClient):
    """Tests OAuth2 authorize URL generator and callback exchange."""
    # 1. Google Authorize URL
    resp = await client.get("/api/auth/oauth/google/authorize")
    assert resp.status_code == 200
    data = resp.json()
    assert "accounts.google.com" in data["authorization_url"]

    # 2. GitHub Authorize URL
    resp_gh = await client.get("/api/auth/oauth/github/authorize")
    assert resp_gh.status_code == 200
    data_gh = resp_gh.json()
    assert "github.com/login/oauth/authorize" in data_gh["authorization_url"]

    # 3. Exchange mock OAuth code
    callback_resp = await client.post(
        "/api/auth/oauth/callback",
        json={
            "provider": "google",
            "code": f"test_code_{uuid.uuid4().hex}",
            "mock_email": f"google_traveler_{uuid.uuid4().hex[:6]}@gmail.com",
            "mock_name": "Google Traveler",
        }
    )
    assert callback_resp.status_code == 200
    oauth_data = callback_resp.json()
    assert "access_token" in oauth_data
    assert oauth_data["user"]["name"] == "Google Traveler"


@pytest.mark.anyio
async def test_rbac_and_audit_logging(client: AsyncClient, test_users: dict):
    """Tests Granular RBAC permissions (Owner vs Editor vs Viewer) and Audit Logs."""
    owner_token = test_users["owner_token"]
    editor_token = test_users["editor_token"]
    viewer_token = test_users["viewer_token"]
    owner = test_users["owner"]
    editor = test_users["editor"]
    viewer = test_users["viewer"]

    # 1. Owner creates a trip
    create_resp = await client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Tokyo & Kyoto Explorer",
            "description": "Multi-city journey across Japan",
            "start_date": "2026-10-01",
            "end_date": "2026-10-15",
            "total_budget": 5000.0,
            "currency": "USD",
            "visibility": "private",
        }
    )
    assert create_resp.status_code == 201
    trip_id = create_resp.json()["data"]["id"]

    # 2. Owner adds editor and viewer collaborators
    add_ed_resp = await client.post(
        f"/api/trips/{trip_id}/collaborators",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"email": editor.email, "role": "editor"}
    )
    assert add_ed_resp.status_code == 201

    add_vw_resp = await client.post(
        f"/api/trips/{trip_id}/collaborators",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"email": viewer.email, "role": "viewer"}
    )
    assert add_vw_resp.status_code == 201

    # 3. Viewer attempts to update trip -> Should fail with 403
    vw_update_resp = await client.put(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"title": "Hacked Title by Viewer"}
    )
    assert vw_update_resp.status_code == 403

    # 4. Editor updates trip -> Should succeed
    ed_update_resp = await client.put(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {editor_token}"},
        json={"title": "Tokyo & Kyoto Adventure"}
    )
    assert ed_update_resp.status_code == 200
    assert ed_update_resp.json()["data"]["title"] == "Tokyo & Kyoto Adventure"

    # 5. Editor logs an expense -> Should succeed
    exp_resp = await client.post(
        f"/api/trips/{trip_id}/expenses",
        headers={"Authorization": f"Bearer {editor_token}"},
        json={
            "category": "transport",
            "description": "Shinkansen Bullet Train",
            "actual_amount": 350.0,
            "currency": "USD"
        }
    )
    assert exp_resp.status_code == 201

    # 6. Check Audit Logs (Editor or Owner can view)
    audit_resp = await client.get(
        f"/api/trips/{trip_id}/audit-logs",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 3  # TRIP_CREATED, COLLABORATOR_ADDED, TRIP_UPDATED, EXPENSE_CREATED
    actions = [l["action"] for l in logs]
    assert "TRIP_CREATED" in actions
    assert "TRIP_UPDATED" in actions

    # 7. Viewer attempts to delete trip -> 403
    vw_del_resp = await client.delete(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert vw_del_resp.status_code == 403

    # 8. Editor attempts to delete trip -> 403 (Owner only)
    ed_del_resp = await client.delete(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert ed_del_resp.status_code == 403


@pytest.mark.anyio
async def test_notifications_lifecycle(client: AsyncClient, test_users: dict):
    """Tests notification listing and mark as read functionality."""
    owner_token = test_users["owner_token"]
    editor = test_users["editor"]
    editor_token = test_users["editor_token"]

    # 1. Owner creates trip and invites editor, which triggers a real notification
    create_resp = await client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Swiss Alps Tour",
            "description": "Hiking and sightseeing",
            "start_date": "2026-11-01",
            "end_date": "2026-11-10",
            "total_budget": 3000.0,
            "currency": "USD",
        }
    )
    assert create_resp.status_code == 201
    trip_id = create_resp.json()["data"]["id"]

    add_resp = await client.post(
        f"/api/trips/{trip_id}/collaborators",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"email": editor.email, "role": "editor"}
    )
    assert add_resp.status_code == 201

    # 2. Editor fetches notifications
    notif_resp = await client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()
    assert len(notifs) >= 1
    target_id = notifs[0]["id"]

    # 3. Mark notification as read
    read_resp = await client.patch(
        f"/api/notifications/{target_id}/read",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # 4. Mark all as read
    read_all_resp = await client.post(
        "/api/notifications/read-all",
        headers={"Authorization": f"Bearer {editor_token}"}
    )
    assert read_all_resp.status_code == 200
    assert "Marked" in read_all_resp.json()["message"]


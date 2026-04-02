"""Tests for /users — admin user management."""

from fastapi.testclient import TestClient

from tests.conftest import auth_header, register_and_login


class TestListUsers:
    def test_admin_can_list_users(self, client: TestClient):
        admin = register_and_login(client, "admin", "pass123", "admin")
        register_and_login(client, "alice", "pass123", "viewer")
        resp = client.get("/users/", headers=auth_header(admin))
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_viewer_cannot_list_users(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        assert client.get("/users/", headers=auth_header(viewer)).status_code == 403

    def test_analyst_cannot_list_users(self, client: TestClient):
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        assert client.get("/users/", headers=auth_header(analyst)).status_code == 403


class TestUpdateRole:
    def test_admin_can_change_role(self, client: TestClient):
        admin   = register_and_login(client, "admin", "pass123", "admin")
        register_and_login(client, "alice", "pass123", "viewer")

        users   = client.get("/users/", headers=auth_header(admin)).json()
        alice   = next(u for u in users if u["username"] == "alice")
        resp    = client.patch(
            f"/users/{alice['id']}/role",
            json={"role": "analyst"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "analyst"

    def test_admin_cannot_change_own_role(self, client: TestClient):
        admin    = register_and_login(client, "admin", "pass123", "admin")
        admin_id = client.get("/auth/me", headers=auth_header(admin)).json()["id"]
        resp     = client.patch(
            f"/users/{admin_id}/role",
            json={"role": "viewer"},
            headers=auth_header(admin),
        )
        assert resp.status_code == 400

    def test_update_nonexistent_user(self, client: TestClient):
        admin = register_and_login(client, "admin", "pass123", "admin")
        resp  = client.patch("/users/9999/role", json={"role": "analyst"}, headers=auth_header(admin))
        assert resp.status_code == 404


class TestDeleteUser:
    def test_admin_can_delete_user(self, client: TestClient):
        admin   = register_and_login(client, "admin", "pass123", "admin")
        register_and_login(client, "alice", "pass123", "viewer")

        users   = client.get("/users/", headers=auth_header(admin)).json()
        alice   = next(u for u in users if u["username"] == "alice")
        resp    = client.delete(f"/users/{alice['id']}", headers=auth_header(admin))
        assert resp.status_code == 200

        # Confirm deletion
        after = client.get("/users/", headers=auth_header(admin)).json()
        assert all(u["username"] != "alice" for u in after)

    def test_admin_cannot_self_delete(self, client: TestClient):
        admin    = register_and_login(client, "admin", "pass123", "admin")
        admin_id = client.get("/auth/me", headers=auth_header(admin)).json()["id"]
        resp     = client.delete(f"/users/{admin_id}", headers=auth_header(admin))
        assert resp.status_code == 400

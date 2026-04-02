"""Tests for /transactions — CRUD, filters, and role enforcement."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_header, register_and_login, SAMPLE_TX


def _create_tx(client, token, payload=None):
    return client.post("/transactions/", json=payload or SAMPLE_TX, headers=auth_header(token))


class TestCreateTransaction:
    def test_admin_can_create(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        resp  = _create_tx(client, token)
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"]   == 5000.0
        assert data["type"]     == "income"
        assert data["category"] == "Salary"

    def test_category_is_titlecased(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        resp  = _create_tx(client, token, {**SAMPLE_TX, "category": "food & dining"})
        assert resp.json()["category"] == "Food & Dining"

    def test_viewer_cannot_create(self, client: TestClient):
        token = register_and_login(client, "viewer", "pass123", "viewer")
        assert _create_tx(client, token).status_code == 403

    def test_analyst_cannot_create(self, client: TestClient):
        token = register_and_login(client, "analyst", "pass123", "analyst")
        assert _create_tx(client, token).status_code == 403

    def test_negative_amount_rejected(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        resp  = _create_tx(client, token, {**SAMPLE_TX, "amount": -100})
        assert resp.status_code == 422

    def test_zero_amount_rejected(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        resp  = _create_tx(client, token, {**SAMPLE_TX, "amount": 0})
        assert resp.status_code == 422

    def test_invalid_type_rejected(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        resp  = _create_tx(client, token, {**SAMPLE_TX, "type": "donation"})
        assert resp.status_code == 422

    def test_unauthenticated_cannot_create(self, client: TestClient):
        resp = client.post("/transactions/", json=SAMPLE_TX)
        assert resp.status_code == 401


class TestReadTransaction:
    def test_viewer_can_list(self, client: TestClient):
        admin  = register_and_login(client, "admin",  "pass123", "admin")
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        _create_tx(client, admin)
        resp = client.get("/transactions/", headers=auth_header(viewer))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_viewer_can_get_by_id(self, client: TestClient):
        admin  = register_and_login(client, "admin",  "pass123", "admin")
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        tx_id  = _create_tx(client, admin).json()["id"]
        resp   = client.get(f"/transactions/{tx_id}", headers=auth_header(viewer))
        assert resp.status_code == 200

    def test_get_nonexistent_returns_404(self, client: TestClient):
        token = register_and_login(client, "viewer", "pass123", "viewer")
        resp  = client.get("/transactions/9999", headers=auth_header(token))
        assert resp.status_code == 404

    def test_pagination(self, client: TestClient):
        admin = register_and_login(client, "admin", "pass123", "admin")
        for _ in range(5):
            _create_tx(client, admin)
        resp = client.get("/transactions/?limit=3&skip=0", headers=auth_header(admin))
        assert len(resp.json()) == 3


class TestFiltering:
    def test_analyst_can_filter_by_type(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _create_tx(client, admin, {**SAMPLE_TX, "type": "income"})
        _create_tx(client, admin, {**SAMPLE_TX, "type": "expense"})
        resp = client.get("/transactions/?type=income", headers=auth_header(analyst))
        assert all(t["type"] == "income" for t in resp.json())

    def test_analyst_can_filter_by_category(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _create_tx(client, admin, {**SAMPLE_TX, "category": "Rent"})
        _create_tx(client, admin, {**SAMPLE_TX, "category": "Salary"})
        resp = client.get("/transactions/?category=rent", headers=auth_header(analyst))
        assert len(resp.json()) == 1
        assert resp.json()[0]["category"] == "Rent"

    def test_analyst_can_filter_by_date_range(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _create_tx(client, admin, {**SAMPLE_TX, "date": "2025-01-15"})
        _create_tx(client, admin, {**SAMPLE_TX, "date": "2025-06-15"})
        resp = client.get(
            "/transactions/?start_date=2025-01-01&end_date=2025-03-31",
            headers=auth_header(analyst),
        )
        assert len(resp.json()) == 1
        assert resp.json()[0]["date"] == "2025-01-15"

    def test_viewer_cannot_filter(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        resp   = client.get("/transactions/?type=income", headers=auth_header(viewer))
        assert resp.status_code == 403


class TestUpdateTransaction:
    def test_admin_can_update(self, client: TestClient):
        token  = register_and_login(client, "admin", "pass123", "admin")
        tx_id  = _create_tx(client, token).json()["id"]
        resp   = client.patch(f"/transactions/{tx_id}", json={"amount": 9999.0}, headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["amount"] == 9999.0

    def test_partial_update_preserves_other_fields(self, client: TestClient):
        token  = register_and_login(client, "admin", "pass123", "admin")
        tx_id  = _create_tx(client, token).json()["id"]
        client.patch(f"/transactions/{tx_id}", json={"notes": "Updated note"}, headers=auth_header(token))
        resp   = client.get(f"/transactions/{tx_id}", headers=auth_header(token))
        assert resp.json()["category"] == "Salary"   # unchanged
        assert resp.json()["notes"]    == "Updated note"

    def test_empty_patch_returns_400(self, client: TestClient):
        token  = register_and_login(client, "admin", "pass123", "admin")
        tx_id  = _create_tx(client, token).json()["id"]
        resp   = client.patch(f"/transactions/{tx_id}", json={}, headers=auth_header(token))
        assert resp.status_code == 400

    def test_viewer_cannot_update(self, client: TestClient):
        admin  = register_and_login(client, "admin",  "pass123", "admin")
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        tx_id  = _create_tx(client, admin).json()["id"]
        resp   = client.patch(f"/transactions/{tx_id}", json={"amount": 1.0}, headers=auth_header(viewer))
        assert resp.status_code == 403


class TestDeleteTransaction:
    def test_admin_can_delete(self, client: TestClient):
        token  = register_and_login(client, "admin", "pass123", "admin")
        tx_id  = _create_tx(client, token).json()["id"]
        resp   = client.delete(f"/transactions/{tx_id}", headers=auth_header(token))
        assert resp.status_code == 200
        # Confirm it's gone
        assert client.get(f"/transactions/{tx_id}", headers=auth_header(token)).status_code == 404

    def test_delete_nonexistent_returns_404(self, client: TestClient):
        token = register_and_login(client, "admin", "pass123", "admin")
        assert client.delete("/transactions/9999", headers=auth_header(token)).status_code == 404

    def test_analyst_cannot_delete(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        tx_id   = _create_tx(client, admin).json()["id"]
        assert client.delete(f"/transactions/{tx_id}", headers=auth_header(analyst)).status_code == 403

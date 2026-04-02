"""Tests for /auth — register, login, and /me endpoints."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_header, register_and_login


class TestRegister:
    def test_register_success(self, client: TestClient):
        resp = client.post("/auth/register", json={
            "username": "alice",
            "email":    "alice@test.com",
            "password": "secret123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["role"] == "viewer"
        assert "password_hash" not in data

    def test_register_default_role_is_viewer(self, client: TestClient):
        resp = client.post("/auth/register", json={
            "username": "bob", "email": "bob@test.com", "password": "pass123",
        })
        assert resp.json()["role"] == "viewer"

    def test_register_duplicate_username(self, client: TestClient):
        payload = {"username": "alice", "email": "alice@test.com", "password": "pass123"}
        client.post("/auth/register", json=payload)
        resp = client.post("/auth/register", json={**payload, "email": "alice2@test.com"})
        assert resp.status_code == 409

    def test_register_duplicate_email(self, client: TestClient):
        client.post("/auth/register", json={"username": "alice", "email": "shared@test.com", "password": "pass123"})
        resp = client.post("/auth/register", json={"username": "bob",   "email": "shared@test.com", "password": "pass123"})
        assert resp.status_code == 409

    def test_register_short_password(self, client: TestClient):
        resp = client.post("/auth/register", json={
            "username": "carol", "email": "carol@test.com", "password": "abc",
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client: TestClient):
        resp = client.post("/auth/register", json={
            "username": "dave", "email": "not-an-email", "password": "pass123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        client.post("/auth/register", json={"username": "alice", "email": "alice@test.com", "password": "pass123"})
        resp = client.post("/auth/login", json={"username": "alice", "password": "pass123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient):
        client.post("/auth/register", json={"username": "alice", "email": "alice@test.com", "password": "pass123"})
        resp = client.post("/auth/login", json={"username": "alice", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        resp = client.post("/auth/login", json={"username": "ghost", "password": "pass123"})
        assert resp.status_code == 401


class TestMe:
    def test_me_returns_current_user(self, client: TestClient):
        token = register_and_login(client, "alice", "pass123", "analyst")
        resp  = client.get("/auth/me", headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "alice"
        assert resp.json()["role"] == "analyst"

    def test_me_requires_auth(self, client: TestClient):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client: TestClient):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer bad.token.here"})
        assert resp.status_code == 401

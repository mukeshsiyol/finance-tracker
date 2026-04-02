"""Tests for /export — CSV and JSON download endpoints."""

import csv
import io
import json

from fastapi.testclient import TestClient

from tests.conftest import auth_header, register_and_login, SAMPLE_TX


def _seed(client, admin_token):
    for tx in [
        {**SAMPLE_TX, "type": "income",  "amount": 50000, "category": "Salary"},
        {**SAMPLE_TX, "type": "expense", "amount": 12000, "category": "Rent"},
    ]:
        client.post("/transactions/", json=tx, headers=auth_header(admin_token))


class TestCSVExport:
    def test_csv_download_returns_200(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp = client.get("/export/csv", headers=auth_header(analyst))
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    def test_csv_contains_correct_rows(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp    = client.get("/export/csv", headers=auth_header(analyst))
        reader  = csv.DictReader(io.StringIO(resp.text))
        rows    = list(reader)
        assert len(rows) == 2
        categories = {r["category"] for r in rows}
        assert categories == {"Salary", "Rent"}

    def test_csv_filter_by_type(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp   = client.get("/export/csv?type=income", headers=auth_header(analyst))
        reader = csv.DictReader(io.StringIO(resp.text))
        rows   = list(reader)
        assert len(rows) == 1
        assert rows[0]["type"] == "income"

    def test_viewer_cannot_export(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        assert client.get("/export/csv", headers=auth_header(viewer)).status_code == 403


class TestJSONExport:
    def test_json_download_returns_200(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp = client.get("/export/json", headers=auth_header(analyst))
        assert resp.status_code == 200

    def test_json_content_is_valid(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp    = client.get("/export/json", headers=auth_header(analyst))
        data    = json.loads(resp.content)
        assert isinstance(data, list)
        assert len(data) == 2
        assert all("amount" in tx and "category" in tx for tx in data)

    def test_json_filter_by_category(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed(client, admin)
        resp = client.get("/export/json?category=rent", headers=auth_header(analyst))
        data = json.loads(resp.content)
        assert len(data) == 1
        assert data[0]["category"] == "Rent"

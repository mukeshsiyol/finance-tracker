"""Tests for /analytics — summary, category breakdown, monthly totals, dashboard."""

from fastapi.testclient import TestClient

from tests.conftest import auth_header, register_and_login, SAMPLE_TX


def _seed_transactions(client, admin_token):
    """Create a small, deterministic set of transactions for analytics tests."""
    records = [
        {"amount": 80000, "type": "income",  "category": "Salary",    "date": "2025-01-05"},
        {"amount": 20000, "type": "income",  "category": "Freelance", "date": "2025-01-20"},
        {"amount": 15000, "type": "expense", "category": "Rent",      "date": "2025-01-10"},
        {"amount":  5000, "type": "expense", "category": "Groceries", "date": "2025-01-15"},
        {"amount": 80000, "type": "income",  "category": "Salary",    "date": "2025-02-05"},
        {"amount": 15000, "type": "expense", "category": "Rent",      "date": "2025-02-10"},
    ]
    for r in records:
        client.post("/transactions/", json={**r, "notes": None}, headers=auth_header(admin_token))


class TestSummary:
    def test_summary_correct_values(self, client: TestClient):
        admin   = register_and_login(client, "admin",  "pass123", "admin")
        viewer  = register_and_login(client, "viewer", "pass123", "viewer")
        _seed_transactions(client, admin)

        resp = client.get("/analytics/summary", headers=auth_header(viewer))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"]    == 180000.0
        assert data["total_expenses"]  == 35000.0
        assert data["current_balance"] == 145000.0
        assert data["total_records"]   == 6
        assert data["income_records"]  == 3
        assert data["expense_records"] == 3

    def test_summary_empty_db(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        resp   = client.get("/analytics/summary", headers=auth_header(viewer))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"]    == 0
        assert data["current_balance"] == 0

    def test_viewer_can_access_summary(self, client: TestClient):
        token = register_and_login(client, "viewer", "pass123", "viewer")
        assert client.get("/analytics/summary", headers=auth_header(token)).status_code == 200

    def test_unauthenticated_blocked(self, client: TestClient):
        assert client.get("/analytics/summary").status_code == 401


class TestCategoryBreakdown:
    def test_breakdown_structure(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed_transactions(client, admin)

        resp = client.get("/analytics/categories", headers=auth_header(analyst))
        assert resp.status_code == 200
        data = resp.json()
        assert "income" in data and "expense" in data

        income_cats = {c["category"]: c for c in data["income"]}
        assert "Salary" in income_cats
        assert income_cats["Salary"]["total"] == 160000.0
        assert income_cats["Salary"]["count"] == 2

    def test_percentages_sum_to_100(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed_transactions(client, admin)

        data = client.get("/analytics/categories", headers=auth_header(analyst)).json()
        for tx_type in ("income", "expense"):
            total_pct = sum(c["percentage"] for c in data[tx_type])
            assert abs(total_pct - 100.0) < 0.1   # floating point tolerance

    def test_viewer_blocked_from_categories(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        assert client.get("/analytics/categories", headers=auth_header(viewer)).status_code == 403


class TestMonthlyTotals:
    def test_monthly_values_correct(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed_transactions(client, admin)

        resp   = client.get("/analytics/monthly", headers=auth_header(analyst))
        assert resp.status_code == 200
        months = {(m["year"], m["month"]): m for m in resp.json()}

        jan = months[(2025, 1)]
        assert jan["total_income"]  == 100000.0
        assert jan["total_expense"] == 20000.0
        assert jan["net"]           == 80000.0

        feb = months[(2025, 2)]
        assert feb["net"] == 65000.0

    def test_viewer_blocked_from_monthly(self, client: TestClient):
        viewer = register_and_login(client, "viewer", "pass123", "viewer")
        assert client.get("/analytics/monthly", headers=auth_header(viewer)).status_code == 403


class TestDashboard:
    def test_dashboard_shape(self, client: TestClient):
        admin   = register_and_login(client, "admin",   "pass123", "admin")
        analyst = register_and_login(client, "analyst", "pass123", "analyst")
        _seed_transactions(client, admin)

        resp = client.get("/analytics/dashboard", headers=auth_header(analyst))
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "category_breakdown" in data
        assert "monthly_totals" in data
        assert "recent_transactions" in data
        assert len(data["recent_transactions"]) <= 10

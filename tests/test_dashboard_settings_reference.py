"""Smoke tests for newly added dashboard, settings, and reference routes."""

from main import app


def _paths() -> set[str]:
    return {str(getattr(route, "path", "")) for route in app.routes}


def test_dashboard_paths_registered():
    paths = _paths()
    assert "/api/dashboard/stats" in paths
    assert "/api/dashboard/complaints-status" in paths


def test_settings_paths_registered():
    paths = _paths()
    assert "/api/settings/billing" in paths
    assert "/api/admin/profile" in paths
    assert "/api/settings/notifications" in paths


def test_reference_paths_registered():
    paths = _paths()
    assert "/api/states" in paths
    assert "/api/discoms" in paths


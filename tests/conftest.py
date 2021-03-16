"""Prepare the tests."""
import pytest


@pytest.fixture
def db_url(tmpdir):
    return tmpdir / "db.sql"

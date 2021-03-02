"""Prepare the tests."""
import pytest


@pytest.fixture
def db_filename(tmpdir):
    return tmpdir / "db.sql"

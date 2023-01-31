"""Test the ``bluepyparallel.evaluator`` module."""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import os
from uuid import uuid4

import pandas as pd
import pytest
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import schema
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from bluepyparallel import database

URLS = [
    "/tmpdir/test_bpp.db",
    "sqlite:////tmpdir/test_bpp.db",
]
try:
    # Set up the PostgreSQL database:
    #   Create the ``test_bpp`` role::
    #     $ sudo -u postgres psql -c "CREATE ROLE test_bpp PASSWORD 'test_bpp' SUPERUSER CREATEDB
    #       CREATEROLE INHERIT LOGIN;"
    #   Create the ``test_bpp`` database::
    #     $ sudo -u postgres createdb -E UTF-8 test_bpp
    #     $ sudo -u postgres psql -d test_bpp -c 'CREATE SCHEMA test_bpp;'
    #     $ sudo -u postgres psql -c 'GRANT CREATE ON DATABASE test_bpp TO "test_bpp";'
    #     $ sudo -u postgres psql -d test_bpp -c 'GRANT USAGE,CREATE ON SCHEMA test_bpp TO
    #       "test_bpp";'
    PG_URL = "postgresql://test_bpp:test_bpp@localhost/test_bpp"
    create_engine(PG_URL).connect()
    URLS.append(PG_URL)
    with_postresql = True
except OperationalError:
    with_postresql = False
except ModuleNotFoundError as e:
    with_postresql = False
    if "psycopg2" not in str(e):
        raise


@pytest.fixture(params=URLS)
def url(request, tmpdir):
    """The url fixture."""
    return request.param.replace("/tmpdir", str(tmpdir))


@pytest.fixture
def small_df():
    """A fixture for a small DF."""
    data = {"a": list(range(6)), "b": [str(i * 10) for i in range(6)], "exception": [None] * 6}
    idx = [f"idx_{(i + 1) * 2}" for i in range(6)]
    return pd.DataFrame(data, index=idx)


@pytest.fixture()
def small_db(url, small_df):
    """A fixture for a small DB."""
    db = database.DataBase(url)
    db.create(small_df)
    small_df.to_sql(
        name=db.table.name,
        con=db.connection,
        schema=db.table.schema,
        if_exists="replace",
        index_label=db.index_col,
    )
    return db


@pytest.fixture()
def autoremoved_schema():
    """A fixture to create a tmp schema in the DB and remove it afterwards."""
    schema_name = str(uuid4())
    yield schema_name
    engine = create_engine(PG_URL)
    engine.execute(schema.DropSchema(schema_name, cascade=True))


class TestDataBase:
    """Test the ``DataBase`` class."""

    @pytest.mark.parametrize("table_name", [None, "df", "df_name"])
    def test_create(self, url, small_df, table_name):
        """Test the ``db.create()`` method."""
        db = database.DataBase(url)
        db.create(small_df, table_name)

        # Check DB
        if url.startswith("/"):
            url = "sqlite:///" + url
        engine = create_engine(url)
        conn = engine.connect()
        metadata = MetaData()
        table = Table(
            table_name or "df",
            metadata,
            autoload_with=engine,
        )

        # Check reflected table
        assert str(table.c.items()) == str(db.table.c.items())

        # Check elements inserted into the DB
        query = select(table)
        res = conn.execute(query).fetchall()
        assert res == []

    @pytest.mark.parametrize("table_name", [None, "df", "df_name"])
    @pytest.mark.skipif(not with_postresql, reason="Only tested with PostgreSQL")
    def test_create_with_schema(self, small_df, table_name, autoremoved_schema):
        """Test the ``db.create()`` method with a schema."""
        schema_name = autoremoved_schema
        url = PG_URL
        db = database.DataBase(url)
        db.create(small_df, table_name, schema_name)

        # Check DB
        if url.startswith("/"):
            url = "sqlite:///" + url
        engine = create_engine(url)
        conn = engine.connect()
        metadata = MetaData()
        table = Table(
            table_name or "df",
            metadata,
            schema=schema_name,
            autoload_with=engine,
        )

        # Check reflected table
        assert str(table.c.items()) == str(db.table.c.items())

        # Check elements inserted into the DB
        query = select(table)
        res = conn.execute(query).fetchall()
        assert res == []

    def test_db_exists(self, tmpdir):
        """Test the ``db.db_exists()`` method."""
        # Ensure that the DB does not exist
        url = URLS[1].replace("/tmpdir", str(tmpdir))
        engine = create_engine(url)
        if os.path.isfile(engine.url.database):
            os.remove(engine.url.database)

        # Setup the DB
        db = database.DataBase(url)

        # Test that the DB does not exist
        assert not db.db_exists()

        # Create the DB
        db = database.DataBase(url, create=True)

        # Test that the DB does exist
        assert db.db_exists()

    def test_exists(self, small_db):
        """Test the ``db.exists()`` method."""
        assert small_db.exists("df")
        assert not small_db.exists("UNKNOWN TABLE")

    def test_load(self, small_df, small_db):
        """Test the ``db.load()`` method."""
        res = small_db.load()

        # Check DB
        assert res.equals(small_df)

    def test_write(self, small_df, small_db):
        """Test the ``db.write()`` method."""
        small_db.write("idx_100", result={"a": 1, "b": "test_1"})
        small_db.write("idx_101", exception="test exception")
        small_db.write("idx_102")  # Should write nothing

        # Check DB after write
        res = small_db.load()
        small_df.loc["idx_100", ["a", "b", "exception"]] = [1, "test_1", None]
        small_df.loc["idx_101", ["a", "b", "exception"]] = [None, None, "test exception"]
        assert res.equals(small_df)

    def test_get_url(self, url, small_db):
        """Test the ``db.get_url()`` method."""
        if url.startswith("/"):
            url = "sqlite:///" + url
        assert str(small_db.get_url()) == url

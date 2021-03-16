"""Test the bluepyparallel.evaluator module"""
# pylint: disable=redefined-outer-name
import pandas as pd
import pytest
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select

from bluepyparallel import database

URLS = ["/tmpdir/test.db", "sqlite:////tmpdir/test.db"]


@pytest.fixture(params=URLS)
def url(request, tmpdir):
    return request.param.replace("/tmpdir", str(tmpdir))


@pytest.fixture
def small_df():
    data = {"a": list(range(6)), "b": [str(i * 10) for i in range(6)], "exception": [None] * 6}
    idx = [f"idx_{(i + 1) * 2}" for i in range(6)]
    return pd.DataFrame(data, index=idx)


@pytest.fixture()
def small_db(url, small_df):
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


class TestDataBase:
    """Test the DataBase class."""

    @pytest.mark.parametrize("table_name", [None, "df", "df_name"])
    @pytest.mark.parametrize("schema_name", [None])
    def test_create(self, url, small_df, table_name, schema_name):
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
            autoload=True,
            autoload_with=engine,
        )

        # Check reflected table
        assert str(table.c.items()) == str(db.table.c.items())

        # Check elements inserted into the DB
        query = select([table])
        res = conn.execute(query).fetchall()
        assert res == []

    def test_exists(self, small_db):
        assert small_db.exists("df")
        assert not small_db.exists("UNKNOWN TABLE")

    def test_load(self, small_df, small_db):
        res = small_db.load()

        # Check DB
        assert res.equals(small_df)

    def test_write(self, small_df, small_db):
        small_db.write("idx_100", result={"a": 1, "b": "test_1"})
        small_db.write("idx_101", exception="test exception")
        small_db.write("idx_102")  # Should write nothing

        # Check DB after write
        res = small_db.load()
        small_df.loc["idx_100", ["a", "b", "exception"]] = [1, "test_1", None]
        small_df.loc["idx_101", ["a", "b", "exception"]] = [None, None, "test exception"]
        assert res.equals(small_df)

    def test_get_url(self, url, small_db):
        if url.startswith("/"):
            url = "sqlite:///" + url
        assert str(small_db.get_url()) == url

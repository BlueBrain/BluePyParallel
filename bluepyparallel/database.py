"""Module"""
import re

import pandas as pd
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import schema
from sqlalchemy import select
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists


class DataBase:
    """A database API using SQLAlchemy."""

    index_col = "df_index"
    _url_pattern = r"[a-zA-Z0-9_\-\+]+://.*"

    def __init__(self, url, *args, create=False, **kwargs):
        if not re.match(self._url_pattern, str(url)):
            url = "sqlite:///" + str(url)

        self.engine = create_engine(url, *args, **kwargs)

        if create and not database_exists(self.engine.url):
            create_database(self.engine.url)

        self.connection = self.engine.connect()
        self.metadata = None
        self.table = None

    def __del__(self):
        self.connection.close()

    def get_url(self):
        return self.engine.url

    def create(self, df, table_name=None, schema_name=None):
        if table_name is None:
            table_name = "df"
        if schema_name is not None and schema_name not in self.connection.dialect.get_schema_names(
            self.connection
        ):
            self.connection.execute(schema.CreateSchema(schema_name))
        new_df = df.loc[[]]
        new_df.to_sql(
            name=table_name,
            con=self.connection,
            schema=schema_name,
            if_exists="replace",
            index_label=self.index_col,
        )
        self.reflect(table_name, schema_name)

    def exists(self, table_name, schema_name=None):
        inspector = Inspector.from_engine(self.engine)
        return table_name in inspector.get_table_names(schema=schema_name)

    def reflect(self, table_name, schema_name=None):
        self.metadata = MetaData()
        self.table = Table(
            table_name,
            self.metadata,
            schema=schema_name,
            autoload=True,
            autoload_with=self.engine,
        )

    def load(self):
        query = select([self.table])
        return pd.read_sql(query, self.connection, index_col=self.index_col)

    def write(self, row_id, result=None, exception=None, **input_values):
        if result is not None:
            vals = result
        elif exception is not None:
            vals = {"exception": exception}
        else:
            return

        query = insert(self.table).values(dict(**{self.index_col: row_id}, **vals, **input_values))
        self.connection.execute(query)

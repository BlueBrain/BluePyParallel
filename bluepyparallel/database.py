"""Module used to provide a simple API to a database in which the results are stored."""
import re

import pandas as pd
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import schema
from sqlalchemy import select
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists

try:  # pragma: no cover
    import psycopg2

    with_psycopg2 = True
except ImportError:
    with_psycopg2 = False


class DataBase:
    """A simple API to manage the database in which the results are inserted using SQLAlchemy.

    Args:
        url (str): The URL of the database following the RFC-1738 format (
            https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)
        create (bool): If set to True, the database will be automatically created by the
            constructor.
        args and kwargs: They will be passed to the :func:`sqlalchemy.create_engine` function.
    """

    index_col = "df_index"
    _url_pattern = r"[a-zA-Z0-9_\-\+]+://.*"

    def __init__(self, url, *args, create=False, **kwargs):
        if not re.match(self._url_pattern, str(url)):
            url = "sqlite:///" + str(url)

        self.engine = create_engine(url, *args, **kwargs)

        if create and not self.db_exists():
            create_database(self.engine.url)

        self._connection = None
        self.metadata = None
        self.table = None

    def __del__(self):
        """Close the connection and the engine to the database."""
        self.connection.close()
        self.engine.dispose()

    @property
    def connection(self):
        """Get a connection to the database."""
        if self._connection is None:
            self._connection = self.engine.connect()
        return self._connection

    def get_url(self):
        """Get the URL of the database."""
        return self.engine.url

    def create(self, df, table_name=None, schema_name=None):
        """Create a table in the database in which the results will be written."""
        if table_name is None:
            table_name = "df"
        if schema_name is not None and schema_name not in self.connection.dialect.get_schema_names(
            self.connection
        ):  # pragma: no cover
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

    def db_exists(self):
        """Check that the server and the database exist."""
        if with_psycopg2:  # pragma: no cover
            exceptions = (OperationalError, psycopg2.OperationalError)
        else:
            exceptions = (OperationalError,)

        try:
            return database_exists(self.engine.url)
        except exceptions:  # pragma: no cover
            return False

    def exists(self, table_name, schema_name=None):
        """Test that the table exists in the database."""
        inspector = Inspector.from_engine(self.engine)
        return table_name in inspector.get_table_names(schema=schema_name)

    def reflect(self, table_name, schema_name=None):
        """Reflect the table from the database."""
        self.metadata = MetaData()
        self.table = Table(
            table_name,
            self.metadata,
            schema=schema_name,
            autoload=True,
            autoload_with=self.engine,
        )

    def load(self):
        """Load the table data from the database."""
        query = select([self.table])
        return pd.read_sql(query, self.connection, index_col=self.index_col)

    def write(self, row_id, result=None, exception=None, **input_values):
        """Write a result entry or an exception into the table."""
        if result is not None:
            vals = result
        elif exception is not None:
            vals = {"exception": exception}
        else:
            return

        query = insert(self.table).values(dict(**{self.index_col: row_id}, **vals, **input_values))
        self.connection.execute(query)

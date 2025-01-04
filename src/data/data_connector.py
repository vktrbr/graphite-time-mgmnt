import os
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine


def get_engine(database: str, schema: str):
    """
    Creates a Snowflake SQLAlchemy engine using environment variables for credentials.

    :param database: Optional Snowflake database name
    :param schema: Optional Snowflake schema name
    :return: A SQLAlchemy Engine connected to Snowflake.
    :raises EnvironmentError: If any required Snowflake environment variable is missing.
    """
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
    ]
    for var in required_vars:
        if var not in os.environ:
            raise EnvironmentError(f"Missing required environment variable: {var}")

    if not database or not schema:
        raise ValueError("Database and schema are required parameters")

    url_params = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "role": os.environ["SNOWFLAKE_ROLE"],
    }

    if database:
        url_params["database"] = database
    if schema:
        url_params["schema"] = schema

    return create_engine(URL(**url_params))

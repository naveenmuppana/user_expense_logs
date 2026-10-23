import os 
from sqlalchemy import create_engine,text
from dotenv import load_dotenv


load_dotenv()

test_database_url = os.getenv("TEST_DATABASE_URL")
assert test_database_url, "TEST_DATABASE_URL is missing from .env"


engine = create_engine(test_database_url)

def test_database_is_expense_tracker_test():
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    assert database_name == "expense_tracker_test"

    engine.dispose()
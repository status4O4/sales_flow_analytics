from dotenv import load_dotenv
import os

load_dotenv()


def get_database_url() -> str:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "test_top_city")

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = get_database_url()

CREATE_TEST_DATA = int(os.getenv("CREATE_TEST_DATA", 1))
USERS_COUNT_TEST_DATA = int(os.getenv("USERS_COUNT_TEST_DATA", 10000))
PRODUCTS_COUNT_TEST_DATA = int(os.getenv("PRODUCTS_COUNT_TEST_DATA", 10000))
SALES_COUNT_TEST_DATA = int(os.getenv("SALES_COUNT_TEST_DATA", 3000000))

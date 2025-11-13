from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.sql_queries import (
    truncate_tables_query,
    insert_test_users_query,
    insert_test_products_query,
    insert_test_sales_query,
    create_users_table_query,
    create_products_table_query,
    create_sales_table_query,
)
import logging


logger = logging.getLogger(__name__)


async def create_tables(session: AsyncSession):
    try:
        logger.info("Create users table...")
        await session.execute(text(create_users_table_query))
        await session.commit()
        logger.info("Users table created")

        logger.info("Create products table...")
        await session.execute(text(create_products_table_query))
        await session.commit()
        logger.info("Products table created")

        logger.info("Create sales table...")
        await session.execute(text(create_sales_table_query))
        await session.commit()
        logger.info("Sales table created")
        logger.info("Tables successfully created!")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating tables: {e}")
        raise


async def create_test_data(
    session: AsyncSession,
    users_count=50000,
    products_count=5000,
    sales_count=10000000,
):
    truncate_tables = text(truncate_tables_query)
    insert_users = text(insert_test_users_query)
    insert_products = text(insert_test_products_query)
    insert_sales = text(insert_test_sales_query)

    try:
        logger.info("Cleaning tables...")
        await session.execute(truncate_tables)
        await session.commit()
        logger.info("Tables cleaned")

        logger.info(f"Adding {users_count} users...")
        await session.execute(insert_users, {"users_count": users_count})
        await session.commit()
        logger.info("Users added")

        logger.info(f"Adding {products_count} products...")
        await session.execute(insert_products, {"products_count": products_count})
        await session.commit()
        logger.info("Products added")

        logger.info(f"Adding {sales_count} sales...")
        await session.execute(
            insert_sales,
            {
                "users_count": users_count,
                "products_count": products_count,
                "sales_count": sales_count,
            },
        )
        await session.commit()
        logger.info("Sales added")
        logger.info("Test data successfully created!")

    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating test data: {e}")
        raise


async def select_by_date(
    session: AsyncSession, start_date: datetime, end_date: datetime, query: str
):
    try:
        result = await session.execute(
            text(query),
            {
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        return result.fetchall()
    except Exception as e:
        await session.rollback()
        logger.error(f"Error selecting: {e}")
        raise

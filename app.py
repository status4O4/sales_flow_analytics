import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import (
    CREATE_TEST_DATA,
    PRODUCTS_COUNT_TEST_DATA,
    SALES_COUNT_TEST_DATA,
    USERS_COUNT_TEST_DATA,
)
from database.database import get_db
from database.sql_queries import select_sales_query
from database.utils import (
    create_tables,
    create_test_data,
    select_by_date,
)
from utils.async_http_client import AsyncHTTPClient
from utils.utils import process_sales_data


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    try:
        logger.info("Creating test data...")
        async for session in get_db():
            await create_tables(session=session)
            if CREATE_TEST_DATA:
                await create_test_data(
                    session=session,
                    users_count=USERS_COUNT_TEST_DATA,
                    products_count=PRODUCTS_COUNT_TEST_DATA,
                    sales_count=SALES_COUNT_TEST_DATA,
                )
                logger.info("Test data created successfully")
            else:
                logger.info("Test data creation skipped")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

async_h_client = AsyncHTTPClient()


@app.get("/sales/summary")
async def get_sales_summary(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
):
    date_format = "%Y-%m-%d"

    try:
        start_dt = datetime.strptime(start_date, date_format)
        end_dt = datetime.strptime(end_date, date_format)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте формат YYYY-MM-DD",
        )

    if start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальная дата не может быть больше конечной",
        )

    current_date = datetime.now()
    if start_dt > current_date or end_dt > current_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Даты не могут быть в будущем",
        )
    http_result = ""
    async with async_h_client as client:
        """
        Не особо понял каким образом получать данные с https://jsonplaceholder.typicode.com/posts 
        (Запрос возвращает данные в формате, что я написал ниже и ничего более подходящего под продажи я не нашел)
        {
            "userId": int,
            "id": int,
            "title": str,
            "body": str
        },
        """
        http_result = await client.get(endpoint="posts")

    raw_data = await select_by_date(
        session=db,
        start_date=datetime.strptime(start_date, date_format),
        end_date=datetime.strptime(end_date, date_format),
        query=select_sales_query,
    )
    result = process_sales_data(
        start_date=datetime.strptime(start_date, date_format),
        end_date=datetime.strptime(end_date, date_format),
        raw_data=raw_data,
    )
    return result


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

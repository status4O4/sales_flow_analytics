from fastapi import FastAPI
import pandas as pd
import asyncio
import aiohttp

app = FastAPI()


@app.get("/sales/summary")
async def get_sales_summary(start_date: str, end_date: str):
    """
    Требования:
    1. Асинхронно получить данные из mock API:
       https://jsonplaceholder.typicode.com/posts
       (имитация данных продаж)

    2. Обработать данные с помощью pandas:
       - Сгруппировать по дням
       - Посчитать скользящее среднее (окно 3 дня)
       - Найти топ-5 дней по продажам

    3. Вернуть результат в формате JSON

    4. Добавить обработку ошибок и валидацию дат
    """
    pass

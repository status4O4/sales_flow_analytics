import pandas as pd
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def process_sales_data(start_date: datetime, end_date: datetime, raw_data) -> dict:
    try:
        if not raw_data:
            return {
                "error": "No sales data found for the specified period",
                "moving_average": [],
                "top_days": [],
            }

        df = pd.DataFrame(raw_data, columns=["sale_date", "amount"])

        if df.empty:
            return {
                "error": "No data available after processing",
                "moving_average": [],
                "top_days": [],
            }

        df["sale_date"] = pd.to_datetime(df["sale_date"])

        daily_sales = df.groupby(df["sale_date"].dt.date)["amount"].sum().reset_index()
        daily_sales["sale_date"] = pd.to_datetime(daily_sales["sale_date"])
        daily_sales = daily_sales.rename(columns={"amount": "sales"})
        daily_sales["sales"] = pd.to_numeric(daily_sales["sales"], errors="coerce")

        daily_sales = daily_sales.sort_values("sale_date")

        daily_sales["moving_average"] = (
            daily_sales["sales"].rolling(window=3, min_periods=1).mean().round(2)
        )

        top_days = daily_sales.nlargest(5, "sales")[["sale_date", "sales"]]

        result_data = {
            "summary": {
                "total_days": len(daily_sales),
                "total_sales": float(daily_sales["sales"].sum()),
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            },
            "moving_average": [
                {
                    "date": row["sale_date"].strftime("%Y-%m-%d"),
                    "sales": float(row["sales"]),
                    "moving_average": float(row["moving_average"]),
                }
                for _, row in daily_sales.iterrows()
            ],
            "top_days": [
                {
                    "date": row["sale_date"].strftime("%Y-%m-%d"),
                    "sales": float(row["sales"]),
                }
                for _, row in top_days.iterrows()
            ],
        }

        return result_data

    except Exception as e:
        logger.error(f"Error processing sales data: {e}")
        return {
            "error": f"Processing error: {str(e)}",
            "moving_average": [],
            "top_days": [],
        }


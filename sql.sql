WITH monthly_city_sales AS (
    SELECT 
        DATE_TRUNC('month', s.sale_date) AS sale_month,
        u.city,
        SUM(s.amount) AS total_sales,
        SUM(SUM(s.amount)) OVER (PARTITION BY DATE_TRUNC('month', s.sale_date)) AS monthly_total_sales,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('month', s.sale_date) 
            ORDER BY SUM(s.amount) DESC
        ) AS city_rank
    FROM sales S
    INNER JOIN users U ON S.user_id = U.id
    WHERE S.sale_date IS NOT NULL
      AND U.city IS NOT NULL
    GROUP BY sale_month, U.city
)
SELECT 
    sale_month,
    city,
    ROUND((total_sales / monthly_total_sales) * 100, 2) AS sales_percentage,
    monthly_total_sales,
    city_rank
FROM monthly_city_sales

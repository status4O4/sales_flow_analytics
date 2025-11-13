select_sales_query = """
SELECT sale_date, amount
FROM sales 
WHERE sale_date BETWEEN :start_date AND :end_date;
"""

select_top_cities_by_monthly_sales_percentage_query = """
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
      AND s.sale_date BETWEEN :start_date AND :end_date
    GROUP BY sale_month, U.city
)
SELECT 
    sale_month,
    city,
    ROUND((total_sales / monthly_total_sales) * 100, 2) AS sales_percentage,
    monthly_total_sales,
    city_rank
FROM monthly_city_sales
    WHERE city_rank < 4
  ORDER BY sale_month;
"""

truncate_tables_query = "TRUNCATE TABLE sales, users, products CASCADE;"

insert_test_users_query = """
INSERT INTO users (id, name, city)
SELECT 
    id,
    'User_' || id,
    (ARRAY['Moscow', 'Saint Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan', 
           'Nizhny Novgorod', 'Chelyabinsk', 'Samara', 'Omsk', 'Rostov-on-Don',
           'Ufa', 'Krasnoyarsk', 'Voronezh', 'Perm', 'Volgograd'])[(id % 15) + 1]
FROM generate_series(1, :users_count) AS id;
"""

insert_test_products_query = """
INSERT INTO products (id, name, category)
SELECT 
    id,
    'Product_' || id,
    (ARRAY['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 
           'Automotive', 'Beauty', 'Toys', 'Food', 'Jewelry'])[(id % 10) + 1]
FROM generate_series(1, :products_count) AS id;
"""

insert_test_sales_query = """
INSERT INTO sales (id, user_id, product_id, sale_date, amount, quantity)
SELECT 
    id,
    (random() * (:users_count - 1))::int + 1,
    (random() * (:products_count - 1))::int + 1,
    DATE '2020-01-01' + (random() * 1825)::int,
    ROUND((random() * 2000 + 1)::numeric, 2),
    (random() * 20)::int + 1
FROM generate_series(1, :sales_count) AS id;
"""

create_sales_table_query = """ 
CREATE TABLE IF NOT EXISTS sales (
    id INT, 
    user_id INT, 
    product_id INT, 
    sale_date DATE, 
    amount DECIMAL, 
    quantity INT
);
"""

create_users_table_query = """ 
CREATE TABLE IF NOT EXISTS users (
    id INT, 
    name VARCHAR(50), 
    city VARCHAR(50)
);
"""

create_products_table_query = """
CREATE TABLE IF NOT EXISTS products (
    id INT, 
    name VARCHAR(50), 
    category VARCHAR(50)
);
"""

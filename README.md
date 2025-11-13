# Система анализа продаж
## 1. SQL запрос
```sql
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
    FROM sales s
    INNER JOIN users u ON s.user_id = u.id
    WHERE s.sale_date IS NOT NULL
      AND u.city IS NOT NULL
    --  AND s.sale_date BETWEEN :start_date AND :end_date -- Если нужно по дате выбирать
    GROUP BY sale_month, u.city
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
```

---

## 2. Python Backend

1. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте `.env` файл:
```env
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="test"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Если нужны тестовые данные
CREATE_TEST_DATA=0
USERS_COUNT_TEST_DATA=50000
PRODUCTS_COUNT_TEST_DATA=5000
SALES_COUNT_TEST_DATA=3000000
```

4. Запустите сервер:
```bash
python app.py
```

---

## 3. Frontend
Доступно при запуске FastAPI приложения http://127.0.0.1:8000/

---

## 4. Google Apps Script + Sheets

### Формулы в таблицах
```excel
// A1 - QUERY
=QUERY(A:C; "SELECT A, SUM(B) WHERE C >= date '"&TEXT(TODAY()-30;"yyyy-mm-dd")&"' GROUP BY A"; 1)

// B1 - ARRAYFORMULA  
=ARRAYFORMULA(IF(LEN(A2:A); B2:B*C2:C; ""))

// C1 - Процентное соотношение
=ARRAYFORMULA(IF(LEN(B2:B); B2:B/SUM(B2:B)*100; ""))
```

### Apps Script функция
```javascript
function updateSalesReport() {
  const apiUrl = "https://api.example.com/sales";
  const response = UrlFetchApp.fetch(apiUrl);
  const data = JSON.parse(response.getContentText());
  
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const rawDataSheet = spreadsheet.getSheetByName("Raw Data");
  const summarySheet = spreadsheet.getSheetByName("Summary");
  
  rawDataSheet.clearContents();
  
  if (data.length > 0) {
    const headers = Object.keys(data[0]);
    const headerRange = rawDataSheet.getRange(1, 1, 1, headers.length);
    headerRange.setValues([headers]);
    
    const values = data.map(row => headers.map(header => row[header]));
    const dataRange = rawDataSheet.getRange(2, 1, values.length, headers.length);
    dataRange.setValues(values);
    
    const amountIndex = headers.indexOf("amount");
    const totalSales = values.reduce((sum, row) => sum + parseFloat(row[amountIndex] || 0), 0);
    
    summarySheet.clearContents();
    summarySheet.getRange("A1").setValue("Total Sales");
    summarySheet.getRange("B1").setValue(totalSales);
    
    if (totalSales > 10000) {
      MailApp.sendEmail({
        to: "admin@example.com",
        subject: "Sales Report Alert",
        body: `Total sales amount: ${totalSales} has exceeded the threshold.`
      });
    }
  }
}
```

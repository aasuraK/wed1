CREATE TABLE Invoices (
    InvoiceID VARCHAR(255) PRIMARY KEY,
    Branch VARCHAR(255),
    City VARCHAR(255),
    CustomerType VARCHAR(255),
    Gender VARCHAR(255),
    ProductLine VARCHAR(255),
    UnitPrice FLOAT,
    Quantity INT,
    Tax5Percent FLOAT,
    Total FLOAT,
    Q VARCHAR(255),
    Time VARCHAR(255),
    Payment VARCHAR(255),
    COGS FLOAT,
    GrossMarginPercentage FLOAT,
    GrossIncome FLOAT,
    Rating FLOAT,
    Month INT,
    Year INT
);

WITH monthly_sales AS (
    SELECT "Product line",
           SUM("Total") AS total_sales,
           strftime('%m', "Sale Date") AS month,
           strftime('%Y', "Sale Date") AS year
    FROM result
    GROUP BY "Product line", month, year
),
growth_rate AS (
    SELECT "Product line",
           month,
           year,
           total_sales,
           LAG(total_sales) OVER (PARTITION BY "Product line" ORDER BY year, month) AS previous_month_sales,
           ((total_sales - LAG(total_sales) OVER (PARTITION BY "Product line" ORDER BY year, month)) / LAG(total_sales) OVER (PARTITION BY "Product line" ORDER BY year, month)) * 100 AS growth_rate
    FROM monthly_sales
)
SELECT *
FROM growth_rate
ORDER BY "Product line", year, month

CREATE TABLE result (
    ProductLine VARCHAR(255),
    Total FLOAT,
    Month INT,
    Year INT
);

COPY Invoices FROM '/Users/amoghnigam/Downloads/pathsetter/dashboard/output/check_v1_processed_supermarket_sales.csv' DELIMITER ',' header csv;


COPY result(ProductLine, Total, Month, Year) 
FROM '/Users/amoghnigam/Downloads/pathsetter/dashboard/output/results_final.csv' 
DELIMITER ',' 
CSV HEADER;

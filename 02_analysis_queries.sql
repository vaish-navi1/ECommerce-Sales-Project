USE ecommerce_analytics;

-- 1. Overall KPIs
SELECT
  ROUND(SUM(LineRevenue), 2) AS total_revenue,
  COUNT(DISTINCT Invoice) AS total_orders,
  COUNT(DISTINCT CustomerID) AS unique_customers,
  ROUND(SUM(LineRevenue) / NULLIF(COUNT(DISTINCT Invoice), 0), 2) AS average_order_value
FROM cleaned_transactions;

-- 2. Monthly revenue and month-over-month change
WITH monthly AS (
  SELECT InvoiceMonth, SUM(LineRevenue) AS revenue
  FROM cleaned_transactions
  GROUP BY InvoiceMonth
)
SELECT InvoiceMonth, ROUND(revenue, 2) AS revenue,
       ROUND(100 * (revenue - LAG(revenue) OVER (ORDER BY InvoiceMonth)) /
       NULLIF(LAG(revenue) OVER (ORDER BY InvoiceMonth), 0), 2) AS mom_growth_pct
FROM monthly
ORDER BY InvoiceMonth;

-- 3. Top 10 countries by revenue
SELECT Country, ROUND(SUM(LineRevenue), 2) AS revenue,
       COUNT(DISTINCT Invoice) AS orders,
       COUNT(DISTINCT CustomerID) AS customers
FROM cleaned_transactions
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;

-- 4. Top 10 products by revenue
SELECT StockCode, MAX(Description) AS product_description,
       ROUND(SUM(LineRevenue), 2) AS revenue,
       SUM(Quantity) AS units_sold
FROM cleaned_transactions
GROUP BY StockCode
ORDER BY revenue DESC
LIMIT 10;

-- 5. Customers by lifetime value
SELECT CustomerID, ROUND(SUM(LineRevenue), 2) AS lifetime_revenue,
       COUNT(DISTINCT Invoice) AS order_count,
       MAX(InvoiceDate) AS last_purchase
FROM cleaned_transactions
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY lifetime_revenue DESC
LIMIT 20;

-- 6. Repeat customer rate (customer has more than one distinct invoice)
WITH customer_orders AS (
  SELECT CustomerID, COUNT(DISTINCT Invoice) AS order_count
  FROM cleaned_transactions
  WHERE CustomerID IS NOT NULL
  GROUP BY CustomerID
)
SELECT
  COUNT(*) AS identified_customers,
  SUM(order_count > 1) AS repeat_customers,
  ROUND(100.0 * SUM(order_count > 1) / NULLIF(COUNT(*), 0), 2) AS repeat_customer_pct
FROM customer_orders;

-- 7. Country and month comparison
SELECT Country, InvoiceMonth, ROUND(SUM(LineRevenue), 2) AS revenue
FROM cleaned_transactions
GROUP BY Country, InvoiceMonth
ORDER BY Country, InvoiceMonth;

-- 8. Weekday sales pattern
SELECT DAYNAME(InvoiceDate) AS weekday,
       ROUND(SUM(LineRevenue), 2) AS revenue,
       COUNT(DISTINCT Invoice) AS orders
FROM cleaned_transactions
GROUP BY DAYOFWEEK(InvoiceDate), DAYNAME(InvoiceDate)
ORDER BY DAYOFWEEK(InvoiceDate);

-- 9. Average basket size (units per invoice)
SELECT ROUND(SUM(Quantity) / NULLIF(COUNT(DISTINCT Invoice), 0), 2) AS avg_units_per_order
FROM cleaned_transactions;

-- 10. Check duplicate line records (exact duplicate key heuristic)
SELECT Invoice, StockCode, InvoiceDate, Quantity, Price, COUNT(*) AS row_count
FROM cleaned_transactions
GROUP BY Invoice, StockCode, InvoiceDate, Quantity, Price
HAVING COUNT(*) > 1
ORDER BY row_count DESC;

-- 11. Sales concentration by country
WITH country_rev AS (
  SELECT Country, SUM(LineRevenue) AS revenue
  FROM cleaned_transactions GROUP BY Country
)
SELECT Country, ROUND(revenue, 2) AS revenue,
       ROUND(100 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct
FROM country_rev
ORDER BY revenue DESC;

-- 12. Customer recency/frequency/monetary (RFM base)
SELECT CustomerID,
       DATEDIFF((SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) FROM cleaned_transactions),
                MAX(InvoiceDate)) AS recency_days,
       COUNT(DISTINCT Invoice) AS frequency,
       ROUND(SUM(LineRevenue), 2) AS monetary_value
FROM cleaned_transactions
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY monetary_value DESC;

-- 13.  Calculate Overall Business Performance
SELECT
    ROUND(SUM(LineRevenue), 2) AS total_revenue,
    COUNT(DISTINCT Invoice) AS total_orders,
    COUNT(DISTINCT CustomerID) AS unique_customers,
    ROUND(AVG(LineRevenue), 2) AS average_line_revenue
FROM cleaned_transactions;
-- 14.  Find Monthly Sales Trends
SELECT
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
    ROUND(SUM(LineRevenue), 2) AS monthly_revenue,
    COUNT(DISTINCT Invoice) AS total_orders
FROM cleaned_transactions
GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
ORDER BY sales_month;
-- 15.  Find Top 10 Products
SELECT
    Description,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(LineRevenue), 2) AS total_revenue
FROM cleaned_transactions
WHERE Description IS NOT NULL
GROUP BY Description
ORDER BY total_revenue DESC
LIMIT 10;
-- 16.  Find Top 10 Countries by revenue
SELECT
    Country,
    ROUND(SUM(LineRevenue), 2) AS total_revenue,
    COUNT(DISTINCT Invoice) AS total_orders
FROM cleaned_transactions
GROUP BY Country
ORDER BY total_revenue DESC
LIMIT 10;
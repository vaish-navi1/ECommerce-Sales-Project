-- MySQL 8+ schema for E-Commerce Sales Analytics
-- Option A (recommended for beginners): create schema and use MySQL Workbench
-- Server > Data Import Wizard to import output/cleaned_transactions.csv into
-- a table named cleaned_transactions, then verify the columns below.
CREATE DATABASE IF NOT EXISTS ecommerce_analytics;
USE ecommerce_analytics;

-- Create this table before using the MySQL Table Data Import Wizard.
CREATE TABLE IF NOT EXISTS cleaned_transactions (
    Invoice VARCHAR(30),
    StockCode VARCHAR(40),
    Description TEXT,
    Quantity INT,
    InvoiceDate DATETIME,
    Price DECIMAL(12,4),
    CustomerID BIGINT NULL,
    Country VARCHAR(100),
    LineRevenue DECIMAL(14,4),
    InvoiceMonth CHAR(7),
    InvoiceYear SMALLINT,
    InvoiceDay DATE
);

-- Import CSV using Workbench Table Data Import Wizard:
-- 1. Right-click ecommerce_analytics schema > Table Data Import Wizard.
-- 2. Select output/cleaned_transactions.csv.
-- 3. Choose existing table cleaned_transactions if prompted.
-- 4. Map columns and check date/time formats.
-- 5. Run SELECT COUNT(*) FROM cleaned_transactions; to validate.

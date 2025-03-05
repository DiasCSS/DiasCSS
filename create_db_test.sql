--  Customers 
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(222),
    email VARCHAR(222) UNIQUE,
    country VARCHAR(222)
);

--  Products 
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(222),
    price DECIMAL(10,2) ,
    category VARCHAR(222)
);

--  Sales Transactions 
CREATE TABLE sales_transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INT,
    product_id INT,
    purchase_date DATE,
    quantity INT CHECK (quantity > 0),
    total_amount DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

--  Shipping Details 
CREATE TABLE shipping_details (
    transaction_id INT PRIMARY KEY,
    shipping_date DATE,
    shipping_address VARCHAR(222),
    city VARCHAR(222),
    country VARCHAR(222),
    FOREIGN KEY (transaction_id) REFERENCES sales_transactions(transaction_id)
);

--   Monthly sales and moving average qeury
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', purchase_date) AS month,
        SUM(total_amount) AS total_sales,
        COUNT(transaction_id) AS total_transactions
    FROM sales_transactions
    GROUP BY DATE_TRUNC('month', purchase_date)
),
moving_avg AS (
    SELECT
        month,
        total_sales,
        total_transactions,
        (SELECT AVG(total_sales) 
         FROM monthly_sales m2 
         WHERE m2.month BETWEEN monthly_sales.month - INTERVAL '2 months' AND monthly_sales.month) AS moving_avg_sales
    FROM monthly_sales
)
SELECT * FROM moving_avg ORDER BY month;

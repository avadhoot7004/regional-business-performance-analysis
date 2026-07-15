# Data Profiling & Quality Assessment Report (Official Kaggle Superstore Dataset)

This report outlines the profiling results, identified data quality issues, and core business assumptions for the official **9,994-row Kaggle Superstore dataset**.

---

## 1. Dataset Overview

*   **Total Records:** 9,994
*   **Total Columns:** 21
*   **Unique Orders:** 5,009
*   **Unique Customers:** 793 (with a strictly 1-to-1 ID-to-name mapping)
*   **Unique Products:** 1,862
*   **Date Range:** January 3, 2014 to December 30, 2017 (Order Dates)

---

## 2. Column Schema & Data Types

Below is the schema of the raw Kaggle dataset:

| Column Name       | Raw Data Type | Null Count | Null % | Unique Count | Business Concept                                                       |
| :------------------| :--------------| :-----------| :-------| :-------------| :-----------------------------------------------------------------------|
| **Row ID**        | `int64`       | 0          | 0.00%  | 9,994       | Sequential integer unique row identifier.                              |
| **Order ID**      | `str`         | 0          | 0.00%  | 5,009       | Transactional ID representing a single cart/checkout.                  |
| **Order Date**    | `str`         | 0          | 0.00%  | 1,237       | Date the order was placed (stored as string).                          |
| **Ship Date**     | `str`         | 0          | 0.00%  | 1,334       | Date the order shipped (stored as string).                             |
| **Ship Mode**     | `str`         | 0          | 0.00%  | 4            | Shipping method (Standard Class, Second Class, First Class, Same Day). |
| **Customer ID**   | `str`         | 0          | 0.00%  | 793          | Unique alphanumeric identifier for the customer.                       |
| **Customer Name** | `str`         | 0          | 0.00%  | 793          | Full name of the customer.                                             |
| **Segment**       | `str`         | 0          | 0.00%  | 3            | Customer market segment (Consumer, Corporate, Home Office).            |
| **Country**       | `str`         | 0          | 0.00%  | 1            | Country of sale (always "United States").                              |
| **City**          | `str`         | 0          | 0.00%  | 531          | Delivery city.                                                         |
| **State**         | `str`         | 0          | 0.00%  | 49           | Delivery US State.                                                     |
| **Postal Code**   | `int64`       | 0          | 0.00%  | 631          | US ZIP code.                                                           |
| **Region**        | `str`         | 0          | 0.00%  | 4            | Broad regional classification (East, West, Central, South).            |
| **Product ID**    | `str`         | 0          | 0.00%  | 1,862       | Alphanumeric product item identifier.                                  |
| **Category**      | `str`         | 0          | 0.00%  | 3            | High-level category (Furniture, Office Supplies, Technology).          |
| **Sub-Category**  | `str`         | 0          | 0.00%  | 17           | Detailed product category (e.g. Chairs, Paper, Binders).               |
| **Product Name**  | `str`         | 0          | 0.00%  | 1,850       | Text name of the product.                                              |
| **Sales**         | `float64`     | 0          | 0.00%  | 5,825       | Gross sales revenue of the line item (decimal).                        |
| **Quantity**      | `int64`       | 0          | 0.00%  | 14           | Number of units purchased (integer).                                   |
| **Discount**      | `float64`     | 0          | 0.00%  | 12           | Discount percentage applied (decimal, e.g. 0.0 to 0.8).                |
| **Profit**        | `float64`     | 0          | 0.00%  | 7,287       | Net profit or loss of the line item (decimal).                         |

---

## 3. Data Quality Issues Identified

During our profiling phase, we discovered three distinct data quality issues that must be resolved in our warehouse ingestion and staging phases:

### Issue 1: Truncated Leading Zeros in US Postal Codes
*   **Description:** `Postal Code` is loaded as an integer. 449 rows have zip codes with value < 10,000 (e.g. `6824` instead of `06824` for Connecticut).
*   **Impact:** Zip codes in the northeast region appear as 4 digits, which is incorrect for geographic plotting or mapping.
*   **Resolution:** In the staging layer, we will pad these values with leading zeros to format them as standard 5-character strings.

### Issue 2: Duplicate Product Entries in Single Orders
*   **Description:** There are 8 occurrences of the same `Order ID` + `Product ID` appearing multiple times in the dataset.
*   **Impact:** A standard natural key of `Order ID` + `Product ID` is not unique. 
*   **Deep Dive:** For example, in Order `CA-2016-129714`, Product `OFF-PA-10001970` appears twice: once with a quantity of 2 (Row ID 351) and once with a quantity of 4 (Row ID 353). These represent separate line items under the same order.
*   **Resolution:** We must use `Row ID` as our primary key grain. When creating surrogate hash keys in dbt staging, we should hash the `Row ID` or use it directly as the unique identifier.

### Issue 3: Text-based Date Fields
*   **Description:** `Order Date` and `Ship Date` are stored as text in `M/D/YYYY` format (e.g. `11/8/2016`).
*   **Impact:** Database engines like Snowflake cannot perform date math or sorting without parsing.
*   **Resolution:** In staging, we will explicitly cast these text strings to standard SQL dates using Snowflake's `TRY_TO_DATE(order_date, 'MM/DD/YYYY')`.

---

## 4. Analytical Assumptions & Business Rules

We establish the following parameters for data warehousing:

1.  **Unique Business Grain:** The grain of the dataset is **Order Line Item** (uniquely defined by `Row ID`).
2.  **Customer Entity definition:** Customer ID and Customer Name have a strict 1-to-1 relationship. Therefore, `Customer ID` is the clean key for customer dimension modeling.
3.  **Unprofitable Orders:** 1,871 records have negative profit (sales with negative return). This is a normal retail outcome (due to high discounts) and should be preserved in the marts.
4.  **Date Flow Integrity:** We verified that `Order Date` <= `Ship Date` for all records. Maximum shipping lag is 7 days, which is within operational parameters (unlike the Packt dataset where anomalies existed).
5.  **Standard Hierarchy:** The product classification hierarchy is:
    *   `Category` (Broad Category: e.g., Technology)
    *   `Sub-Category` (Detailed Category: e.g., Phones)
    *   `Product ID` / `Product Name` (Product Item)

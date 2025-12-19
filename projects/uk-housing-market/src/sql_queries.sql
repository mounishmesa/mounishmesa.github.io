-- =============================================================================
-- UK Housing Market Analysis - SQL Queries
-- =============================================================================
-- Database: housing_market.db (SQLite)
-- Author: Mounish Mesa
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. OVERVIEW QUERIES
-- -----------------------------------------------------------------------------

-- Total transactions and market value
SELECT 
    COUNT(*) AS total_transactions,
    ROUND(SUM(price), 0) AS total_market_value,
    ROUND(AVG(price), 0) AS average_price,
    ROUND(MIN(price), 0) AS min_price,
    ROUND(MAX(price), 0) AS max_price
FROM transactions;


-- Transactions by year
SELECT 
    year,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(SUM(price), 0) AS total_value
FROM transactions
GROUP BY year
ORDER BY year;


-- -----------------------------------------------------------------------------
-- 2. BOROUGH ANALYSIS
-- -----------------------------------------------------------------------------

-- Average price by borough (sorted by price)
SELECT 
    district AS borough,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(MIN(price), 0) AS min_price,
    ROUND(MAX(price), 0) AS max_price
FROM transactions
GROUP BY district
ORDER BY avg_price DESC;


-- Top 10 most expensive boroughs
SELECT 
    district AS borough,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(AVG(price) - (SELECT AVG(price) FROM transactions), 0) AS vs_london_avg
FROM transactions
GROUP BY district
ORDER BY avg_price DESC
LIMIT 10;


-- Year-over-year price change by borough
WITH yearly_avg AS (
    SELECT 
        year,
        district,
        AVG(price) AS avg_price
    FROM transactions
    GROUP BY year, district
)
SELECT 
    curr.district AS borough,
    curr.year,
    ROUND(curr.avg_price, 0) AS current_avg,
    ROUND(prev.avg_price, 0) AS previous_avg,
    ROUND((curr.avg_price - prev.avg_price) / prev.avg_price * 100, 2) AS yoy_change_pct
FROM yearly_avg curr
JOIN yearly_avg prev 
    ON curr.district = prev.district 
    AND curr.year = prev.year + 1
ORDER BY curr.year DESC, yoy_change_pct DESC;


-- -----------------------------------------------------------------------------
-- 3. PROPERTY TYPE ANALYSIS
-- -----------------------------------------------------------------------------

-- Average price by property type
SELECT 
    property_type,
    property_type_name,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1) AS pct_of_total
FROM transactions
GROUP BY property_type, property_type_name
ORDER BY avg_price DESC;


-- Property type breakdown by borough
SELECT 
    district AS borough,
    property_type_name,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price
FROM transactions
GROUP BY district, property_type_name
ORDER BY district, avg_price DESC;


-- Most common property type in each borough
WITH ranked AS (
    SELECT 
        district,
        property_type_name,
        COUNT(*) AS cnt,
        ROW_NUMBER() OVER (PARTITION BY district ORDER BY COUNT(*) DESC) AS rn
    FROM transactions
    GROUP BY district, property_type_name
)
SELECT 
    district AS borough,
    property_type_name AS most_common_type,
    cnt AS transactions
FROM ranked
WHERE rn = 1
ORDER BY district;


-- -----------------------------------------------------------------------------
-- 4. TIME-BASED ANALYSIS
-- -----------------------------------------------------------------------------

-- Monthly transaction volume and prices
SELECT 
    year_month,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(SUM(price), 0) AS total_value
FROM transactions
GROUP BY year_month
ORDER BY year_month;


-- Quarterly analysis
SELECT 
    year,
    quarter,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(SUM(price) / 1000000, 1) AS total_value_millions
FROM transactions
GROUP BY year, quarter
ORDER BY year, quarter;


-- Seasonal patterns (average by month across all years)
SELECT 
    month,
    CASE month
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        WHEN 12 THEN 'December'
    END AS month_name,
    COUNT(*) AS avg_transactions,
    ROUND(AVG(price), 0) AS avg_price
FROM transactions
GROUP BY month
ORDER BY month;


-- -----------------------------------------------------------------------------
-- 5. REGIONAL ANALYSIS
-- -----------------------------------------------------------------------------

-- London regions comparison
SELECT 
    region,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(MIN(price), 0) AS min_price,
    ROUND(MAX(price), 0) AS max_price,
    COUNT(DISTINCT district) AS num_boroughs
FROM transactions
WHERE region IS NOT NULL
GROUP BY region
ORDER BY avg_price DESC;


-- Regional price trends over years
SELECT 
    year,
    region,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price
FROM transactions
WHERE region IS NOT NULL
GROUP BY year, region
ORDER BY year, region;


-- -----------------------------------------------------------------------------
-- 6. POSTCODE ANALYSIS
-- -----------------------------------------------------------------------------

-- Top 20 most expensive postcode districts
SELECT 
    postcode_district,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(MIN(price), 0) AS min_price,
    ROUND(MAX(price), 0) AS max_price
FROM transactions
WHERE postcode_district IS NOT NULL
GROUP BY postcode_district
HAVING COUNT(*) >= 50  -- Minimum transactions for reliability
ORDER BY avg_price DESC
LIMIT 20;


-- Postcode district price bands
SELECT 
    postcode_district,
    CASE 
        WHEN AVG(price) >= 2000000 THEN 'Ultra Prime (£2M+)'
        WHEN AVG(price) >= 1000000 THEN 'Prime (£1M-£2M)'
        WHEN AVG(price) >= 750000 THEN 'Premium (£750k-£1M)'
        WHEN AVG(price) >= 500000 THEN 'Mid-Market (£500k-£750k)'
        ELSE 'Entry Level (<£500k)'
    END AS price_band,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price
FROM transactions
WHERE postcode_district IS NOT NULL
GROUP BY postcode_district
HAVING COUNT(*) >= 50
ORDER BY avg_price DESC;


-- -----------------------------------------------------------------------------
-- 7. PRICE BAND ANALYSIS
-- -----------------------------------------------------------------------------

-- Distribution by price bands
SELECT 
    price_band,
    COUNT(*) AS transactions,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1) AS pct_of_total,
    ROUND(AVG(price), 0) AS avg_price_in_band
FROM transactions
GROUP BY price_band
ORDER BY 
    CASE price_band
        WHEN 'Under £250k' THEN 1
        WHEN '£250k-£500k' THEN 2
        WHEN '£500k-£750k' THEN 3
        WHEN '£750k-£1M' THEN 4
        WHEN '£1M-£2M' THEN 5
        WHEN 'Over £2M' THEN 6
    END;


-- Price bands by borough
SELECT 
    district AS borough,
    price_band,
    COUNT(*) AS transactions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY district), 1) AS pct_in_borough
FROM transactions
GROUP BY district, price_band
ORDER BY district, 
    CASE price_band
        WHEN 'Under £250k' THEN 1
        WHEN '£250k-£500k' THEN 2
        WHEN '£500k-£750k' THEN 3
        WHEN '£750k-£1M' THEN 4
        WHEN '£1M-£2M' THEN 5
        WHEN 'Over £2M' THEN 6
    END;


-- -----------------------------------------------------------------------------
-- 8. AFFORDABILITY METRICS
-- -----------------------------------------------------------------------------

-- Assuming average London salary of £45,000
-- Price to income ratio by borough

SELECT 
    district AS borough,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(AVG(price) / 45000, 1) AS price_to_income_ratio,
    CASE 
        WHEN AVG(price) / 45000 > 20 THEN 'Severely Unaffordable'
        WHEN AVG(price) / 45000 > 15 THEN 'Very Unaffordable'
        WHEN AVG(price) / 45000 > 10 THEN 'Unaffordable'
        WHEN AVG(price) / 45000 > 5 THEN 'Moderately Affordable'
        ELSE 'Relatively Affordable'
    END AS affordability_rating
FROM transactions
GROUP BY district
ORDER BY price_to_income_ratio DESC;


-- -----------------------------------------------------------------------------
-- 9. NEW BUILD VS ESTABLISHED
-- -----------------------------------------------------------------------------

-- New build premium analysis
SELECT 
    old_new AS status,
    CASE old_new 
        WHEN 'Y' THEN 'New Build'
        WHEN 'N' THEN 'Established'
    END AS status_name,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price
FROM transactions
GROUP BY old_new;


-- New build premium by borough
WITH new_vs_old AS (
    SELECT 
        district,
        AVG(CASE WHEN old_new = 'Y' THEN price END) AS new_build_avg,
        AVG(CASE WHEN old_new = 'N' THEN price END) AS established_avg
    FROM transactions
    GROUP BY district
)
SELECT 
    district AS borough,
    ROUND(new_build_avg, 0) AS new_build_avg,
    ROUND(established_avg, 0) AS established_avg,
    ROUND((new_build_avg - established_avg) / established_avg * 100, 1) AS new_build_premium_pct
FROM new_vs_old
WHERE new_build_avg IS NOT NULL AND established_avg IS NOT NULL
ORDER BY new_build_premium_pct DESC;


-- -----------------------------------------------------------------------------
-- 10. FREEHOLD VS LEASEHOLD
-- -----------------------------------------------------------------------------

-- Duration type analysis
SELECT 
    duration,
    CASE duration 
        WHEN 'F' THEN 'Freehold'
        WHEN 'L' THEN 'Leasehold'
    END AS duration_type,
    COUNT(*) AS transactions,
    ROUND(AVG(price), 0) AS avg_price,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1) AS pct_of_total
FROM transactions
GROUP BY duration;


-- Freehold vs Leasehold by property type
SELECT 
    property_type_name,
    ROUND(AVG(CASE WHEN duration = 'F' THEN price END), 0) AS freehold_avg,
    ROUND(AVG(CASE WHEN duration = 'L' THEN price END), 0) AS leasehold_avg,
    SUM(CASE WHEN duration = 'F' THEN 1 ELSE 0 END) AS freehold_count,
    SUM(CASE WHEN duration = 'L' THEN 1 ELSE 0 END) AS leasehold_count
FROM transactions
GROUP BY property_type_name
ORDER BY property_type_name;

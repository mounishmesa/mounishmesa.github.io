-- ============================================================
-- UK Cost of Living Analysis - SQL Queries
-- ============================================================
-- Database: cost_of_living.db
-- Author: Mounish Mesa
-- Date: December 2024
-- ============================================================

-- ============================================================
-- SECTION 1: OVERVIEW & CURRENT STATE
-- ============================================================

-- Q1.1: Latest inflation figures
SELECT 
    date,
    cpi_annual AS "CPI Rate (%)",
    cpih_annual AS "CPIH Rate (%)",
    inflation_regime AS "Regime"
FROM cpi_data
WHERE date = (SELECT MAX(date) FROM cpi_data)
;

-- Q1.2: Current year summary (2024)
SELECT 
    year,
    COUNT(*) AS months_recorded,
    ROUND(AVG(cpi_annual), 2) AS avg_cpi,
    ROUND(MIN(cpi_annual), 2) AS min_cpi,
    ROUND(MAX(cpi_annual), 2) AS max_cpi,
    ROUND(AVG(cpih_annual), 2) AS avg_cpih
FROM cpi_data
WHERE year = 2024
GROUP BY year
;

-- Q1.3: Inflation vs BOE 2% target - current year
SELECT 
    date,
    cpi_annual,
    2.0 AS boe_target,
    ROUND(cpi_annual - 2.0, 2) AS deviation,
    CASE 
        WHEN cpi_annual > 2.0 THEN 'Above Target'
        WHEN cpi_annual < 2.0 THEN 'Below Target'
        ELSE 'On Target'
    END AS status
FROM cpi_data
WHERE year >= 2024
ORDER BY date
;

-- Q1.4: Summary statistics by decade
SELECT 
    (year / 10) * 10 AS decade,
    COUNT(*) AS months,
    ROUND(AVG(cpi_annual), 2) AS avg_inflation,
    ROUND(MAX(cpi_annual), 2) AS peak_inflation,
    ROUND(MIN(cpi_annual), 2) AS lowest_inflation
FROM cpi_data
GROUP BY decade
ORDER BY decade
;

-- ============================================================
-- SECTION 2: TIME SERIES ANALYSIS
-- ============================================================

-- Q2.1: Monthly CPI trend (last 24 months)
SELECT 
    date,
    cpi_annual,
    cpih_annual,
    inflation_regime
FROM cpi_data
WHERE date >= DATE('now', '-24 months')
ORDER BY date
;

-- Q2.2: Year-over-Year comparison
SELECT 
    year,
    ROUND(AVG(cpi_annual), 2) AS annual_avg,
    ROUND(AVG(cpi_annual) - LAG(AVG(cpi_annual)) OVER (ORDER BY year), 2) AS yoy_change
FROM cpi_data
WHERE year >= 2015
GROUP BY year
ORDER BY year
;

-- Q2.3: Monthly seasonality analysis
SELECT 
    month,
    month_name,
    ROUND(AVG(cpi_annual), 2) AS avg_inflation,
    COUNT(*) AS sample_size
FROM cpi_data
WHERE year >= 2015
GROUP BY month, month_name
ORDER BY month
;

-- Q2.4: Quarterly averages
SELECT 
    year,
    CASE 
        WHEN month IN (1,2,3) THEN 'Q1'
        WHEN month IN (4,5,6) THEN 'Q2'
        WHEN month IN (7,8,9) THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    ROUND(AVG(cpi_annual), 2) AS avg_cpi
FROM cpi_data
WHERE year >= 2020
GROUP BY year, quarter
ORDER BY year, quarter
;

-- Q2.5: Rolling 12-month average
SELECT 
    date,
    cpi_annual,
    ROUND(AVG(cpi_annual) OVER (
        ORDER BY date 
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_12m_avg
FROM cpi_data
WHERE year >= 2020
ORDER BY date
;

-- ============================================================
-- SECTION 3: CATEGORY BREAKDOWN
-- ============================================================

-- Q3.1: Food inflation trend
SELECT 
    date,
    food_inflation,
    ROUND(AVG(food_inflation) OVER (ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW), 2) AS rolling_avg
FROM cpi_data
WHERE food_inflation IS NOT NULL
    AND year >= 2020
ORDER BY date
;

-- Q3.2: Housing & Energy inflation trend
SELECT 
    date,
    housing_energy_inflation,
    cpi_annual,
    ROUND(housing_energy_inflation - cpi_annual, 2) AS diff_from_headline
FROM cpi_data
WHERE housing_energy_inflation IS NOT NULL
    AND year >= 2020
ORDER BY date
;

-- Q3.3: Category comparison (from generated data)
SELECT 
    year,
    ROUND(AVG(food_beverages), 2) AS food,
    ROUND(AVG(housing_energy), 2) AS housing_energy,
    ROUND(AVG(transport), 2) AS transport,
    ROUND(AVG(recreation_culture), 2) AS recreation,
    ROUND(AVG(restaurants_hotels), 2) AS restaurants
FROM cpi_data
WHERE food_beverages IS NOT NULL
GROUP BY year
ORDER BY year
;

-- Q3.4: Peak inflation by category (2022-2023 crisis)
SELECT 
    'Food & Beverages' AS category, MAX(food_inflation) AS peak, 
    (SELECT date FROM cpi_data WHERE food_inflation = (SELECT MAX(food_inflation) FROM cpi_data)) AS peak_date
FROM cpi_data WHERE food_inflation IS NOT NULL
UNION ALL
SELECT 
    'Housing & Energy', MAX(housing_energy_inflation),
    (SELECT date FROM cpi_data WHERE housing_energy_inflation = (SELECT MAX(housing_energy_inflation) FROM cpi_data))
FROM cpi_data WHERE housing_energy_inflation IS NOT NULL
;

-- ============================================================
-- SECTION 4: REGIONAL ANALYSIS
-- ============================================================

-- Q4.1: Regional price index ranking (latest year)
SELECT 
    region,
    overall_index,
    housing_index,
    ROUND(overall_index - 100, 2) AS diff_from_uk_avg,
    RANK() OVER (ORDER BY overall_index DESC) AS rank
FROM regional_prices
WHERE year = (SELECT MAX(year) FROM regional_prices)
ORDER BY overall_index DESC
;

-- Q4.2: London vs Rest of UK
SELECT 
    year,
    MAX(CASE WHEN region = 'London' THEN overall_index END) AS london_index,
    ROUND(AVG(CASE WHEN region != 'London' THEN overall_index END), 2) AS rest_of_uk,
    ROUND(MAX(CASE WHEN region = 'London' THEN overall_index END) - 
          AVG(CASE WHEN region != 'London' THEN overall_index END), 2) AS london_premium
FROM regional_prices
GROUP BY year
ORDER BY year
;

-- Q4.3: Regional housing cost comparison
SELECT 
    region,
    housing_index,
    ROUND(housing_index - 100, 2) AS vs_uk_average,
    CASE 
        WHEN housing_index >= 120 THEN 'Very Expensive'
        WHEN housing_index >= 105 THEN 'Above Average'
        WHEN housing_index >= 95 THEN 'Average'
        ELSE 'Below Average'
    END AS affordability
FROM regional_prices
WHERE year = (SELECT MAX(year) FROM regional_prices)
ORDER BY housing_index DESC
;

-- Q4.4: North-South divide
SELECT 
    year,
    ROUND(AVG(CASE WHEN region IN ('London', 'South East', 'South West', 'East of England') 
              THEN overall_index END), 2) AS south_avg,
    ROUND(AVG(CASE WHEN region IN ('North East', 'North West', 'Yorkshire and Humber') 
              THEN overall_index END), 2) AS north_avg,
    ROUND(AVG(CASE WHEN region IN ('London', 'South East', 'South West', 'East of England') 
              THEN overall_index END) - 
          AVG(CASE WHEN region IN ('North East', 'North West', 'Yorkshire and Humber') 
              THEN overall_index END), 2) AS north_south_gap
FROM regional_prices
GROUP BY year
ORDER BY year
;

-- Q4.5: Devolved nations comparison
SELECT 
    year,
    MAX(CASE WHEN region = 'Scotland' THEN overall_index END) AS scotland,
    MAX(CASE WHEN region = 'Wales' THEN overall_index END) AS wales,
    MAX(CASE WHEN region = 'Northern Ireland' THEN overall_index END) AS northern_ireland,
    ROUND(AVG(CASE WHEN region NOT IN ('Scotland', 'Wales', 'Northern Ireland') 
              THEN overall_index END), 2) AS england_avg
FROM regional_prices
GROUP BY year
ORDER BY year
;

-- ============================================================
-- SECTION 5: WAGES & PURCHASING POWER
-- ============================================================

-- Q5.1: Latest wages data
SELECT 
    date,
    avg_weekly_earnings,
    private_sector,
    public_sector,
    yoy_change
FROM wages
WHERE date = (SELECT MAX(date) FROM wages)
;

-- Q5.2: Wage growth vs inflation
SELECT 
    w.date,
    w.avg_weekly_earnings,
    w.yoy_change AS wage_growth,
    c.cpi_annual AS inflation,
    ROUND(w.yoy_change - c.cpi_annual, 2) AS real_wage_change
FROM wages w
LEFT JOIN cpi_data c ON w.date = c.date
WHERE w.date >= '2020-01-01'
ORDER BY w.date
;

-- Q5.3: Public vs Private sector wages
SELECT 
    year,
    ROUND(AVG(private_sector), 2) AS avg_private,
    ROUND(AVG(public_sector), 2) AS avg_public,
    ROUND(AVG(public_sector) - AVG(private_sector), 2) AS public_premium
FROM wages
GROUP BY year
ORDER BY year
;

-- Q5.4: Purchasing power erosion since 2020
SELECT 
    date,
    avg_weekly_earnings AS nominal_wage,
    ROUND(avg_weekly_earnings / (1 + cumulative_inflation/100), 2) AS real_wage_2020
FROM wages w
JOIN cpi_data c ON w.date = c.date
WHERE w.date >= '2020-01-01'
ORDER BY w.date
;

-- ============================================================
-- SECTION 6: BASKET OF GOODS
-- ============================================================

-- Q6.1: Current prices vs 2020
SELECT 
    b1.item,
    b1.category,
    b2.average_price AS price_2020,
    b1.average_price AS price_2024,
    ROUND((b1.average_price - b2.average_price) / b2.average_price * 100, 1) AS pct_change
FROM basket_of_goods b1
JOIN basket_of_goods b2 ON b1.item = b2.item
WHERE b1.year = 2024 AND b2.year = 2020
ORDER BY pct_change DESC
;

-- Q6.2: Category price trends
SELECT 
    year,
    category,
    ROUND(AVG(average_price), 2) AS avg_price,
    COUNT(*) AS items
FROM basket_of_goods
GROUP BY year, category
ORDER BY category, year
;

-- Q6.3: Most inflated items since 2020
SELECT 
    item,
    category,
    ROUND((MAX(CASE WHEN year = 2024 THEN average_price END) - 
           MAX(CASE WHEN year = 2020 THEN average_price END)) / 
           MAX(CASE WHEN year = 2020 THEN average_price END) * 100, 1) AS inflation_pct
FROM basket_of_goods
GROUP BY item, category
ORDER BY inflation_pct DESC
LIMIT 10
;

-- Q6.4: Energy price changes
SELECT 
    year,
    MAX(CASE WHEN item LIKE '%Electricity%' THEN average_price END) AS electricity_kwh,
    MAX(CASE WHEN item LIKE '%Gas%' THEN average_price END) AS gas_kwh,
    MAX(CASE WHEN item LIKE '%Petrol%' THEN average_price END) AS petrol_litre
FROM basket_of_goods
WHERE category IN ('Energy', 'Transport')
GROUP BY year
ORDER BY year
;

-- ============================================================
-- SECTION 7: INFLATION REGIME ANALYSIS
-- ============================================================

-- Q7.1: Time spent in each regime
SELECT 
    inflation_regime,
    COUNT(*) AS months,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cpi_data WHERE inflation_regime IS NOT NULL), 1) AS pct_of_time,
    ROUND(AVG(cpi_annual), 2) AS avg_rate
FROM cpi_data
WHERE inflation_regime IS NOT NULL
GROUP BY inflation_regime
ORDER BY avg_rate DESC
;

-- Q7.2: High inflation periods (>5%)
SELECT 
    date,
    cpi_annual,
    inflation_regime
FROM cpi_data
WHERE cpi_annual > 5
ORDER BY date
;

-- Q7.3: Deflation periods
SELECT 
    date,
    cpi_annual,
    month_name
FROM cpi_data
WHERE cpi_annual < 0
ORDER BY date
;

-- Q7.4: Regime transitions
SELECT 
    date,
    cpi_annual,
    inflation_regime,
    LAG(inflation_regime) OVER (ORDER BY date) AS previous_regime
FROM cpi_data
WHERE year >= 2020
ORDER BY date
;

-- ============================================================
-- SECTION 8: COMPARATIVE ANALYSIS
-- ============================================================

-- Q8.1: 2022 Crisis vs Historical comparison
SELECT 
    'Pre-Crisis (2015-2019)' AS period,
    ROUND(AVG(cpi_annual), 2) AS avg_inflation,
    ROUND(MAX(cpi_annual), 2) AS peak
FROM cpi_data WHERE year BETWEEN 2015 AND 2019
UNION ALL
SELECT 
    'Crisis (2022-2023)',
    ROUND(AVG(cpi_annual), 2),
    ROUND(MAX(cpi_annual), 2)
FROM cpi_data WHERE year BETWEEN 2022 AND 2023
UNION ALL
SELECT 
    'Recovery (2024)',
    ROUND(AVG(cpi_annual), 2),
    ROUND(MAX(cpi_annual), 2)
FROM cpi_data WHERE year = 2024
;

-- Q8.2: COVID impact on inflation
SELECT 
    year,
    month_name,
    cpi_annual,
    CASE 
        WHEN year = 2020 AND month BETWEEN 3 AND 6 THEN 'Lockdown'
        WHEN year = 2020 AND month > 6 THEN 'Recovery Start'
        WHEN year = 2021 THEN 'Reopening'
        ELSE 'Post-COVID'
    END AS covid_phase
FROM cpi_data
WHERE year >= 2020 AND year <= 2021
ORDER BY date
;

-- ============================================================
-- SECTION 9: FORECASTING INPUTS
-- ============================================================

-- Q9.1: Recent trend (for forecasting)
SELECT 
    date,
    cpi_annual,
    ROUND(AVG(cpi_annual) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma_3m,
    ROUND(AVG(cpi_annual) OVER (ORDER BY date ROWS BETWEEN 5 PRECEDING AND CURRENT ROW), 2) AS ma_6m
FROM cpi_data
WHERE date >= '2024-01-01'
ORDER BY date
;

-- Q9.2: Volatility measure
SELECT 
    year,
    ROUND(AVG(cpi_annual), 2) AS mean,
    ROUND(MAX(cpi_annual) - MIN(cpi_annual), 2) AS range,
    COUNT(*) AS observations
FROM cpi_data
WHERE year >= 2020
GROUP BY year
ORDER BY year
;

-- ============================================================
-- SECTION 10: EXECUTIVE SUMMARY QUERIES
-- ============================================================

-- Q10.1: Key metrics dashboard
SELECT 
    (SELECT ROUND(cpi_annual, 2) FROM cpi_data ORDER BY date DESC LIMIT 1) AS current_cpi,
    (SELECT ROUND(AVG(cpi_annual), 2) FROM cpi_data WHERE year = 2024) AS ytd_avg_2024,
    (SELECT ROUND(MAX(cpi_annual), 2) FROM cpi_data) AS all_time_peak,
    (SELECT date FROM cpi_data WHERE cpi_annual = (SELECT MAX(cpi_annual) FROM cpi_data)) AS peak_date,
    (SELECT region FROM regional_prices WHERE year = 2023 ORDER BY overall_index DESC LIMIT 1) AS most_expensive_region,
    (SELECT region FROM regional_prices WHERE year = 2023 ORDER BY overall_index ASC LIMIT 1) AS cheapest_region
;

-- Q10.2: Year-to-date summary
SELECT 
    'CPI' AS metric,
    ROUND(AVG(cpi_annual), 2) AS avg_2024,
    ROUND(MIN(cpi_annual), 2) AS min_2024,
    ROUND(MAX(cpi_annual), 2) AS max_2024
FROM cpi_data WHERE year = 2024
UNION ALL
SELECT 
    'CPIH',
    ROUND(AVG(cpih_annual), 2),
    ROUND(MIN(cpih_annual), 2),
    ROUND(MAX(cpih_annual), 2)
FROM cpi_data WHERE year = 2024 AND cpih_annual IS NOT NULL
;

-- End of queries
-- ============================================================
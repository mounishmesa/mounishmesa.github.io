# UK Cost of Living Analysis 🇬🇧📊

## Project Overview

An in-depth analysis of UK inflation trends, regional price variations, and purchasing power using official ONS (Office for National Statistics) data. This project demonstrates advanced data analysis skills across Python, SQL, Excel, and Power BI.

**Live Dashboard:** [Coming Soon]

**Portfolio:** [mounishmesa.github.io](https://mounishmesa.github.io)

---

## 🎯 Objectives

1. **Track Inflation Trends** - Analyze CPI/CPIH movements from 2019-2024
2. **Category Analysis** - Deep-dive into food, energy, housing, and transport costs
3. **Regional Comparison** - Compare cost of living across UK regions
4. **Purchasing Power** - Calculate real wage changes and affordability indices
5. **Interactive Tools** - Build what-if scenarios for salary planning

---

## 📊 Key Findings

> *Analysis in progress - findings will be updated upon completion*

### Preview Metrics
- **Current UK Inflation Rate:** TBD
- **Highest Inflation Category:** TBD
- **Most Expensive Region:** TBD
- **Real Wage Change (YoY):** TBD

---

## 🗂️ Project Structure

```
cost-of-living/
├── README.md                    # This file
├── app.py                       # Streamlit dashboard
├── requirements.txt             # Python dependencies
├── data/
│   ├── raw/                     # Original ONS data
│   └── processed/               # Cleaned datasets
├── src/
│   ├── 01_download_data.py      # ONS API data fetching
│   ├── 02_data_cleaning.py      # Data transformation
│   └── 03_analysis.py           # Statistical analysis
├── sql/
│   └── queries.sql              # 50+ analysis queries
├── excel/
│   └── cost_of_living_analysis.xlsx
├── powerbi/
│   └── UK_Cost_of_Living.pbix
└── outputs/
    ├── charts/                  # Visualization exports
    └── reports/                 # Analysis summaries
```

---

## 📈 Data Sources

| Dataset | Source | Period | Records |
|---------|--------|--------|---------|
| Consumer Price Index (CPI) | ONS | 2019-2024 | TBD |
| CPIH (with Housing) | ONS | 2019-2024 | TBD |
| Regional Price Parities | ONS | 2019-2023 | TBD |
| Average Weekly Earnings | ONS | 2019-2024 | TBD |

**Data License:** Open Government Licence v3.0

---

## 🔧 Technologies Used

### Data Processing
- **Python 3.11** - Core programming
- **pandas** - Data manipulation
- **requests** - ONS API integration
- **SQLite** - Database storage

### Visualization
- **Plotly** - Interactive charts
- **Matplotlib/Seaborn** - Static visualizations
- **Streamlit** - Web dashboard
- **Power BI** - Business intelligence dashboard

### Analysis
- **SQL** - Complex queries, window functions, CTEs
- **Excel** - Pivot tables, XLOOKUP, What-If Analysis
- **DAX** - Power BI measures and calculations

---

## 📊 Analysis Sections

### 1. Inflation Overview
- Monthly and annual CPI/CPIH trends
- Comparison to Bank of England 2% target
- Historical context (2008 crisis, COVID, 2022 energy crisis)

### 2. Category Breakdown
| Category | Weight in CPI | Key Drivers |
|----------|--------------|-------------|
| Housing & Energy | ~32% | Gas, electricity, rent |
| Food & Beverages | ~11% | Groceries, dining |
| Transport | ~10% | Fuel, public transport |
| Recreation | ~9% | Entertainment, holidays |

### 3. Regional Analysis
- London vs National Average
- North-South price divide
- Devolved nations comparison
- Urban vs Rural costs

### 4. Purchasing Power Calculator
Interactive tool to calculate:
- Required salary increase to match inflation
- Real wage change over time
- Regional cost comparison

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
Power BI Desktop (optional)
Excel 2016+ (optional)
```

### Installation
```bash
# Clone repository
git clone https://github.com/mounishmesa/mounishmesa.github.io.git
cd projects/uk-cost-of-living

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run Analysis
```bash
# Download latest data
python src/01_download_data.py

# Clean and process
python src/02_data_cleaning.py

# Generate analysis
python src/03_analysis.py

# Launch dashboard
streamlit run app.py
```

---

## 📋 SQL Query Examples

### Average Inflation by Category
```sql
SELECT 
    category,
    ROUND(AVG(annual_rate), 2) AS avg_inflation,
    MAX(annual_rate) AS peak_inflation,
    MIN(annual_rate) AS lowest_inflation
FROM cpi_data
WHERE year BETWEEN 2022 AND 2024
GROUP BY category
ORDER BY avg_inflation DESC;
```

### Regional Price Comparison
```sql
WITH regional_avg AS (
    SELECT 
        region,
        AVG(price_index) AS avg_index
    FROM regional_prices
    GROUP BY region
)
SELECT 
    region,
    avg_index,
    ROUND((avg_index - 100) * 100 / 100, 1) AS pct_diff_from_uk
FROM regional_avg
ORDER BY avg_index DESC;
```

---

## 📊 Power BI Features

### DAX Measures
```dax
// Year-over-Year Inflation Change
YoY Change = 
VAR CurrentYear = SELECTEDVALUE(CPI[Year])
VAR PrevYearRate = CALCULATE(AVERAGE(CPI[Rate]), CPI[Year] = CurrentYear - 1)
RETURN
    AVERAGE(CPI[Rate]) - PrevYearRate

// Real Wage Growth
Real Wage Growth = 
    [Average Wage Growth] - [Average Inflation Rate]

// Purchasing Power Index
Purchasing Power = 
    DIVIDE(100, [Cumulative Inflation], 100)
```

### Interactive Features
- Year and category slicers
- Drill-through to regional details
- What-if parameter for salary scenarios
- Bookmarks for key insights

---

## 📁 Excel Workbook Contents

| Sheet | Description |
|-------|-------------|
| Raw Data | Imported ONS datasets |
| Cleaned Data | Processed and validated |
| Pivot Analysis | Multi-dimensional analysis |
| Regional Comparison | Price parity calculations |
| Salary Calculator | What-if analysis tool |
| Dashboard | Summary visualizations |

### Key Excel Functions Used
- `XLOOKUP` - Dynamic data retrieval
- `SUMIFS/AVERAGEIFS` - Conditional aggregations
- `Data Model` - Relationships between tables
- `What-If Analysis` - Goal seek and scenarios

---

## 🔍 Key Insights

> *To be populated after analysis completion*

### Headline Findings
1. **Inflation Peak:** [Month/Year] at [X]%
2. **Most Affected Category:** [Category] with [X]% increase
3. **Regional Disparity:** London [X]% higher than [Region]
4. **Real Wage Impact:** Purchasing power down [X]% since [Year]

---

## 📚 References

- [ONS Consumer Price Indices](https://www.ons.gov.uk/economy/inflationandpriceindices)
- [Bank of England Inflation Target](https://www.bankofengland.co.uk/monetary-policy)
- [ONS Regional Accounts](https://www.ons.gov.uk/economy/regionalaccounts)

---

## 👤 Author

**Mounish Mesa**
- Portfolio: [mounishmesa.github.io](https://mounishmesa.github.io)
- LinkedIn: [linkedin.com/in/mounish-jm](https://linkedin.com/in/mounish-jm)
- Email: mounicar9496@gmail.com

---

## 📄 License

This project uses publicly available data under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

---

*Last Updated: December 2024*
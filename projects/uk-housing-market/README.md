# 🏠 UK Housing Market Analysis

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python)](https://python.org)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?style=flat&logo=powerbi)](https://powerbi.microsoft.com)
[![Status](https://img.shields.io/badge/Status-In%20Progress-orange?style=flat)]()

## 📋 Overview

Comprehensive analysis of the UK housing market using HM Land Registry Price Paid Data, focusing on London borough trends, affordability metrics, and price prediction modelling.

![Dashboard Preview](./assets/dashboard-preview.png)

---

## 🎯 Objectives

1. **Analyse price trends** across London boroughs over the past 10 years
2. **Calculate affordability indices** comparing prices to average earnings
3. **Build predictive models** for property price forecasting
4. **Create interactive dashboards** for stakeholder exploration

---

## 📊 Data Sources

| Source | Description | Update Frequency |
|--------|-------------|------------------|
| [HM Land Registry](https://www.gov.uk/government/collections/price-paid-data) | Property transaction records | Monthly |
| [ONS House Price Index](https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/housepriceindex/latest) | Official price indices | Monthly |
| [ONS Earnings Data](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours) | Average weekly earnings | Quarterly |

---

## 🛠️ Tech Stack

- **Data Processing:** Python (Pandas, NumPy)
- **Database:** SQL Server / SQLite
- **Visualisation:** Power BI, Matplotlib, Plotly
- **Machine Learning:** Scikit-learn
- **Version Control:** Git

---

## 📁 Project Structure

```
uk-housing-market/
├── README.md
├── data/
│   ├── raw/                    # Original downloaded data
│   ├── processed/              # Cleaned and transformed data
│   └── external/               # Additional reference data
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_modelling.ipynb
├── sql/
│   ├── create_tables.sql
│   ├── data_extraction.sql
│   └── aggregations.sql
├── src/
│   ├── data_processing.py
│   ├── visualisation.py
│   └── modelling.py
├── dashboards/
│   └── housing_analysis.pbix
├── reports/
│   └── findings_summary.pdf
└── requirements.txt
```

---

## 🔍 Key Findings

### Price Trends by Borough

| Borough | Avg Price (2024) | 5-Year Change | Trend |
|---------|------------------|---------------|-------|
| Kensington & Chelsea | £1.2M | +15% | 📈 |
| Westminster | £980K | +12% | 📈 |
| Camden | £850K | +18% | 📈 |
| Tower Hamlets | £520K | +22% | 📈 |
| Barking & Dagenham | £320K | +28% | 📈 |

*Note: Figures are illustrative - actual analysis in progress*

### Affordability Index

The affordability ratio (house price to earnings) has increased from 8.5x in 2014 to 12.3x in 2024, indicating declining affordability across London.

---

## 📈 Visualisations

### 1. Price Distribution Heatmap
Interactive map showing average property prices by postcode district.

### 2. Time Series Analysis
10-year price trends with seasonal decomposition and moving averages.

### 3. Predictive Model Performance
Comparison of Linear Regression, Random Forest, and XGBoost models.

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.9+
SQL Server or SQLite
Power BI Desktop
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/mounishmesa/mounishmesa.github.io.git
cd mounishmesa.github.io/projects/uk-housing-market
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download the data
```bash
# Download HM Land Registry data from:
# https://www.gov.uk/government/collections/price-paid-data
```

---

## 📓 Notebooks

| Notebook | Description |
|----------|-------------|
| `01_data_exploration.ipynb` | Initial data profiling and quality assessment |
| `02_data_cleaning.ipynb` | Data cleaning, handling missing values, outliers |
| `03_analysis.ipynb` | Statistical analysis and visualisations |
| `04_modelling.ipynb` | Price prediction models and evaluation |

---

## 🔗 SQL Queries

Key queries used in this analysis:

**Average Price by Borough:**
```sql
SELECT 
    borough,
    YEAR(transaction_date) AS year,
    AVG(price) AS avg_price,
    COUNT(*) AS num_transactions
FROM property_transactions
WHERE transaction_date >= '2014-01-01'
GROUP BY borough, YEAR(transaction_date)
ORDER BY borough, year;
```

**Year-over-Year Change:**
```sql
WITH yearly_prices AS (
    SELECT 
        borough,
        YEAR(transaction_date) AS year,
        AVG(price) AS avg_price
    FROM property_transactions
    GROUP BY borough, YEAR(transaction_date)
)
SELECT 
    curr.borough,
    curr.year,
    curr.avg_price,
    ROUND((curr.avg_price - prev.avg_price) / prev.avg_price * 100, 2) AS yoy_change
FROM yearly_prices curr
LEFT JOIN yearly_prices prev 
    ON curr.borough = prev.borough 
    AND curr.year = prev.year + 1;
```

---

## 📊 Power BI Dashboard

The interactive dashboard includes:

- **Overview Page:** Key metrics, trends, and filters
- **Borough Analysis:** Deep dive by London borough
- **Property Types:** Comparison across detached, semi, terraced, flats
- **Predictions:** Model outputs and confidence intervals

[View Dashboard](./dashboards/housing_analysis.pbix) | [Screenshots](./assets/)

---

## 🎯 Future Enhancements

- [ ] Add rental market data comparison
- [ ] Include mortgage rate impact analysis
- [ ] Implement Streamlit web app
- [ ] Add postcode-level granularity
- [ ] Integrate with live data feeds

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

---

## 🤝 Acknowledgements

- HM Land Registry for open data access
- Office for National Statistics (ONS)
- Bank of England for economic indicators

---

## 📫 Contact

**Mounish Mesa**
- Email: mounicar9496@gmail.com
- LinkedIn: [linkedin.com/in/mounish-jm](https://www.linkedin.com/in/mounish-jm/)

---

*Last Updated: December 2024*

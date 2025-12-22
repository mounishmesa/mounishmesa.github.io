# FTSE 100/250 Stock Market Analysis

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An interactive stock market analysis tool that tracks FTSE 100 and FTSE 250 companies, analyzes sector performance, measures volatility, and correlates stock movements with Bank of England interest rate decisions.

## 🎯 Project Objectives

- Track and analyze FTSE 100/250 stock performance
- Calculate key financial metrics (returns, volatility, beta)
- Identify sector rotation and performance patterns
- Analyze correlation between stock prices and BOE interest rates
- Provide interactive visualizations for investment insights

## 📊 Live Demo

🔗 **[View Interactive Dashboard](https://your-streamlit-app-url.streamlit.app)**

## 🖼️ Screenshots

### Dashboard Overview
![Dashboard](outputs/charts/dashboard_preview.png)

### Sector Performance
![Sectors](outputs/charts/sector_performance.png)

### BOE Rate Correlation
![Correlation](outputs/charts/boe_correlation.png)

## 📁 Project Structure
```
ftse-stock-analysis/
├── app.py                    # Streamlit dashboard
├── requirements.txt          # Dependencies
├── data/
│   ├── raw/                  # Original data files
│   ├── processed/            # Cleaned data
│   └── stock_market.db       # SQLite database
├── src/                      # Python scripts
├── sql/                      # SQL queries
├── outputs/                  # Charts and reports
└── notebooks/                # Jupyter notebooks
```

## 🛠️ Technologies Used

| Category | Tools |
|----------|-------|
| **Language** | Python 3.9+ |
| **Data Collection** | yfinance, requests, BeautifulSoup |
| **Data Processing** | Pandas, NumPy |
| **Database** | SQLite |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Dashboard** | Streamlit |
| **BI Tool** | Power BI |

## 📈 Key Features

### 1. Real-Time Stock Data
- Daily OHLCV data for 350+ UK stocks
- Automatic data refresh capability
- 2-year historical data coverage

### 2. Performance Metrics
- Daily and cumulative returns
- Year-to-date (YTD) performance
- 52-week high/low tracking
- Relative strength analysis

### 3. Volatility Analysis
- 30-day rolling volatility
- 90-day rolling volatility
- Beta coefficient vs FTSE 100
- Risk-adjusted returns (Sharpe ratio)

### 4. Sector Analysis
- 11 GICS sector classifications
- Sector rotation identification
- Market cap weighted performance
- Sector correlation matrix

### 5. BOE Rate Correlation
- Interest rate impact analysis
- Stock performance around rate decisions
- Sector sensitivity to monetary policy
- Lead/lag correlation studies

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mounishmesa/mounishmesa.github.io.git
cd projects/ftse-stock-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run data pipeline**
```bash
python src/01_fetch_constituents.py
python src/02_fetch_stock_data.py
python src/03_fetch_boe_rates.py
python src/04_data_cleaning.py
python src/05_calculate_metrics.py
```

5. **Launch dashboard**
```bash
streamlit run app.py
```

## 📊 Data Sources

| Source | Description | Update Frequency |
|--------|-------------|------------------|
| [Yahoo Finance](https://finance.yahoo.com) | Stock prices, volumes | Daily |
| [Bank of England](https://www.bankofengland.co.uk) | Base interest rates | As announced |
| [Wikipedia](https://en.wikipedia.org/wiki/FTSE_100_Index) | Index constituents | Quarterly |

## 🔍 Key Findings

### Top Performing Sectors (YTD)
1. **Energy** - Benefiting from oil price recovery
2. **Financials** - Rising rates improving margins
3. **Healthcare** - Defensive positioning

### Volatility Insights
- Average 30-day volatility: 18.5%
- Most volatile sector: Technology (24.2%)
- Least volatile sector: Utilities (12.1%)

### BOE Rate Correlation
- Financials show +0.72 correlation with rate increases
- Real Estate shows -0.65 correlation
- Rate announcements cause 2.3x normal daily volatility

## 📋 SQL Analysis Examples
```sql
-- Top 10 YTD performers
SELECT ticker, company_name, 
       ROUND(ytd_return, 2) as ytd_pct
FROM stocks 
ORDER BY ytd_return DESC 
LIMIT 10;

-- Sector performance summary
SELECT sector, 
       ROUND(AVG(ytd_return), 2) as avg_return,
       ROUND(AVG(volatility_30d), 2) as avg_vol
FROM stocks 
GROUP BY sector 
ORDER BY avg_return DESC;
```

## 📈 Power BI Dashboard

A complementary Power BI dashboard is available for enterprise users:
- File: `FTSE_Analysis_Dashboard.pbix`
- Features: Drill-through analysis, custom date ranges, export capabilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Mounish Mesa**
- LinkedIn: [linkedin.com/in/mounish-jm](https://linkedin.com/in/mounish-jm)
- GitHub: [github.com/mounishmesa](https://github.com/mounishmesa)
- Portfolio: [mounishmesa.github.io](https://mounishmesa.github.io)

## 🙏 Acknowledgments

- Yahoo Finance for providing free stock data API
- Bank of England for publicly available interest rate data
- FTSE Russell for index methodology documentation

---

*Last Updated: December 2024*
```

---

## ⏱️ Timeline

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Set up project structure, fetch FTSE constituents | `ftse100_constituents.csv` |
| 2 | Download stock data via yfinance | `stock_prices.csv` |
| 3 | Fetch BOE rates, clean all data | `stock_market.db` |
| 4 | Calculate metrics (returns, volatility) | `volatility_metrics.csv` |
| 5 | Correlation analysis, sector breakdown | Analysis outputs |
| 6 | Create static visualizations | PNG charts |
| 7 | Build Streamlit dashboard | `app.py` |
| 8 | Deploy, write README, update portfolio | Live demo |

---

## ✅ Checklist Before Starting

- [ ] Create project folder structure
- [ ] Set up virtual environment
- [ ] Install required packages (`pip install -r requirements.txt`)
- [ ] Verify yfinance works with test ticker
- [ ] Download BOE rate data manually (backup)
- [ ] Prepare FTSE 100/250 ticker list

---

## 📦 requirements.txt
```
yfinance==0.2.33
pandas==2.1.3
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0
streamlit==1.28.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
openpyxl==3.1.2
scipy==1.11.4

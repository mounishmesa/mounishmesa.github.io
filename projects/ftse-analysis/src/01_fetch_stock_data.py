"""
FTSE 100 Stock Data Fetcher
Fetches historical stock data for top FTSE 100 companies using Yahoo Finance
Author: Mounish Mesa
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Create data directory if it doesn't exist
os.makedirs('../data', exist_ok=True)

# Top 30 FTSE 100 companies by market cap (Yahoo Finance tickers)
FTSE_100_TICKERS = {
    # Energy
    'SHEL.L': {'name': 'Shell', 'sector': 'Energy'},
    'BP.L': {'name': 'BP', 'sector': 'Energy'},
    
    # Financials
    'HSBA.L': {'name': 'HSBC', 'sector': 'Financials'},
    'LLOY.L': {'name': 'Lloyds', 'sector': 'Financials'},
    'BARC.L': {'name': 'Barclays', 'sector': 'Financials'},
    'NWG.L': {'name': 'NatWest', 'sector': 'Financials'},
    'STAN.L': {'name': 'Standard Chartered', 'sector': 'Financials'},
    'LSEG.L': {'name': 'London Stock Exchange', 'sector': 'Financials'},
    
    # Consumer Goods
    'ULVR.L': {'name': 'Unilever', 'sector': 'Consumer Goods'},
    'DGE.L': {'name': 'Diageo', 'sector': 'Consumer Goods'},
    'RKT.L': {'name': 'Reckitt', 'sector': 'Consumer Goods'},
    'BATS.L': {'name': 'British American Tobacco', 'sector': 'Consumer Goods'},
    
    # Healthcare
    'AZN.L': {'name': 'AstraZeneca', 'sector': 'Healthcare'},
    'GSK.L': {'name': 'GSK', 'sector': 'Healthcare'},
    
    # Mining & Materials
    'RIO.L': {'name': 'Rio Tinto', 'sector': 'Mining'},
    'AAL.L': {'name': 'Anglo American', 'sector': 'Mining'},
    'GLEN.L': {'name': 'Glencore', 'sector': 'Mining'},
    
    # Telecom & Tech
    'VOD.L': {'name': 'Vodafone', 'sector': 'Telecom'},
    'BT-A.L': {'name': 'BT Group', 'sector': 'Telecom'},
    
    # Industrials
    'BA.L': {'name': 'BAE Systems', 'sector': 'Industrials'},
    'RR.L': {'name': 'Rolls-Royce', 'sector': 'Industrials'},
    'REL.L': {'name': 'RELX', 'sector': 'Industrials'},
    
    # Retail & Consumer Services
    'TSCO.L': {'name': 'Tesco', 'sector': 'Retail'},
    'SBRY.L': {'name': 'Sainsbury', 'sector': 'Retail'},
    'JD.L': {'name': 'JD Sports', 'sector': 'Retail'},
    
    # Utilities
    'NG.L': {'name': 'National Grid', 'sector': 'Utilities'},
    'SSE.L': {'name': 'SSE', 'sector': 'Utilities'},
    
    # Real Estate
    'LAND.L': {'name': 'Land Securities', 'sector': 'Real Estate'},
    'BLND.L': {'name': 'British Land', 'sector': 'Real Estate'},
    
    # Other
    'CPG.L': {'name': 'Compass Group', 'sector': 'Services'},
}

def fetch_stock_data(tickers_dict, period='2y'):
    """
    Fetch historical stock data for given tickers
    
    Args:
        tickers_dict: Dictionary with ticker symbols and metadata
        period: Time period (1y, 2y, 5y, max)
    
    Returns:
        DataFrame with all stock data
    """
    all_data = []
    
    print(f"Fetching data for {len(tickers_dict)} stocks...")
    print("-" * 50)
    
    for ticker, info in tickers_dict.items():
        try:
            print(f"Fetching {info['name']} ({ticker})...", end=" ")
            
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                print("No data found")
                continue
            
            # Add metadata
            hist['Ticker'] = ticker
            hist['Company'] = info['name']
            hist['Sector'] = info['sector']
            hist = hist.reset_index()
            
            all_data.append(hist)
            print(f"✓ {len(hist)} records")
            
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Combine all data
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        print("-" * 50)
        print(f"Total records fetched: {len(df):,}")
        return df
    else:
        return pd.DataFrame()

def fetch_ftse_index(period='2y'):
    """Fetch FTSE 100 index data for benchmark comparison"""
    print("\nFetching FTSE 100 Index (^FTSE)...")
    
    ftse = yf.Ticker("^FTSE")
    hist = ftse.history(period=period)
    hist = hist.reset_index()
    hist['Ticker'] = '^FTSE'
    hist['Company'] = 'FTSE 100 Index'
    hist['Sector'] = 'Index'
    
    print(f"✓ {len(hist)} records")
    return hist

def calculate_metrics(df):
    """Calculate additional metrics for analysis"""
    
    # Daily returns
    df['Daily_Return'] = df.groupby('Ticker')['Close'].pct_change() * 100
    
    # Rolling volatility (20-day)
    df['Volatility_20D'] = df.groupby('Ticker')['Daily_Return'].transform(
        lambda x: x.rolling(window=20).std()
    )
    
    # Rolling average (50-day)
    df['MA_50'] = df.groupby('Ticker')['Close'].transform(
        lambda x: x.rolling(window=50).mean()
    )
    
    # Rolling average (200-day)
    df['MA_200'] = df.groupby('Ticker')['Close'].transform(
        lambda x: x.rolling(window=200).mean()
    )
    
    # Price relative to 50-day MA
    df['Price_vs_MA50'] = ((df['Close'] / df['MA_50']) - 1) * 100
    
    return df

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("FTSE 100 STOCK DATA FETCHER")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Fetch individual stocks
    stocks_df = fetch_stock_data(FTSE_100_TICKERS, period='2y')
    
    # Fetch FTSE 100 index
    index_df = fetch_ftse_index(period='2y')
    
    # Combine stocks and index
    combined_df = pd.concat([stocks_df, index_df], ignore_index=True)
    
    # Calculate metrics
    print("\nCalculating metrics...")
    combined_df = calculate_metrics(combined_df)
    
    # Save raw data
    raw_path = '../data/ftse_stock_data_raw.csv'
    combined_df.to_csv(raw_path, index=False)
    print(f"\n✓ Raw data saved to: {raw_path}")
    
    # Create summary statistics
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"Total Records: {len(combined_df):,}")
    print(f"Date Range: {combined_df['Date'].min().strftime('%Y-%m-%d')} to {combined_df['Date'].max().strftime('%Y-%m-%d')}")
    print(f"Companies: {combined_df['Company'].nunique()}")
    print(f"Sectors: {combined_df['Sector'].nunique()}")
    
    # Sector breakdown
    print("\nRecords by Sector:")
    sector_counts = combined_df.groupby('Sector')['Ticker'].nunique()
    for sector, count in sector_counts.items():
        print(f"  {sector}: {count} companies")
    
    print("\n✓ Data fetching complete!")
    
    return combined_df

if __name__ == "__main__":
    df = main()
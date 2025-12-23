"""
FTSE 100 Stock Analysis
Analyzes stock performance, sector trends, and generates visualizations
Author: Mounish Mesa
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Create outputs directory
os.makedirs('../outputs', exist_ok=True)

def load_data():
    """Load the fetched stock data"""
    df = pd.read_csv('../data/ftse_stock_data_raw.csv')
    # Fix timezone issue by parsing with UTC then removing timezone
    df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
    print(f"Loaded {len(df):,} records")
    print(f"Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    return df

def calculate_performance(df):
    """Calculate performance metrics for each stock"""
    
    # Get latest and earliest prices for each stock
    performance = []
    
    for ticker in df['Ticker'].unique():
        stock_data = df[df['Ticker'] == ticker].sort_values('Date')
        
        if len(stock_data) < 50:  # Skip if insufficient data
            continue
        
        # Get prices at different points
        latest = stock_data.iloc[-1]
        earliest = stock_data.iloc[0]
        
        # 1 month ago (approx 21 trading days)
        one_month = stock_data.iloc[-22] if len(stock_data) > 22 else earliest
        
        # 3 months ago (approx 63 trading days)
        three_month = stock_data.iloc[-64] if len(stock_data) > 64 else earliest
        
        # 6 months ago (approx 126 trading days)
        six_month = stock_data.iloc[-127] if len(stock_data) > 127 else earliest
        
        # 1 year ago (approx 252 trading days)
        one_year = stock_data.iloc[-253] if len(stock_data) > 253 else earliest
        
        # Calculate returns
        perf = {
            'Ticker': ticker,
            'Company': latest['Company'],
            'Sector': latest['Sector'],
            'Current_Price': latest['Close'],
            'Return_1M': ((latest['Close'] / one_month['Close']) - 1) * 100,
            'Return_3M': ((latest['Close'] / three_month['Close']) - 1) * 100,
            'Return_6M': ((latest['Close'] / six_month['Close']) - 1) * 100,
            'Return_1Y': ((latest['Close'] / one_year['Close']) - 1) * 100,
            'Return_Total': ((latest['Close'] / earliest['Close']) - 1) * 100,
            'Volatility': stock_data['Daily_Return'].std(),
            'Avg_Volume': stock_data['Volume'].mean(),
            'Max_Price': stock_data['Close'].max(),
            'Min_Price': stock_data['Close'].min(),
            'Price_Range_Pct': ((stock_data['Close'].max() / stock_data['Close'].min()) - 1) * 100
        }
        
        performance.append(perf)
    
    perf_df = pd.DataFrame(performance)
    return perf_df

def plot_sector_performance(perf_df):
    """Plot sector performance comparison"""
    
    # Exclude index from sector analysis
    sector_data = perf_df[perf_df['Sector'] != 'Index']
    
    # Calculate sector averages
    sector_perf = sector_data.groupby('Sector').agg({
        'Return_1M': 'mean',
        'Return_3M': 'mean',
        'Return_6M': 'mean',
        'Return_1Y': 'mean',
        'Volatility': 'mean'
    }).round(2)
    
    sector_perf = sector_perf.sort_values('Return_1Y', ascending=True)
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Sector returns by period
    ax1 = axes[0]
    x = np.arange(len(sector_perf))
    width = 0.2
    
    bars1 = ax1.barh(x - width*1.5, sector_perf['Return_1M'], width, label='1 Month', color='#3498db')
    bars2 = ax1.barh(x - width*0.5, sector_perf['Return_3M'], width, label='3 Month', color='#2ecc71')
    bars3 = ax1.barh(x + width*0.5, sector_perf['Return_6M'], width, label='6 Month', color='#f39c12')
    bars4 = ax1.barh(x + width*1.5, sector_perf['Return_1Y'], width, label='1 Year', color='#9b59b6')
    
    ax1.set_yticks(x)
    ax1.set_yticklabels(sector_perf.index)
    ax1.set_xlabel('Return (%)')
    ax1.set_title('FTSE 100 Sector Performance by Period', fontsize=12, fontweight='bold')
    ax1.legend(loc='lower right')
    ax1.axvline(x=0, color='black', linewidth=0.5)
    
    # Plot 2: Risk vs Return (1Y)
    ax2 = axes[1]
    colors = plt.cm.Set2(np.linspace(0, 1, len(sector_perf)))
    
    for i, (sector, row) in enumerate(sector_perf.iterrows()):
        ax2.scatter(row['Volatility'], row['Return_1Y'], s=150, c=[colors[i]], 
                   label=sector, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Volatility (Daily Std Dev)')
    ax2.set_ylabel('1-Year Return (%)')
    ax2.set_title('Risk vs Return by Sector', fontsize=12, fontweight='bold')
    ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
    ax2.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig('../outputs/01_sector_performance.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 01_sector_performance.png")
    
    return sector_perf

def plot_top_performers(perf_df):
    """Plot top and bottom performing stocks"""
    
    # Exclude index
    stocks = perf_df[perf_df['Sector'] != 'Index'].copy()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Top 10 performers (1Y)
    ax1 = axes[0, 0]
    top10 = stocks.nlargest(10, 'Return_1Y')
    colors = ['#27ae60' if x > 0 else '#e74c3c' for x in top10['Return_1Y']]
    bars = ax1.barh(top10['Company'], top10['Return_1Y'], color=colors)
    ax1.set_xlabel('1-Year Return (%)')
    ax1.set_title('Top 10 Performers (1 Year)', fontsize=11, fontweight='bold')
    ax1.axvline(x=0, color='black', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, top10['Return_1Y']):
        ax1.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
                va='center', fontsize=9)
    
    # Bottom 10 performers (1Y)
    ax2 = axes[0, 1]
    bottom10 = stocks.nsmallest(10, 'Return_1Y')
    colors = ['#27ae60' if x > 0 else '#e74c3c' for x in bottom10['Return_1Y']]
    bars = ax2.barh(bottom10['Company'], bottom10['Return_1Y'], color=colors)
    ax2.set_xlabel('1-Year Return (%)')
    ax2.set_title('Bottom 10 Performers (1 Year)', fontsize=11, fontweight='bold')
    ax2.axvline(x=0, color='black', linewidth=0.5)
    
    for bar, val in zip(bars, bottom10['Return_1Y']):
        ax2.text(val - 3, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
                va='center', fontsize=9)
    
    # Most volatile stocks
    ax3 = axes[1, 0]
    volatile = stocks.nlargest(10, 'Volatility')
    ax3.barh(volatile['Company'], volatile['Volatility'], color='#e67e22')
    ax3.set_xlabel('Volatility (Daily Std Dev)')
    ax3.set_title('Most Volatile Stocks', fontsize=11, fontweight='bold')
    
    # Least volatile stocks
    ax4 = axes[1, 1]
    stable = stocks.nsmallest(10, 'Volatility')
    ax4.barh(stable['Company'], stable['Volatility'], color='#3498db')
    ax4.set_xlabel('Volatility (Daily Std Dev)')
    ax4.set_title('Least Volatile Stocks', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../outputs/02_top_performers.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 02_top_performers.png")

def plot_price_trends(df):
    """Plot price trends for major stocks vs FTSE index"""
    
    # Select major stocks (one from each major sector)
    major_tickers = ['SHEL.L', 'HSBA.L', 'AZN.L', 'RIO.L', 'TSCO.L', '^FTSE']
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()
    
    for i, ticker in enumerate(major_tickers):
        ax = axes[i]
        stock_data = df[df['Ticker'] == ticker].sort_values('Date')
        
        if stock_data.empty:
            continue
        
        # Normalize prices to 100 at start
        first_price = stock_data['Close'].iloc[0]
        stock_data['Normalized'] = (stock_data['Close'] / first_price) * 100
        
        # Plot price
        ax.plot(stock_data['Date'], stock_data['Normalized'], 
               linewidth=1.5, color='#2c3e50')
        
        # Plot 50-day MA
        ax.plot(stock_data['Date'], (stock_data['MA_50'] / first_price) * 100, 
               linewidth=1, color='#e74c3c', linestyle='--', alpha=0.7, label='50-day MA')
        
        # Fill between current and starting price
        ax.fill_between(stock_data['Date'], 100, stock_data['Normalized'],
                       where=(stock_data['Normalized'] >= 100), 
                       color='#27ae60', alpha=0.3)
        ax.fill_between(stock_data['Date'], 100, stock_data['Normalized'],
                       where=(stock_data['Normalized'] < 100), 
                       color='#e74c3c', alpha=0.3)
        
        ax.axhline(y=100, color='gray', linestyle='-', linewidth=0.5)
        
        company = stock_data['Company'].iloc[0]
        current_val = stock_data['Normalized'].iloc[-1]
        change = current_val - 100
        
        ax.set_title(f"{company}\n({change:+.1f}% total)", fontsize=10, fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        if i == 0:
            ax.legend(loc='upper left', fontsize=8)
    
    plt.suptitle('Price Performance (Normalized to 100)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('../outputs/03_price_trends.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 03_price_trends.png")

def plot_correlation_matrix(df):
    """Plot correlation matrix between major stocks"""
    
    # Select stocks for correlation
    tickers = ['SHEL.L', 'BP.L', 'HSBA.L', 'LLOY.L', 'AZN.L', 'GSK.L', 
               'RIO.L', 'GLEN.L', 'TSCO.L', 'NG.L']
    
    # Pivot to get daily returns for each stock
    pivot_df = df[df['Ticker'].isin(tickers)].pivot_table(
        index='Date', 
        columns='Company', 
        values='Daily_Return'
    )
    
    # Calculate correlation
    corr_matrix = pivot_df.corr()
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                cmap='RdYlGn', center=0, 
                square=True, linewidths=0.5,
                annot_kws={'size': 9},
                cbar_kws={'shrink': 0.8},
                ax=ax)
    
    ax.set_title('Stock Return Correlations\n(Daily Returns)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../outputs/04_correlation_matrix.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 04_correlation_matrix.png")

def plot_volatility_over_time(df):
    """Plot rolling volatility over time"""
    
    # Get FTSE index volatility
    ftse = df[df['Ticker'] == '^FTSE'].sort_values('Date').copy()
    
    # Calculate different rolling windows
    ftse['Vol_20D'] = ftse['Daily_Return'].rolling(window=20).std()
    ftse['Vol_60D'] = ftse['Daily_Return'].rolling(window=60).std()
    
    fig, ax = plt.subplots(figsize=(14, 5))
    
    ax.plot(ftse['Date'], ftse['Vol_20D'], label='20-Day Volatility', 
           color='#e74c3c', linewidth=1.5)
    ax.plot(ftse['Date'], ftse['Vol_60D'], label='60-Day Volatility', 
           color='#3498db', linewidth=1.5)
    
    # Add average line
    avg_vol = ftse['Vol_20D'].mean()
    ax.axhline(y=avg_vol, color='gray', linestyle='--', linewidth=1, 
              label=f'Average ({avg_vol:.2f})')
    
    ax.fill_between(ftse['Date'], ftse['Vol_20D'], alpha=0.3, color='#e74c3c')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Volatility (Std Dev of Daily Returns)')
    ax.set_title('FTSE 100 Market Volatility Over Time', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.tight_layout()
    plt.savefig('../outputs/05_volatility.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 05_volatility.png")

def plot_monthly_returns_heatmap(df):
    """Create a heatmap of monthly returns by sector"""
    
    # Exclude index
    stocks = df[df['Sector'] != 'Index'].copy()
    
    # Ensure Date is datetime
    stocks['Date'] = pd.to_datetime(stocks['Date'])
    
    # Extract year-month as string (avoids Period issues)
    stocks['YearMonth'] = stocks['Date'].dt.strftime('%Y-%m')
    
    # Calculate monthly returns by sector
    monthly_data = []
    
    for (ym, sector), group in stocks.groupby(['YearMonth', 'Sector']):
        group = group.sort_values('Date')
        if len(group) > 1:
            first_price = group['Close'].iloc[0]
            last_price = group['Close'].iloc[-1]
            ret = ((last_price / first_price) - 1) * 100
            monthly_data.append({
                'YearMonth': ym,
                'Sector': sector,
                'Return': ret
            })
    
    monthly_returns = pd.DataFrame(monthly_data)
    
    # Pivot for heatmap
    pivot = monthly_returns.pivot(index='Sector', columns='YearMonth', values='Return')
    
    # Keep last 12 months
    pivot = pivot.iloc[:, -12:]
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                linewidths=0.5, annot_kws={'size': 8}, ax=ax,
                cbar_kws={'label': 'Return (%)'})
    
    ax.set_title('Monthly Returns by Sector (Last 12 Months)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Sector')
    
    # Rotate x labels
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('../outputs/06_monthly_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Saved: 06_monthly_heatmap.png")

def generate_summary_report(perf_df, sector_perf):
    """Generate a text summary report"""
    
    stocks = perf_df[perf_df['Sector'] != 'Index']
    ftse = perf_df[perf_df['Sector'] == 'Index'].iloc[0]
    
    report = []
    report.append("=" * 70)
    report.append("FTSE 100 STOCK ANALYSIS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 70)
    
    report.append("\n" + "-" * 70)
    report.append("MARKET OVERVIEW")
    report.append("-" * 70)
    report.append(f"FTSE 100 Index 1-Year Return: {ftse['Return_1Y']:.2f}%")
    report.append(f"FTSE 100 Index Volatility: {ftse['Volatility']:.2f}")
    report.append(f"Stocks Analyzed: {len(stocks)}")
    report.append(f"Sectors Covered: {stocks['Sector'].nunique()}")
    
    report.append("\n" + "-" * 70)
    report.append("TOP PERFORMERS (1-YEAR RETURN)")
    report.append("-" * 70)
    for _, row in stocks.nlargest(5, 'Return_1Y').iterrows():
        report.append(f"  {row['Company']:25} {row['Return_1Y']:+.2f}%  ({row['Sector']})")
    
    report.append("\n" + "-" * 70)
    report.append("BOTTOM PERFORMERS (1-YEAR RETURN)")
    report.append("-" * 70)
    for _, row in stocks.nsmallest(5, 'Return_1Y').iterrows():
        report.append(f"  {row['Company']:25} {row['Return_1Y']:+.2f}%  ({row['Sector']})")
    
    report.append("\n" + "-" * 70)
    report.append("SECTOR PERFORMANCE (1-YEAR)")
    report.append("-" * 70)
    for sector in sector_perf.sort_values('Return_1Y', ascending=False).index:
        ret = sector_perf.loc[sector, 'Return_1Y']
        vol = sector_perf.loc[sector, 'Volatility']
        report.append(f"  {sector:20} Return: {ret:+.2f}%  Volatility: {vol:.2f}")
    
    report.append("\n" + "-" * 70)
    report.append("MOST VOLATILE STOCKS")
    report.append("-" * 70)
    for _, row in stocks.nlargest(5, 'Volatility').iterrows():
        report.append(f"  {row['Company']:25} Volatility: {row['Volatility']:.2f}  ({row['Sector']})")
    
    report.append("\n" + "-" * 70)
    report.append("MOST STABLE STOCKS")
    report.append("-" * 70)
    for _, row in stocks.nsmallest(5, 'Volatility').iterrows():
        report.append(f"  {row['Company']:25} Volatility: {row['Volatility']:.2f}  ({row['Sector']})")
    
    report.append("\n" + "=" * 70)
    report.append("END OF REPORT")
    report.append("=" * 70)
    
    # Save report
    report_text = '\n'.join(report)
    with open('../outputs/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("\n" + report_text)
    print("\n[OK] Saved: analysis_report.txt")

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("FTSE 100 STOCK ANALYSIS")
    print("=" * 60)
    print()
    
    # Load data
    df = load_data()
    
    # Calculate performance metrics
    print("\nCalculating performance metrics...")
    perf_df = calculate_performance(df)
    
    # Save performance data
    perf_df.to_csv('../outputs/stock_performance.csv', index=False)
    print("[OK] Saved: stock_performance.csv")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    print("-" * 40)
    
    sector_perf = plot_sector_performance(perf_df)
    plot_top_performers(perf_df)
    plot_price_trends(df)
    plot_correlation_matrix(df)
    plot_volatility_over_time(df)
    plot_monthly_returns_heatmap(df)
    
    # Generate summary report
    print("\n" + "-" * 40)
    generate_summary_report(perf_df, sector_perf)
    
    print("\n[OK] Analysis complete!")
    
    return df, perf_df

if __name__ == "__main__":
    df, perf_df = main()
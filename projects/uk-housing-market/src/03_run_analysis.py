"""
UK Housing Market Analysis - Run Analysis Script
=================================================
Generates all visualisations and reports from the cleaned data.
Run this instead of Jupyter notebook.

Author: Mounish Mesa
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
from datetime import datetime

# Create outputs folder
os.makedirs('outputs', exist_ok=True)

print("=" * 60)
print("UK HOUSING MARKET ANALYSIS")
print("=" * 60)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------
print("\n📂 Loading data from database...")

conn = sqlite3.connect('data/housing_market.db')
df = pd.read_sql("SELECT * FROM transactions", conn)
df['date_of_transfer'] = pd.to_datetime(df['date_of_transfer'])

print(f"✓ Loaded {len(df):,} transactions")
print(f"✓ Date range: {df['date_of_transfer'].min().date()} to {df['date_of_transfer'].max().date()}")

# -----------------------------------------------------------------------------
# OVERVIEW STATISTICS
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("OVERVIEW STATISTICS")
print("=" * 60)

print(f"\nTotal Transactions: {len(df):,}")
print(f"Total Market Value: £{df['price'].sum():,.0f}")
print(f"Average Price: £{df['price'].mean():,.0f}")
print(f"Median Price: £{df['price'].median():,.0f}")
print(f"Price Range: £{df['price'].min():,.0f} - £{df['price'].max():,.0f}")
print(f"Boroughs Covered: {df['district'].nunique()}")

# -----------------------------------------------------------------------------
# CHART 1: Price Distribution
# -----------------------------------------------------------------------------
print("\n📊 Creating price distribution chart...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
df_capped = df[df['price'] <= 2000000]
axes[0].hist(df_capped['price'], bins=50, edgecolor='white', alpha=0.7, color='#2563eb')
axes[0].set_xlabel('Price (£)', fontsize=12)
axes[0].set_ylabel('Frequency', fontsize=12)
axes[0].set_title('Distribution of Property Prices (Up to £2M)', fontsize=14)
axes[0].axvline(df['price'].median(), color='red', linestyle='--', 
                label=f'Median: £{df["price"].median():,.0f}')
axes[0].axvline(df['price'].mean(), color='green', linestyle='--', 
                label=f'Mean: £{df["price"].mean():,.0f}')
axes[0].legend()
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))

# Box plot by property type
property_order = df.groupby('property_type_name')['price'].median().sort_values(ascending=False).index
df.boxplot(column='price', by='property_type_name', ax=axes[1], positions=range(len(property_order)))
axes[1].set_xlabel('Property Type', fontsize=12)
axes[1].set_ylabel('Price (£)', fontsize=12)
axes[1].set_title('Price Distribution by Property Type', fontsize=14)
axes[1].set_ylim(0, 2000000)
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000000:.1f}M'))
plt.suptitle('')

plt.tight_layout()
plt.savefig('outputs/01_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: outputs/01_price_distribution.png")

# -----------------------------------------------------------------------------
# CHART 2: Borough Average Prices
# -----------------------------------------------------------------------------
print("\n📊 Creating borough prices chart...")

borough_prices = df.groupby('district')['price'].mean().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(12, 10))
colors = plt.cm.Blues(np.linspace(0.3, 1, len(borough_prices)))
bars = ax.barh(borough_prices.index, borough_prices.values, color=colors)
ax.set_xlabel('Average Price (£)', fontsize=12)
ax.set_title('Average Property Prices by London Borough', fontsize=14, fontweight='bold')
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000000:.1f}M'))

# Add value labels
for bar, val in zip(bars, borough_prices.values):
    ax.text(val + 20000, bar.get_y() + bar.get_height()/2, 
            f'£{val/1000:.0f}k', va='center', fontsize=8)

plt.tight_layout()
plt.savefig('outputs/02_borough_prices.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: outputs/02_borough_prices.png")

# -----------------------------------------------------------------------------
# CHART 3: Price Trends Over Time
# -----------------------------------------------------------------------------
print("\n📊 Creating price trends chart...")

monthly_avg = df.groupby('year_month').agg({
    'price': ['mean', 'median', 'count']
}).reset_index()
monthly_avg.columns = ['year_month', 'mean', 'median', 'count']
monthly_avg['year_month'] = pd.to_datetime(monthly_avg['year_month'])

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# Price trends
axes[0].plot(monthly_avg['year_month'], monthly_avg['mean'], 
             label='Average Price', color='#2563eb', linewidth=2)
axes[0].plot(monthly_avg['year_month'], monthly_avg['median'], 
             label='Median Price', color='#06b6d4', linewidth=2)
axes[0].set_ylabel('Price (£)', fontsize=12)
axes[0].set_title('London Property Prices Over Time', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))
axes[0].grid(True, alpha=0.3)

# Transaction volume
axes[1].bar(monthly_avg['year_month'], monthly_avg['count'], color='#10b981', alpha=0.7)
axes[1].set_xlabel('Date', fontsize=12)
axes[1].set_ylabel('Number of Transactions', fontsize=12)
axes[1].set_title('Monthly Transaction Volume', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/03_price_trends.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: outputs/03_price_trends.png")

# -----------------------------------------------------------------------------
# CHART 4: Property Type Comparison
# -----------------------------------------------------------------------------
print("\n📊 Creating property type chart...")

property_stats = df.groupby('property_type_name').agg({
    'price': ['mean', 'median', 'count']
}).reset_index()
property_stats.columns = ['property_type', 'avg_price', 'median_price', 'count']
property_stats = property_stats.sort_values('avg_price', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Average prices
bars1 = axes[0].bar(property_stats['property_type'], property_stats['avg_price'], 
                    color=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'])
axes[0].set_ylabel('Average Price (£)', fontsize=12)
axes[0].set_title('Average Price by Property Type', fontsize=14, fontweight='bold')
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))

for bar, val in zip(bars1, property_stats['avg_price']):
    axes[0].text(bar.get_x() + bar.get_width()/2, val + 10000, 
                 f'£{val/1000:.0f}k', ha='center', fontsize=10)

# Transaction counts
bars2 = axes[1].bar(property_stats['property_type'], property_stats['count'], 
                    color=['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'])
axes[1].set_ylabel('Number of Transactions', fontsize=12)
axes[1].set_title('Transactions by Property Type', fontsize=14, fontweight='bold')

for bar, val in zip(bars2, property_stats['count']):
    axes[1].text(bar.get_x() + bar.get_width()/2, val + 1000, 
                 f'{val:,}', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/04_property_types.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: outputs/04_property_types.png")

# -----------------------------------------------------------------------------
# CHART 5: Regional Comparison
# -----------------------------------------------------------------------------
print("\n📊 Creating regional comparison chart...")

regional_stats = df.groupby('region').agg({
    'price': ['mean', 'median', 'count']
}).reset_index()
regional_stats.columns = ['region', 'avg_price', 'median_price', 'count']
regional_stats = regional_stats.dropna().sort_values('avg_price', ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#dc2626', '#f97316', '#eab308', '#22c55e', '#3b82f6']
bars = ax.bar(regional_stats['region'], regional_stats['avg_price'], color=colors)
ax.set_ylabel('Average Price (£)', fontsize=12)
ax.set_title('Average Property Prices by London Region', fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))

for bar, val in zip(bars, regional_stats['avg_price']):
    ax.text(bar.get_x() + bar.get_width()/2, val + 10000, 
            f'£{val/1000:.0f}k', ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/05_regional_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: outputs/05_regional_comparison.png")

# -----------------------------------------------------------------------------
# CHART 6: Year-over-Year Changes
# -----------------------------------------------------------------------------
print("\n📊 Creating YoY changes chart...")

yearly_borough = df.groupby(['year', 'district'])['price'].mean().unstack()
yoy_change = yearly_borough.pct_change() * 100

latest_year = df['year'].max()
if latest_year in yoy_change.index:
    latest_change = yoy_change.loc[latest_year].dropna().sort_values(ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    colors = ['#22c55e' if x >= 0 else '#ef4444' for x in latest_change.values]
    bars = ax.barh(latest_change.index, latest_change.values, color=colors)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_xlabel('Year-over-Year Change (%)', fontsize=12)
    ax.set_title(f'Property Price Changes by Borough ({latest_year-1} to {latest_year})', 
                 fontsize=14, fontweight='bold')
    
    for bar, val in zip(bars, latest_change.values):
        ax.text(val + (0.3 if val >= 0 else -0.3), bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', ha='left' if val >= 0 else 'right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('outputs/06_yoy_changes.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: outputs/06_yoy_changes.png")

# -----------------------------------------------------------------------------
# SUMMARY TABLE
# -----------------------------------------------------------------------------
print("\n📄 Creating summary tables...")

# Borough summary
borough_summary = df.groupby('district').agg({
    'price': ['mean', 'median', 'min', 'max', 'count']
}).reset_index()
borough_summary.columns = ['Borough', 'Avg Price', 'Median Price', 'Min Price', 'Max Price', 'Transactions']
borough_summary = borough_summary.sort_values('Avg Price', ascending=False)
borough_summary.to_csv('outputs/borough_summary.csv', index=False)
print("  ✓ Saved: outputs/borough_summary.csv")

# Top 10 boroughs
print("\n" + "=" * 60)
print("TOP 10 MOST EXPENSIVE BOROUGHS")
print("=" * 60)
for i, row in borough_summary.head(10).iterrows():
    print(f"  {row['Borough']}: £{row['Avg Price']:,.0f} ({row['Transactions']:,} transactions)")

# Most affordable
print("\n" + "=" * 60)
print("TOP 5 MOST AFFORDABLE BOROUGHS")
print("=" * 60)
for i, row in borough_summary.tail(5).iterrows():
    print(f"  {row['Borough']}: £{row['Avg Price']:,.0f} ({row['Transactions']:,} transactions)")

# -----------------------------------------------------------------------------
# COMPLETE
# -----------------------------------------------------------------------------
conn.close()

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
print("\n📁 Generated files in 'outputs/' folder:")
print("   • 01_price_distribution.png")
print("   • 02_borough_prices.png")
print("   • 03_price_trends.png")
print("   • 04_property_types.png")
print("   • 05_regional_comparison.png")
print("   • 06_yoy_changes.png")
print("   • borough_summary.csv")
print("\n🎯 Next steps:")
print("   1. Review the charts in the outputs folder")
print("   2. Connect Power BI to housing_market.db")
print("   3. Upload charts to your GitHub portfolio")
print("   4. Create a Streamlit dashboard (optional)")

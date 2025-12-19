"""
UK Housing Market Analysis - Exploratory Data Analysis
=======================================================
Jupyter Notebook content for housing market analysis.

To use: Copy this code into Jupyter notebook cells.

Author: Mounish Mesa
"""

# =============================================================================
# CELL 1: Setup and Imports
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '£{:,.0f}'.format(x) if abs(x) > 100 else '{:.2f}'.format(x))

print("✓ Libraries loaded successfully")


# =============================================================================
# CELL 2: Load Data from Database
# =============================================================================

# Connect to database
conn = sqlite3.connect('data/housing_market.db')

# Load main transactions
df = pd.read_sql("SELECT * FROM transactions", conn)
df['date_of_transfer'] = pd.to_datetime(df['date_of_transfer'])

# Load aggregated tables
monthly_borough = pd.read_sql("SELECT * FROM monthly_borough", conn)
yearly_borough = pd.read_sql("SELECT * FROM yearly_borough", conn)
property_summary = pd.read_sql("SELECT * FROM property_summary", conn)
regional_summary = pd.read_sql("SELECT * FROM regional_summary", conn)

print(f"✓ Loaded {len(df):,} transactions")
print(f"✓ Date range: {df['date_of_transfer'].min().date()} to {df['date_of_transfer'].max().date()}")


# =============================================================================
# CELL 3: Overview Statistics
# =============================================================================

print("=" * 60)
print("LONDON HOUSING MARKET OVERVIEW")
print("=" * 60)

overview_stats = {
    'Total Transactions': f"{len(df):,}",
    'Total Market Value': f"£{df['price'].sum():,.0f}",
    'Average Price': f"£{df['price'].mean():,.0f}",
    'Median Price': f"£{df['price'].median():,.0f}",
    'Price Range': f"£{df['price'].min():,.0f} - £{df['price'].max():,.0f}",
    'Boroughs Covered': df['district'].nunique(),
    'Unique Postcodes': df['postcode'].nunique()
}

for key, value in overview_stats.items():
    print(f"{key}: {value}")


# =============================================================================
# CELL 4: Price Distribution Analysis
# =============================================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram of prices (capped at £2M for visibility)
df_capped = df[df['price'] <= 2000000]
axes[0].hist(df_capped['price'], bins=50, edgecolor='white', alpha=0.7, color='#2563eb')
axes[0].set_xlabel('Price (£)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Property Prices (Up to £2M)')
axes[0].axvline(df['price'].median(), color='red', linestyle='--', label=f'Median: £{df["price"].median():,.0f}')
axes[0].legend()

# Box plot by property type
df.boxplot(column='price', by='property_type_name', ax=axes[1])
axes[1].set_xlabel('Property Type')
axes[1].set_ylabel('Price (£)')
axes[1].set_title('Price Distribution by Property Type')
axes[1].set_ylim(0, 2000000)
plt.suptitle('')

plt.tight_layout()
plt.savefig('outputs/price_distribution.png', dpi=300, bbox_inches='tight')
plt.show()


# =============================================================================
# CELL 5: Borough Analysis - Average Prices
# =============================================================================

# Calculate average prices by borough
borough_prices = df.groupby('district').agg({
    'price': ['mean', 'median', 'count']
}).reset_index()
borough_prices.columns = ['Borough', 'Average Price', 'Median Price', 'Transactions']
borough_prices = borough_prices.sort_values('Average Price', ascending=True)

# Create horizontal bar chart
fig = px.bar(
    borough_prices,
    y='Borough',
    x='Average Price',
    orientation='h',
    title='Average Property Prices by London Borough',
    color='Average Price',
    color_continuous_scale='Blues',
    hover_data=['Median Price', 'Transactions']
)

fig.update_layout(
    height=800,
    xaxis_title='Average Price (£)',
    yaxis_title='',
    coloraxis_showscale=False
)

fig.write_html('outputs/borough_prices_interactive.html')
fig.show()


# =============================================================================
# CELL 6: Time Series Analysis - Price Trends
# =============================================================================

# Monthly average prices
monthly_avg = df.groupby('year_month')['price'].agg(['mean', 'median', 'count']).reset_index()
monthly_avg['year_month'] = pd.to_datetime(monthly_avg['year_month'])

# Create time series plot
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Average Property Prices Over Time', 'Transaction Volume Over Time'),
    vertical_spacing=0.15
)

# Price trend
fig.add_trace(
    go.Scatter(x=monthly_avg['year_month'], y=monthly_avg['mean'], 
               mode='lines', name='Average Price', line=dict(color='#2563eb', width=2)),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=monthly_avg['year_month'], y=monthly_avg['median'], 
               mode='lines', name='Median Price', line=dict(color='#06b6d4', width=2)),
    row=1, col=1
)

# Volume trend
fig.add_trace(
    go.Bar(x=monthly_avg['year_month'], y=monthly_avg['count'], 
           name='Transactions', marker_color='#10b981'),
    row=2, col=1
)

fig.update_layout(height=600, showlegend=True, title_text='London Housing Market Trends')
fig.update_yaxes(title_text='Price (£)', row=1, col=1)
fig.update_yaxes(title_text='Number of Transactions', row=2, col=1)

fig.write_html('outputs/price_trends_interactive.html')
fig.show()


# =============================================================================
# CELL 7: Year-over-Year Price Changes
# =============================================================================

# Calculate YoY changes by borough
yearly_prices = df.groupby(['year', 'district'])['price'].mean().unstack()
yoy_change = yearly_prices.pct_change() * 100

# Get latest year's change
latest_year = df['year'].max()
latest_change = yoy_change.loc[latest_year].sort_values(ascending=False)

# Plot
fig, ax = plt.subplots(figsize=(12, 8))
colors = ['#10b981' if x >= 0 else '#ef4444' for x in latest_change.values]
bars = ax.barh(latest_change.index, latest_change.values, color=colors)
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('Year-over-Year Change (%)')
ax.set_title(f'Property Price Changes by Borough ({latest_year-1} to {latest_year})')

# Add value labels
for bar, val in zip(bars, latest_change.values):
    ax.text(val + 0.5 if val >= 0 else val - 0.5, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', ha='left' if val >= 0 else 'right', fontsize=8)

plt.tight_layout()
plt.savefig('outputs/yoy_price_changes.png', dpi=300, bbox_inches='tight')
plt.show()


# =============================================================================
# CELL 8: Property Type Analysis
# =============================================================================

# Average price by property type over time
property_trends = df.groupby(['year', 'property_type_name'])['price'].mean().unstack()

fig = px.line(
    property_trends.reset_index().melt(id_vars='year', var_name='Property Type', value_name='Average Price'),
    x='year',
    y='Average Price',
    color='Property Type',
    title='Average Prices by Property Type Over Time',
    markers=True
)

fig.update_layout(
    xaxis_title='Year',
    yaxis_title='Average Price (£)',
    legend_title='Property Type'
)

fig.write_html('outputs/property_type_trends.html')
fig.show()


# =============================================================================
# CELL 9: Regional Analysis (London Regions)
# =============================================================================

# Regional comparison
regional_stats = df.groupby('region').agg({
    'price': ['mean', 'median', 'count'],
    'district': 'nunique'
}).reset_index()
regional_stats.columns = ['Region', 'Avg Price', 'Median Price', 'Transactions', 'Boroughs']

# Create comparison chart
fig = px.bar(
    regional_stats,
    x='Region',
    y='Avg Price',
    color='Region',
    title='Average Property Prices by London Region',
    text=regional_stats['Avg Price'].apply(lambda x: f'£{x/1000:.0f}k')
)

fig.update_traces(textposition='outside')
fig.update_layout(showlegend=False, yaxis_title='Average Price (£)')

fig.write_html('outputs/regional_comparison.html')
fig.show()

print("\nRegional Summary:")
print(regional_stats.to_string(index=False))


# =============================================================================
# CELL 10: Heatmap - Borough vs Property Type
# =============================================================================

# Create pivot table
heatmap_data = df.pivot_table(
    values='price',
    index='district',
    columns='property_type_name',
    aggfunc='mean'
) / 1000  # Convert to thousands

# Sort by overall average
heatmap_data['Total'] = heatmap_data.mean(axis=1)
heatmap_data = heatmap_data.sort_values('Total', ascending=False).drop('Total', axis=1)

# Plot
fig, ax = plt.subplots(figsize=(12, 14))
sns.heatmap(
    heatmap_data,
    cmap='YlOrRd',
    annot=True,
    fmt='.0f',
    ax=ax,
    cbar_kws={'label': 'Average Price (£000s)'}
)
ax.set_title('Average Property Prices (£000s) by Borough and Property Type')
ax.set_xlabel('Property Type')
ax.set_ylabel('Borough')

plt.tight_layout()
plt.savefig('outputs/borough_property_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()


# =============================================================================
# CELL 11: Top 10 Most Expensive Postcodes
# =============================================================================

# Postcode analysis
postcode_analysis = df.groupby('postcode_district').agg({
    'price': ['mean', 'median', 'count']
}).reset_index()
postcode_analysis.columns = ['Postcode', 'Avg Price', 'Median Price', 'Transactions']

# Filter for postcodes with significant transactions
postcode_analysis = postcode_analysis[postcode_analysis['Transactions'] >= 50]
top_postcodes = postcode_analysis.nlargest(15, 'Avg Price')

fig = px.bar(
    top_postcodes,
    x='Postcode',
    y='Avg Price',
    title='Top 15 Most Expensive Postcode Districts in London',
    color='Avg Price',
    color_continuous_scale='Reds',
    text=top_postcodes['Avg Price'].apply(lambda x: f'£{x/1000000:.2f}M')
)

fig.update_traces(textposition='outside')
fig.update_layout(coloraxis_showscale=False, yaxis_title='Average Price (£)')

fig.write_html('outputs/top_postcodes.html')
fig.show()


# =============================================================================
# CELL 12: Summary Statistics Table
# =============================================================================

# Create comprehensive summary table
summary_by_borough = df.groupby('district').agg({
    'price': ['mean', 'median', 'std', 'min', 'max', 'count'],
    'property_type': lambda x: x.mode().iloc[0] if len(x) > 0 else 'N/A'
}).reset_index()

summary_by_borough.columns = ['Borough', 'Avg Price', 'Median Price', 'Std Dev', 
                               'Min Price', 'Max Price', 'Transactions', 'Most Common Type']
summary_by_borough = summary_by_borough.sort_values('Avg Price', ascending=False)

# Save to CSV
summary_by_borough.to_csv('outputs/borough_summary.csv', index=False)
print("✓ Summary saved to outputs/borough_summary.csv")

# Display
print("\nBorough Summary (sorted by average price):")
print(summary_by_borough.head(10).to_string(index=False))


# =============================================================================
# CELL 13: Save All Outputs
# =============================================================================

import os
os.makedirs('outputs', exist_ok=True)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print("\nGenerated outputs:")
print("  📊 outputs/price_distribution.png")
print("  📊 outputs/borough_prices_interactive.html")
print("  📊 outputs/price_trends_interactive.html")
print("  📊 outputs/yoy_price_changes.png")
print("  📊 outputs/property_type_trends.html")
print("  📊 outputs/regional_comparison.html")
print("  📊 outputs/borough_property_heatmap.png")
print("  📊 outputs/top_postcodes.html")
print("  📄 outputs/borough_summary.csv")

conn.close()
print("\n✓ Database connection closed")

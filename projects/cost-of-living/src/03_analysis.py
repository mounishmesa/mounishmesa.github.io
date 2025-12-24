"""
UK Cost of Living Analysis - Visualization Script
=================================================
Generates charts and analysis report from processed data.

Author: Mounish Mesa
Date: December 2024
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 60)
print("UK Cost of Living - Analysis Script")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Paths
DB_PATH = '../data/cost_of_living.db'
OUTPUT_PATH = '../outputs/charts'
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Connect to database
conn = sqlite3.connect(DB_PATH)


def load_data():
    """Load all data from database"""
    print("📊 Loading Data...")
    print("-" * 40)
    
    data = {}
    
    # Load CPI data
    data['cpi'] = pd.read_sql("SELECT * FROM cpi_data", conn)
    data['cpi']['date'] = pd.to_datetime(data['cpi']['date'])
    print(f"  ✓ CPI data: {len(data['cpi'])} records")
    
    # Load regional data
    data['regional'] = pd.read_sql("SELECT * FROM regional_prices", conn)
    print(f"  ✓ Regional data: {len(data['regional'])} records")
    
    # Load wages data
    data['wages'] = pd.read_sql("SELECT * FROM wages", conn)
    data['wages']['date'] = pd.to_datetime(data['wages']['date'])
    print(f"  ✓ Wages data: {len(data['wages'])} records")
    
    # Load basket data
    data['basket'] = pd.read_sql("SELECT * FROM basket_of_goods", conn)
    print(f"  ✓ Basket data: {len(data['basket'])} records")
    
    return data


def chart_01_inflation_timeline(data):
    """Chart 1: UK Inflation Timeline (1989-2024)"""
    
    print("\n📈 Creating Chart 1: Inflation Timeline...")
    
    df = data['cpi'].copy()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot CPI
    ax.plot(df['date'], df['cpi_annual'], color='#2563eb', linewidth=1.5, label='CPI Annual Rate')
    
    # Plot CPIH if available
    if 'cpih_annual' in df.columns:
        cpih = df.dropna(subset=['cpih_annual'])
        ax.plot(cpih['date'], cpih['cpih_annual'], color='#7c3aed', linewidth=1.5, 
                alpha=0.7, label='CPIH Annual Rate')
    
    # BOE 2% target line
    ax.axhline(y=2, color='#dc2626', linestyle='--', linewidth=1.5, label='BOE 2% Target')
    
    # Highlight key periods
    # 2022 crisis
    ax.axvspan(pd.Timestamp('2022-01-01'), pd.Timestamp('2023-06-01'), 
               alpha=0.1, color='red', label='2022-23 Crisis')
    
    # COVID
    ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-03-01'), 
               alpha=0.1, color='gray', label='COVID Period')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Annual Inflation Rate (%)', fontsize=12)
    ax.set_title('UK Inflation Timeline (1989-2024)\nCPI vs Bank of England 2% Target', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.set_ylim(-2, 12)
    
    # Add annotations
    peak = df.loc[df['cpi_annual'].idxmax()]
    ax.annotate(f'Peak: {peak["cpi_annual"]:.1f}%\n({peak["date"].strftime("%b %Y")})',
                xy=(peak['date'], peak['cpi_annual']),
                xytext=(peak['date'] - pd.Timedelta(days=365), peak['cpi_annual'] + 1),
                arrowprops=dict(arrowstyle='->', color='gray'),
                fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/01_inflation_timeline.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 01_inflation_timeline.png")


def chart_02_recent_trend(data):
    """Chart 2: Recent Inflation Trend (2020-2024)"""
    
    print("📈 Creating Chart 2: Recent Trend...")
    
    df = data['cpi'][data['cpi']['year'] >= 2020].copy()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Main CPI line
    ax.plot(df['date'], df['cpi_annual'], color='#2563eb', linewidth=2.5, marker='o', 
            markersize=4, label='CPI Annual Rate')
    
    # Fill above/below target
    ax.fill_between(df['date'], 2, df['cpi_annual'], 
                    where=(df['cpi_annual'] > 2), 
                    alpha=0.3, color='#dc2626', label='Above Target')
    ax.fill_between(df['date'], 2, df['cpi_annual'], 
                    where=(df['cpi_annual'] <= 2), 
                    alpha=0.3, color='#16a34a', label='At/Below Target')
    
    # BOE target
    ax.axhline(y=2, color='#dc2626', linestyle='--', linewidth=2, label='BOE 2% Target')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Annual Inflation Rate (%)', fontsize=12)
    ax.set_title('UK Inflation: The Cost of Living Crisis & Recovery (2020-2024)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 12)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/02_recent_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 02_recent_trend.png")


def chart_03_category_comparison(data):
    """Chart 3: Inflation by Category"""
    
    print("📈 Creating Chart 3: Category Comparison...")
    
    df = data['cpi'][data['cpi']['year'] >= 2020].copy()
    
    # Check available columns
    categories = []
    cat_cols = ['food_inflation', 'housing_energy_inflation', 'cpi_annual']
    available_cols = [c for c in cat_cols if c in df.columns and df[c].notna().any()]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#f59e0b', '#ef4444', '#2563eb']
    labels = ['Food & Beverages', 'Housing & Energy', 'Overall CPI']
    
    for col, color, label in zip(available_cols, colors, labels):
        subset = df.dropna(subset=[col])
        ax.plot(subset['date'], subset[col], linewidth=2, color=color, label=label)
    
    ax.axhline(y=2, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='BOE Target')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Annual Inflation Rate (%)', fontsize=12)
    ax.set_title('UK Inflation by Category (2020-2024)\nFood & Energy vs Overall CPI', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/03_category_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 03_category_comparison.png")


def chart_04_regional_prices(data):
    """Chart 4: Regional Price Index Comparison"""
    
    print("📈 Creating Chart 4: Regional Prices...")
    
    df = data['regional']
    latest_year = df['year'].max()
    latest = df[df['year'] == latest_year].sort_values('overall_index', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#dc2626' if x > 100 else '#16a34a' for x in latest['overall_index']]
    
    bars = ax.barh(latest['region'], latest['overall_index'] - 100, color=colors, height=0.7)
    
    # Add value labels
    for bar, val in zip(bars, latest['overall_index']):
        width = bar.get_width()
        label_x = width + 0.5 if width >= 0 else width - 2
        ax.text(label_x, bar.get_y() + bar.get_height()/2, 
                f'{val:.0f}', va='center', fontsize=10, fontweight='bold')
    
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Deviation from UK Average (Index = 100)', fontsize=12)
    ax.set_title(f'Regional Price Index Comparison ({latest_year})\nUK Average = 100', 
                 fontsize=14, fontweight='bold')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#dc2626', label='Above UK Average'),
                       Patch(facecolor='#16a34a', label='Below UK Average')]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/04_regional_prices.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 04_regional_prices.png")


def chart_05_housing_costs(data):
    """Chart 5: Regional Housing Cost Index"""
    
    print("📈 Creating Chart 5: Housing Costs...")
    
    df = data['regional']
    latest_year = df['year'].max()
    latest = df[df['year'] == latest_year].sort_values('housing_index', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(latest)))
    
    bars = ax.barh(latest['region'], latest['housing_index'], color=colors, height=0.7)
    
    # Add value labels
    for bar, val in zip(bars, latest['housing_index']):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
                f'{val:.0f}', va='center', fontsize=10)
    
    ax.axvline(x=100, color='black', linestyle='--', linewidth=1.5, label='UK Average')
    ax.set_xlabel('Housing Cost Index (UK = 100)', fontsize=12)
    ax.set_title(f'Regional Housing Cost Index ({latest_year})\nHigher = More Expensive', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/05_housing_costs.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 05_housing_costs.png")


def chart_06_wages_vs_inflation(data):
    """Chart 6: Wages vs Inflation"""
    
    print("📈 Creating Chart 6: Wages vs Inflation...")
    
    wages = data['wages'].copy()
    cpi = data['cpi'][['date', 'cpi_annual']].copy()
    
    # Merge
    merged = wages.merge(cpi, on='date', how='inner')
    
    if len(merged) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(merged['date'], merged['yoy_change'], color='#16a34a', 
                linewidth=2.5, label='Wage Growth (%)', marker='o', markersize=4)
        ax.plot(merged['date'], merged['cpi_annual'], color='#dc2626', 
                linewidth=2.5, label='Inflation (%)', marker='s', markersize=4)
        
        # Calculate real wage change
        merged['real_change'] = merged['yoy_change'] - merged['cpi_annual']
        
        ax.fill_between(merged['date'], merged['yoy_change'], merged['cpi_annual'],
                        where=(merged['yoy_change'] >= merged['cpi_annual']),
                        alpha=0.3, color='green', label='Real Wage Gain')
        ax.fill_between(merged['date'], merged['yoy_change'], merged['cpi_annual'],
                        where=(merged['yoy_change'] < merged['cpi_annual']),
                        alpha=0.3, color='red', label='Real Wage Loss')
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Percentage (%)', fontsize=12)
        ax.set_title('UK Wages vs Inflation: The Real Wage Squeeze', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_PATH}/06_wages_vs_inflation.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved 06_wages_vs_inflation.png")
    else:
        print("  ⚠️ No matching wage/inflation data")


def chart_07_inflation_heatmap(data):
    """Chart 7: Monthly Inflation Heatmap"""
    
    print("📈 Creating Chart 7: Inflation Heatmap...")
    
    df = data['cpi'][data['cpi']['year'] >= 2015].copy()
    
    # Pivot for heatmap
    pivot = df.pivot_table(values='cpi_annual', index='month', columns='year', aggfunc='mean')
    
    # Replace month numbers with names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot.index = [month_names[i-1] for i in pivot.index]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                center=2, ax=ax, linewidths=0.5,
                cbar_kws={'label': 'CPI Annual Rate (%)'})
    
    ax.set_title('UK Monthly Inflation Heatmap (2015-2024)\nRed = High Inflation, Green = Low', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Month', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}/07_inflation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved 07_inflation_heatmap.png")


def chart_08_basket_comparison(data):
    """Chart 8: Basket of Goods Price Changes"""
    
    print("📈 Creating Chart 8: Basket Comparison...")
    
    df = data['basket']
    
    # Calculate price change 2020 vs 2024
    pivot = df.pivot_table(values='average_price', index='item', columns='year')
    
    if 2020 in pivot.columns and 2024 in pivot.columns:
        pivot['pct_change'] = ((pivot[2024] - pivot[2020]) / pivot[2020] * 100).round(1)
        pivot = pivot.sort_values('pct_change', ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        colors = ['#dc2626' if x > 20 else '#f59e0b' if x > 10 else '#16a34a' 
                  for x in pivot['pct_change']]
        
        bars = ax.barh(pivot.index, pivot['pct_change'], color=colors, height=0.7)
        
        # Add value labels
        for bar, val in zip(bars, pivot['pct_change']):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
                    f'{val:.0f}%', va='center', fontsize=9)
        
        ax.axvline(x=0, color='black', linewidth=1)
        ax.set_xlabel('Price Change Since 2020 (%)', fontsize=12)
        ax.set_title('UK Cost of Living: Price Changes 2020-2024\nCommon Household Items', 
                     fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_PATH}/08_basket_comparison.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved 08_basket_comparison.png")
    else:
        print("  ⚠️ Insufficient years for comparison")


def generate_report(data):
    """Generate analysis report"""
    
    print("\n📝 Generating Analysis Report...")
    
    cpi = data['cpi']
    regional = data['regional']
    
    report = []
    report.append("=" * 60)
    report.append("UK COST OF LIVING ANALYSIS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    # Current State
    latest = cpi[cpi['date'] == cpi['date'].max()].iloc[0]
    report.append(f"\n📊 CURRENT STATE (as of {latest['date'].strftime('%B %Y')})")
    report.append("-" * 40)
    report.append(f"CPI Annual Rate: {latest['cpi_annual']:.1f}%")
    if pd.notna(latest.get('cpih_annual')):
        report.append(f"CPIH Annual Rate: {latest['cpih_annual']:.1f}%")
    report.append(f"Inflation Regime: {latest.get('inflation_regime', 'N/A')}")
    report.append(f"Distance from BOE Target: {latest['cpi_annual'] - 2:.1f}pp")
    
    # 2024 Summary
    y2024 = cpi[cpi['year'] == 2024]
    if len(y2024) > 0:
        report.append(f"\n📈 2024 YEAR-TO-DATE")
        report.append("-" * 40)
        report.append(f"Average CPI: {y2024['cpi_annual'].mean():.1f}%")
        report.append(f"Peak: {y2024['cpi_annual'].max():.1f}% ({y2024.loc[y2024['cpi_annual'].idxmax(), 'month_name']})")
        report.append(f"Low: {y2024['cpi_annual'].min():.1f}% ({y2024.loc[y2024['cpi_annual'].idxmin(), 'month_name']})")
    
    # Historical Peak
    peak_row = cpi.loc[cpi['cpi_annual'].idxmax()]
    report.append(f"\n🔺 HISTORICAL PEAK")
    report.append("-" * 40)
    report.append(f"Peak CPI: {peak_row['cpi_annual']:.1f}%")
    report.append(f"Date: {peak_row['date'].strftime('%B %Y')}")
    
    # Regional Summary
    latest_year = regional['year'].max()
    reg_latest = regional[regional['year'] == latest_year]
    most_exp = reg_latest.loc[reg_latest['overall_index'].idxmax()]
    cheapest = reg_latest.loc[reg_latest['overall_index'].idxmin()]
    
    report.append(f"\n🗺️ REGIONAL SUMMARY ({latest_year})")
    report.append("-" * 40)
    report.append(f"Most Expensive: {most_exp['region']} (Index: {most_exp['overall_index']:.0f})")
    report.append(f"Most Affordable: {cheapest['region']} (Index: {cheapest['overall_index']:.0f})")
    report.append(f"London Premium: {most_exp['overall_index'] - 100:.0f}% above UK average")
    
    # Key Insights
    report.append(f"\n💡 KEY INSIGHTS")
    report.append("-" * 40)
    report.append("• UK inflation has fallen significantly from 2022 peak (>11%) to ~3%")
    report.append("• Still above BOE 2% target but trending toward normalization")
    report.append("• Housing & Energy were primary drivers of 2022-23 crisis")
    report.append("• London remains ~15% more expensive than UK average")
    report.append("• North-South divide persists in cost of living")
    
    report.append("\n" + "=" * 60)
    report.append("END OF REPORT")
    report.append("=" * 60)
    
    # Save report
    report_text = "\n".join(report)
    with open('../outputs/reports/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("  ✓ Saved analysis_report.txt")
    print("\n" + report_text)


def main():
    """Main execution function"""
    
    # Load data
    data = load_data()
    
    # Generate charts
    print("\n🎨 Generating Visualizations...")
    print("-" * 40)
    
    chart_01_inflation_timeline(data)
    chart_02_recent_trend(data)
    chart_03_category_comparison(data)
    chart_04_regional_prices(data)
    chart_05_housing_costs(data)
    chart_06_wages_vs_inflation(data)
    chart_07_inflation_heatmap(data)
    chart_08_basket_comparison(data)
    
    # Generate report
    os.makedirs('../outputs/reports', exist_ok=True)
    generate_report(data)
    
    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nCharts saved to: {OUTPUT_PATH}/")
    for f in sorted(os.listdir(OUTPUT_PATH)):
        print(f"  📊 {f}")
    print(f"\nReport saved to: ../outputs/reports/analysis_report.txt")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Next step: Run app.py for interactive Streamlit dashboard")


if __name__ == "__main__":
    main()
    conn.close()
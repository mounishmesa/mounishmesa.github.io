"""
UK Housing Market Analysis - Data Cleaning Script
==================================================
Cleans and prepares HM Land Registry data for analysis.

Author: Mounish Mesa
"""

import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime

# Configuration
PROCESSED_DIR = "data/processed"
DATABASE_PATH = "data/housing_market.db"

# London boroughs with their regions
LONDON_REGIONS = {
    # Central London
    'CITY OF LONDON': 'Central',
    'WESTMINSTER': 'Central',
    'CAMDEN': 'Central',
    'ISLINGTON': 'Central',
    'KENSINGTON AND CHELSEA': 'Central',
    'LAMBETH': 'Central',
    'SOUTHWARK': 'Central',
    'TOWER HAMLETS': 'Central',
    
    # North London
    'BARNET': 'North',
    'ENFIELD': 'North',
    'HARINGEY': 'North',
    'WALTHAM FOREST': 'North',
    
    # South London
    'BROMLEY': 'South',
    'CROYDON': 'South',
    'LEWISHAM': 'South',
    'MERTON': 'South',
    'SUTTON': 'South',
    'GREENWICH': 'South',
    
    # East London
    'BARKING AND DAGENHAM': 'East',
    'BEXLEY': 'East',
    'HAVERING': 'East',
    'NEWHAM': 'East',
    'REDBRIDGE': 'East',
    'HACKNEY': 'East',
    
    # West London
    'BRENT': 'West',
    'EALING': 'West',
    'HAMMERSMITH AND FULHAM': 'West',
    'HARROW': 'West',
    'HILLINGDON': 'West',
    'HOUNSLOW': 'West',
    'RICHMOND UPON THAMES': 'West',
    'KINGSTON UPON THAMES': 'West',
    'WANDSWORTH': 'West'
}

# Property type mapping
PROPERTY_TYPES = {
    "D": "Detached",
    "S": "Semi-Detached",
    "T": "Terraced",
    "F": "Flat/Maisonette",
    "O": "Other"
}


def load_london_data():
    """Load all London data files."""
    print("📂 Loading London data files...")
    
    all_data = []
    
    for filename in os.listdir(PROCESSED_DIR):
        if filename.startswith("london-pp-") and filename.endswith(".csv"):
            filepath = os.path.join(PROCESSED_DIR, filename)
            print(f"  Loading: {filename}")
            df = pd.read_csv(filepath)
            all_data.append(df)
            print(f"    → {len(df):,} records")
    
    if not all_data:
        raise FileNotFoundError("No London data files found. Run 01_download_data.py first.")
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Total records loaded: {len(combined):,}")
    
    return combined


def clean_data(df):
    """Clean and transform the housing data."""
    print("\n🧹 Cleaning data...")
    
    initial_count = len(df)
    
    # 1. Remove duplicates
    df = df.drop_duplicates(subset=['transaction_id'])
    print(f"  Removed duplicates: {initial_count - len(df):,}")
    
    # 2. Convert date column
    df['date_of_transfer'] = pd.to_datetime(df['date_of_transfer'], errors='coerce')
    
    # 3. Remove records with missing essential data
    essential_cols = ['price', 'date_of_transfer', 'postcode', 'district']
    before = len(df)
    df = df.dropna(subset=essential_cols)
    print(f"  Removed missing essentials: {before - len(df):,}")
    
    # 4. Remove outliers (prices < £10,000 or > £50,000,000)
    before = len(df)
    df = df[(df['price'] >= 10000) & (df['price'] <= 50000000)]
    print(f"  Removed price outliers: {before - len(df):,}")
    
    # 5. Standardise district names
    df['district'] = df['district'].str.upper().str.strip()
    
    # 6. Add derived columns
    df['year'] = df['date_of_transfer'].dt.year
    df['month'] = df['date_of_transfer'].dt.month
    df['quarter'] = df['date_of_transfer'].dt.quarter
    df['year_month'] = df['date_of_transfer'].dt.to_period('M').astype(str)
    
    # 7. Add property type names
    df['property_type_name'] = df['property_type'].map(PROPERTY_TYPES)
    
    # 8. Add London region
    df['region'] = df['district'].map(LONDON_REGIONS)
    
    # 9. Extract postcode district (e.g., "SW1" from "SW1A 1AA")
    df['postcode_district'] = df['postcode'].str.extract(r'^([A-Z]{1,2}\d{1,2}[A-Z]?)')
    
    # 10. Add price bands
    df['price_band'] = pd.cut(
        df['price'],
        bins=[0, 250000, 500000, 750000, 1000000, 2000000, float('inf')],
        labels=['Under £250k', '£250k-£500k', '£500k-£750k', 
                '£750k-£1M', '£1M-£2M', 'Over £2M']
    )
    
    print(f"\n✓ Cleaning complete: {len(df):,} records remaining")
    
    return df


def generate_summary_statistics(df):
    """Generate summary statistics for the cleaned data."""
    print("\n📊 Generating Summary Statistics...")
    
    summary = {
        'total_transactions': len(df),
        'date_range': f"{df['date_of_transfer'].min().date()} to {df['date_of_transfer'].max().date()}",
        'avg_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'total_value': df['price'].sum(),
        'unique_postcodes': df['postcode'].nunique(),
        'boroughs_covered': df['district'].nunique()
    }
    
    print(f"\n  Total Transactions: {summary['total_transactions']:,}")
    print(f"  Date Range: {summary['date_range']}")
    print(f"  Average Price: £{summary['avg_price']:,.0f}")
    print(f"  Median Price: £{summary['median_price']:,.0f}")
    print(f"  Price Range: £{summary['min_price']:,.0f} - £{summary['max_price']:,.0f}")
    print(f"  Total Market Value: £{summary['total_value']:,.0f}")
    print(f"  Unique Postcodes: {summary['unique_postcodes']:,}")
    print(f"  Boroughs Covered: {summary['boroughs_covered']}")
    
    # By borough
    print("\n  Top 10 Boroughs by Transaction Volume:")
    borough_counts = df['district'].value_counts().head(10)
    for borough, count in borough_counts.items():
        avg_price = df[df['district'] == borough]['price'].mean()
        print(f"    {borough}: {count:,} transactions (Avg: £{avg_price:,.0f})")
    
    # By property type
    print("\n  Transactions by Property Type:")
    type_counts = df['property_type_name'].value_counts()
    for ptype, count in type_counts.items():
        pct = (count / len(df)) * 100
        avg_price = df[df['property_type_name'] == ptype]['price'].mean()
        print(f"    {ptype}: {count:,} ({pct:.1f}%) - Avg: £{avg_price:,.0f}")
    
    return summary


def create_aggregated_tables(df):
    """Create aggregated summary tables."""
    print("\n📈 Creating aggregated tables...")
    
    # 1. Monthly average prices by borough
    monthly_borough = df.groupby(['year_month', 'district']).agg({
        'price': ['mean', 'median', 'count'],
        'transaction_id': 'count'
    }).reset_index()
    monthly_borough.columns = ['year_month', 'district', 'avg_price', 
                                'median_price', 'transaction_count', 'count']
    
    # 2. Yearly summary by borough
    yearly_borough = df.groupby(['year', 'district']).agg({
        'price': ['mean', 'median', 'min', 'max', 'count'],
    }).reset_index()
    yearly_borough.columns = ['year', 'district', 'avg_price', 'median_price',
                               'min_price', 'max_price', 'transaction_count']
    
    # 3. Property type summary
    property_summary = df.groupby(['year', 'property_type_name']).agg({
        'price': ['mean', 'median', 'count']
    }).reset_index()
    property_summary.columns = ['year', 'property_type', 'avg_price', 
                                 'median_price', 'transaction_count']
    
    # 4. Regional summary
    regional_summary = df.groupby(['year', 'region']).agg({
        'price': ['mean', 'median', 'count']
    }).reset_index()
    regional_summary.columns = ['year', 'region', 'avg_price', 
                                 'median_price', 'transaction_count']
    
    print("  ✓ Monthly borough aggregates")
    print("  ✓ Yearly borough summary")
    print("  ✓ Property type summary")
    print("  ✓ Regional summary")
    
    return {
        'monthly_borough': monthly_borough,
        'yearly_borough': yearly_borough,
        'property_summary': property_summary,
        'regional_summary': regional_summary
    }


def save_to_database(df, aggregates):
    """Save cleaned data and aggregates to SQLite database."""
    print(f"\n💾 Saving to database: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Save main transactions table
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    print(f"  ✓ Saved transactions table: {len(df):,} rows")
    
    # Save aggregated tables
    for name, data in aggregates.items():
        data.to_sql(name, conn, if_exists='replace', index=False)
        print(f"  ✓ Saved {name} table: {len(data):,} rows")
    
    # Create indexes for better query performance
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_district ON transactions(district)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON transactions(year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_postcode ON transactions(postcode)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_property_type ON transactions(property_type)")
    print("  ✓ Created database indexes")
    
    conn.close()
    print(f"\n✓ Database saved successfully!")


def save_cleaned_csv(df):
    """Save cleaned data to CSV."""
    output_path = os.path.join(PROCESSED_DIR, "london_housing_cleaned.csv")
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved cleaned CSV: {output_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("UK Housing Market Analysis - Data Cleaning")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Load data
    df = load_london_data()
    
    # Step 2: Clean data
    df_cleaned = clean_data(df)
    
    # Step 3: Generate statistics
    summary = generate_summary_statistics(df_cleaned)
    
    # Step 4: Create aggregates
    aggregates = create_aggregated_tables(df_cleaned)
    
    # Step 5: Save to database
    save_to_database(df_cleaned, aggregates)
    
    # Step 6: Save cleaned CSV
    save_cleaned_csv(df_cleaned)
    
    print("\n" + "=" * 60)
    print("Data Cleaning Complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print("1. Run 03_analysis.ipynb for exploratory data analysis")
    print("2. Run SQL queries in sql/ folder for custom analysis")
    print("3. Connect Power BI to housing_market.db")


if __name__ == "__main__":
    main()

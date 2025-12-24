"""
UK Cost of Living Analysis - Data Cleaning Script
=================================================
Processes raw ONS data and creates SQLite database.

Author: Mounish Mesa
Date: December 2024
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime

print("=" * 60)
print("UK Cost of Living - Data Cleaning Script")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Paths
RAW_PATH = '../data/raw'
PROCESSED_PATH = '../data/processed'
DB_PATH = '../data/cost_of_living.db'

os.makedirs(PROCESSED_PATH, exist_ok=True)


def clean_ons_timeseries(filepath, value_column_name):
    """
    Clean ONS timeseries CSV files
    ONS files have metadata rows at top, then date and value columns
    """
    try:
        # Read raw file to check structure
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find the header row (usually contains 'Title' or starts with date-like values)
        header_row = 0
        for i, line in enumerate(lines):
            if 'Title' in line or (len(line.split(',')) >= 2 and line.strip()):
                # Check if next row looks like data
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and (next_line[0].isdigit() or next_line.startswith('"')):
                        header_row = i
                        break
        
        # Try different skip rows
        for skip in [header_row, 7, 8, 6, 5]:
            try:
                df = pd.read_csv(filepath, skiprows=skip)
                if len(df.columns) >= 2 and len(df) > 10:
                    break
            except:
                continue
        
        # Rename columns
        if len(df.columns) >= 2:
            df.columns = ['date', 'value'] + list(df.columns[2:])
        
        # Clean date column
        df['date'] = df['date'].astype(str).str.strip()
        
        # Parse different date formats
        # ONS uses formats like: "1988 JAN", "2024 NOV", "1988 Q1"
        def parse_ons_date(date_str):
            date_str = str(date_str).strip()
            try:
                # Try "YYYY MMM" format
                if len(date_str.split()) == 2:
                    parts = date_str.split()
                    year = parts[0]
                    month_str = parts[1].upper()
                    
                    month_map = {
                        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12',
                        'Q1': '03', 'Q2': '06', 'Q3': '09', 'Q4': '12'
                    }
                    
                    if month_str in month_map:
                        return f"{year}-{month_map[month_str]}-01"
                
                # Try standard date parsing
                return pd.to_datetime(date_str).strftime('%Y-%m-%d')
            except:
                return None
        
        df['date_clean'] = df['date'].apply(parse_ons_date)
        df = df.dropna(subset=['date_clean'])
        
        # Clean value column
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        
        # Create final dataframe
        result = pd.DataFrame({
            'date': pd.to_datetime(df['date_clean']),
            value_column_name: df['value'].values
        })
        
        # Extract year and month
        result['year'] = result['date'].dt.year
        result['month'] = result['date'].dt.month
        result['month_name'] = result['date'].dt.strftime('%B')
        
        # Sort by date
        result = result.sort_values('date').reset_index(drop=True)
        
        return result
        
    except Exception as e:
        print(f"    ⚠️ Error cleaning {filepath}: {e}")
        return None


def process_ons_files():
    """Process all downloaded ONS files"""
    
    print("📊 Processing ONS Files...")
    print("-" * 40)
    
    # Map of files to process
    ons_files = {
        'cpi_annual_rate.csv': 'cpi_annual',
        'cpih_annual_rate.csv': 'cpih_annual',
        'cpi_monthly_rate.csv': 'cpi_monthly',
        'food_inflation.csv': 'food_inflation',
        'housing_energy_inflation.csv': 'housing_energy_inflation',
    }
    
    processed_dfs = {}
    
    for filename, col_name in ons_files.items():
        filepath = os.path.join(RAW_PATH, filename)
        if os.path.exists(filepath):
            print(f"  Processing {filename}...", end=" ")
            df = clean_ons_timeseries(filepath, col_name)
            if df is not None and len(df) > 0:
                processed_dfs[col_name] = df
                print(f"✓ {len(df)} records ({df['year'].min()}-{df['year'].max()})")
            else:
                print("✗ No valid data")
        else:
            print(f"  ⚠️ File not found: {filename}")
    
    return processed_dfs


def merge_cpi_data(processed_dfs):
    """Merge all CPI data into single dataframe"""
    
    print("\n🔗 Merging CPI Data...")
    print("-" * 40)
    
    # Start with CPI annual as base
    if 'cpi_annual' not in processed_dfs:
        print("  ⚠️ No CPI annual data found, using generated data")
        return None
    
    merged = processed_dfs['cpi_annual'].copy()
    
    # Merge other series
    for name, df in processed_dfs.items():
        if name != 'cpi_annual':
            # Merge on date
            merge_cols = ['date', name]
            df_to_merge = df[['date', name]].copy()
            merged = merged.merge(df_to_merge, on='date', how='left')
            print(f"  ✓ Merged {name}")
    
    print(f"\n  Final merged dataset: {len(merged)} records")
    return merged


def process_generated_data():
    """Process the generated sample datasets"""
    
    print("\n📋 Processing Generated Data...")
    print("-" * 40)
    
    datasets = {}
    
    # CPI All Categories
    filepath = os.path.join(RAW_PATH, 'cpi_all_categories.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        datasets['cpi_categories'] = df
        print(f"  ✓ cpi_all_categories.csv: {len(df)} records")
    
    # Regional Prices
    filepath = os.path.join(RAW_PATH, 'regional_prices.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        datasets['regional_prices'] = df
        print(f"  ✓ regional_prices.csv: {len(df)} records")
    
    # Wages Data
    filepath = os.path.join(RAW_PATH, 'wages_data.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        datasets['wages'] = df
        print(f"  ✓ wages_data.csv: {len(df)} records")
    
    # Basket of Goods
    filepath = os.path.join(RAW_PATH, 'basket_of_goods.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        datasets['basket'] = df
        print(f"  ✓ basket_of_goods.csv: {len(df)} records")
    
    return datasets


def create_master_cpi_table(ons_merged, generated_data):
    """Create master CPI table combining ONS and generated data"""
    
    print("\n📊 Creating Master CPI Table...")
    print("-" * 40)
    
    # Use ONS data as primary source (more historical data)
    if ons_merged is not None and len(ons_merged) > 0:
        master = ons_merged.copy()
        
        # Add category breakdowns from generated data for recent years
        if 'cpi_categories' in generated_data:
            gen = generated_data['cpi_categories']
            # Only use generated data for category breakdowns
            category_cols = ['food_beverages', 'alcohol_tobacco', 'clothing_footwear',
                           'housing_energy', 'furniture_household', 'health', 'transport',
                           'communication', 'recreation_culture', 'education', 
                           'restaurants_hotels', 'miscellaneous']
            
            # Merge on date
            gen_subset = gen[['date'] + [c for c in category_cols if c in gen.columns]]
            master = master.merge(gen_subset, on='date', how='left')
        
        print(f"  ✓ Master table created with {len(master)} records")
        print(f"    Date range: {master['date'].min().strftime('%Y-%m-%d')} to {master['date'].max().strftime('%Y-%m-%d')}")
        print(f"    Columns: {len(master.columns)}")
        
    else:
        # Fall back to generated data
        master = generated_data.get('cpi_categories', pd.DataFrame())
        print(f"  ℹ️ Using generated data: {len(master)} records")
    
    return master


def calculate_derived_metrics(df):
    """Calculate additional derived metrics"""
    
    print("\n📈 Calculating Derived Metrics...")
    print("-" * 40)
    
    if df is None or len(df) == 0:
        return df
    
    df = df.copy()
    
    # Ensure sorted by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Year-over-Year change (if we have annual CPI)
    if 'cpi_annual' in df.columns:
        df['cpi_yoy_change'] = df['cpi_annual'].diff(12)  # 12 months ago
        print("  ✓ Added YoY change")
    
    # Cumulative inflation (base = first month)
    if 'cpi_annual' in df.columns:
        # Calculate cumulative effect of monthly inflation
        df['cumulative_inflation'] = ((1 + df['cpi_annual']/100/12).cumprod() - 1) * 100
        print("  ✓ Added cumulative inflation")
    
    # BOE Target comparison (2% target)
    if 'cpi_annual' in df.columns:
        df['above_target'] = df['cpi_annual'] > 2.0
        df['deviation_from_target'] = df['cpi_annual'] - 2.0
        print("  ✓ Added BOE target comparison")
    
    # Inflation regime classification
    if 'cpi_annual' in df.columns:
        def classify_inflation(rate):
            if pd.isna(rate):
                return 'Unknown'
            elif rate < 0:
                return 'Deflation'
            elif rate < 1:
                return 'Very Low'
            elif rate < 2:
                return 'Below Target'
            elif rate < 3:
                return 'On Target'
            elif rate < 5:
                return 'Elevated'
            elif rate < 10:
                return 'High'
            else:
                return 'Very High'
        
        df['inflation_regime'] = df['cpi_annual'].apply(classify_inflation)
        print("  ✓ Added inflation regime classification")
    
    return df


def create_sqlite_database(master_cpi, generated_data):
    """Create SQLite database with all tables"""
    
    print("\n💾 Creating SQLite Database...")
    print("-" * 40)
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Table 1: Master CPI Data
        if master_cpi is not None and len(master_cpi) > 0:
            # Convert date to string for SQLite
            master_cpi_db = master_cpi.copy()
            master_cpi_db['date'] = master_cpi_db['date'].dt.strftime('%Y-%m-%d')
            master_cpi_db.to_sql('cpi_data', conn, index=False, if_exists='replace')
            print(f"  ✓ Table 'cpi_data': {len(master_cpi_db)} records")
        
        # Table 2: Regional Prices
        if 'regional_prices' in generated_data:
            generated_data['regional_prices'].to_sql('regional_prices', conn, 
                                                     index=False, if_exists='replace')
            print(f"  ✓ Table 'regional_prices': {len(generated_data['regional_prices'])} records")
        
        # Table 3: Wages Data
        if 'wages' in generated_data:
            wages_db = generated_data['wages'].copy()
            wages_db['date'] = pd.to_datetime(wages_db['date']).dt.strftime('%Y-%m-%d')
            wages_db.to_sql('wages', conn, index=False, if_exists='replace')
            print(f"  ✓ Table 'wages': {len(wages_db)} records")
        
        # Table 4: Basket of Goods
        if 'basket' in generated_data:
            generated_data['basket'].to_sql('basket_of_goods', conn, 
                                           index=False, if_exists='replace')
            print(f"  ✓ Table 'basket_of_goods': {len(generated_data['basket'])} records")
        
        # Create indexes for performance
        print("\n  Creating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cpi_date ON cpi_data(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cpi_year ON cpi_data(year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_regional_year ON regional_prices(year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_regional_region ON regional_prices(region)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wages_date ON wages(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_basket_year ON basket_of_goods(year)")
        print("  ✓ Indexes created")
        
        conn.commit()
        
    finally:
        conn.close()
    
    # Report database size
    db_size = os.path.getsize(DB_PATH) / 1024
    print(f"\n  Database created: {db_size:.1f} KB")


def save_processed_files(master_cpi, generated_data):
    """Save processed CSV files"""
    
    print("\n💾 Saving Processed Files...")
    print("-" * 40)
    
    # Save master CPI
    if master_cpi is not None and len(master_cpi) > 0:
        filepath = os.path.join(PROCESSED_PATH, 'master_cpi_data.csv')
        master_cpi.to_csv(filepath, index=False)
        print(f"  ✓ master_cpi_data.csv ({len(master_cpi)} records)")
    
    # Save regional data
    if 'regional_prices' in generated_data:
        filepath = os.path.join(PROCESSED_PATH, 'regional_prices_clean.csv')
        generated_data['regional_prices'].to_csv(filepath, index=False)
        print(f"  ✓ regional_prices_clean.csv")
    
    # Save wages data
    if 'wages' in generated_data:
        filepath = os.path.join(PROCESSED_PATH, 'wages_clean.csv')
        generated_data['wages'].to_csv(filepath, index=False)
        print(f"  ✓ wages_clean.csv")


def print_data_summary(master_cpi, generated_data):
    """Print summary statistics"""
    
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    
    if master_cpi is not None and len(master_cpi) > 0:
        print("\n📊 CPI Data:")
        print(f"   Records: {len(master_cpi)}")
        print(f"   Date Range: {master_cpi['date'].min().strftime('%Y-%m')} to {master_cpi['date'].max().strftime('%Y-%m')}")
        if 'cpi_annual' in master_cpi.columns:
            recent = master_cpi[master_cpi['date'] >= '2024-01-01']
            if len(recent) > 0:
                print(f"   Latest CPI: {recent['cpi_annual'].iloc[-1]:.1f}%")
                print(f"   2024 Average: {recent['cpi_annual'].mean():.1f}%")
    
    if 'regional_prices' in generated_data:
        df = generated_data['regional_prices']
        print(f"\n🗺️ Regional Data:")
        print(f"   Regions: {df['region'].nunique()}")
        print(f"   Years: {df['year'].min()}-{df['year'].max()}")
        
        latest = df[df['year'] == df['year'].max()]
        most_expensive = latest.loc[latest['overall_index'].idxmax(), 'region']
        cheapest = latest.loc[latest['overall_index'].idxmin(), 'region']
        print(f"   Most Expensive: {most_expensive}")
        print(f"   Most Affordable: {cheapest}")


def main():
    """Main execution function"""
    
    # Step 1: Process ONS files
    ons_data = process_ons_files()
    
    # Step 2: Merge ONS data
    ons_merged = merge_cpi_data(ons_data)
    
    # Step 3: Process generated data
    generated_data = process_generated_data()
    
    # Step 4: Create master CPI table
    master_cpi = create_master_cpi_table(ons_merged, generated_data)
    
    # Step 5: Calculate derived metrics
    master_cpi = calculate_derived_metrics(master_cpi)
    
    # Step 6: Create SQLite database
    create_sqlite_database(master_cpi, generated_data)
    
    # Step 7: Save processed CSV files
    save_processed_files(master_cpi, generated_data)
    
    # Step 8: Print summary
    print_data_summary(master_cpi, generated_data)
    
    print("\n" + "=" * 60)
    print("DATA CLEANING COMPLETE")
    print("=" * 60)
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Next step: Run 03_analysis.py to generate visualizations")
    print("   Or explore the database: data/cost_of_living.db")


if __name__ == "__main__":
    main()
"""
UK Cost of Living Analysis - Data Download Script (Updated)
===========================================================
Downloads official ONS data via direct CSV downloads.

Author: Mounish Mesa
Date: December 2024
"""

import requests
import pandas as pd
import os
from datetime import datetime
import io

# Create data directories if they don't exist
os.makedirs('../data/raw', exist_ok=True)
os.makedirs('../data/processed', exist_ok=True)

print("=" * 60)
print("UK Cost of Living - Data Download Script")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def download_file(url, filename, description):
    """Download a file from URL and save to data/raw/"""
    try:
        print(f"  Downloading {description}...", end=" ")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        filepath = f'../data/raw/{filename}'
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        size_kb = len(response.content) / 1024
        print(f"✓ ({size_kb:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def download_ons_datasets():
    """Download ONS datasets from direct links"""
    
    print("\n📊 Downloading ONS Datasets...")
    print("-" * 40)
    
    # ONS direct download URLs (these are stable links)
    datasets = [
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/d7g7/mm23',
            'filename': 'cpi_annual_rate.csv',
            'description': 'CPI Annual Rate'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l55o/mm23',
            'filename': 'cpih_annual_rate.csv',
            'description': 'CPIH Annual Rate'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/d7g8/mm23',
            'filename': 'cpi_monthly_rate.csv',
            'description': 'CPI Monthly Rate'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l59c/mm23',
            'filename': 'food_inflation.csv',
            'description': 'Food & Beverages Inflation'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l59h/mm23',
            'filename': 'housing_energy_inflation.csv',
            'description': 'Housing & Energy Inflation'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l59m/mm23',
            'filename': 'transport_inflation.csv',
            'description': 'Transport Inflation'
        },
        {
            'url': 'https://www.ons.gov.uk/generator?format=csv&uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/timeseries/kab9/lms',
            'filename': 'avg_weekly_earnings.csv',
            'description': 'Average Weekly Earnings'
        },
    ]
    
    success_count = 0
    for ds in datasets:
        if download_file(ds['url'], ds['filename'], ds['description']):
            success_count += 1
    
    print(f"\n  Downloaded {success_count}/{len(datasets)} datasets from ONS")
    return success_count > 0


def create_comprehensive_sample_data():
    """
    Create comprehensive sample dataset based on actual UK patterns
    This serves as primary data source if downloads fail
    """
    
    print("\n🔧 Creating Comprehensive Dataset...")
    print("-" * 40)
    
    import numpy as np
    np.random.seed(42)
    
    # Generate monthly dates from Jan 2015 to Nov 2024
    dates = pd.date_range(start='2015-01-01', end='2024-11-01', freq='MS')
    
    # =================================================================
    # CPI DATA - Based on actual UK inflation patterns
    # =================================================================
    
    cpi_records = []
    
    for date in dates:
        year, month = date.year, date.month
        
        # Base CPI pattern following UK reality
        if year <= 2016:
            base_cpi = 0.5 + np.random.normal(0, 0.3)
        elif year == 2017:
            base_cpi = 2.5 + np.random.normal(0, 0.2)
        elif year == 2018:
            base_cpi = 2.3 + np.random.normal(0, 0.2)
        elif year == 2019:
            base_cpi = 1.8 + np.random.normal(0, 0.2)
        elif year == 2020:
            if month <= 3:
                base_cpi = 1.7 + np.random.normal(0, 0.2)
            elif month <= 8:
                base_cpi = 0.5 + np.random.normal(0, 0.3)  # COVID dip
            else:
                base_cpi = 0.7 + np.random.normal(0, 0.2)
        elif year == 2021:
            base_cpi = 1.5 + (month / 12) * 3.5 + np.random.normal(0, 0.3)
        elif year == 2022:
            if month <= 4:
                base_cpi = 6 + (month / 4) * 2 + np.random.normal(0, 0.3)
            elif month <= 10:
                base_cpi = 9 + (month - 4) / 6 * 2.1 + np.random.normal(0, 0.3)
            else:
                base_cpi = 10.5 + np.random.normal(0, 0.2)
        elif year == 2023:
            base_cpi = 10.4 - (month / 12) * 6.5 + np.random.normal(0, 0.3)
        else:  # 2024
            base_cpi = 4.0 - (month / 12) * 1.5 + np.random.normal(0, 0.2)
        
        base_cpi = max(-1, base_cpi)  # Floor at -1%
        
        # Category-specific inflation (relative to base)
        food_mult = 1.3 if year >= 2022 else 1.1
        energy_mult = 2.0 if year == 2022 else (1.5 if year == 2023 else 1.0)
        transport_mult = 0.8 if year == 2020 else 1.1
        
        cpi_records.append({
            'date': date.strftime('%Y-%m-%d'),
            'year': year,
            'month': month,
            'month_name': date.strftime('%B'),
            'cpi_annual': round(base_cpi, 1),
            'cpih_annual': round(base_cpi + 0.3 + np.random.normal(0, 0.1), 1),
            'food_beverages': round(base_cpi * food_mult + np.random.normal(0, 0.5), 1),
            'alcohol_tobacco': round(base_cpi * 0.9 + np.random.normal(0, 0.3), 1),
            'clothing_footwear': round(base_cpi * 0.5 + np.random.normal(0, 0.8), 1),
            'housing_energy': round(base_cpi * energy_mult + np.random.normal(0, 1), 1),
            'furniture_household': round(base_cpi * 0.9 + np.random.normal(0, 0.4), 1),
            'health': round(base_cpi * 0.7 + np.random.normal(0, 0.3), 1),
            'transport': round(base_cpi * transport_mult + np.random.normal(0, 0.6), 1),
            'communication': round(base_cpi * 0.4 + np.random.normal(0, 0.5), 1),
            'recreation_culture': round(base_cpi * 0.6 + np.random.normal(0, 0.4), 1),
            'education': round(base_cpi * 1.1 + np.random.normal(0, 0.3), 1),
            'restaurants_hotels': round(base_cpi * 1.2 + np.random.normal(0, 0.4), 1),
            'miscellaneous': round(base_cpi * 0.8 + np.random.normal(0, 0.3), 1),
        })
    
    cpi_df = pd.DataFrame(cpi_records)
    cpi_df.to_csv('../data/raw/cpi_all_categories.csv', index=False)
    print(f"  ✓ Created cpi_all_categories.csv ({len(cpi_df)} records)")
    
    # =================================================================
    # REGIONAL PRICE DATA
    # =================================================================
    
    regions = {
        'London': {'base': 115, 'housing': 145},
        'South East': {'base': 106, 'housing': 120},
        'East of England': {'base': 103, 'housing': 110},
        'South West': {'base': 101, 'housing': 105},
        'West Midlands': {'base': 95, 'housing': 90},
        'East Midlands': {'base': 94, 'housing': 88},
        'Yorkshire and Humber': {'base': 93, 'housing': 85},
        'North West': {'base': 94, 'housing': 87},
        'North East': {'base': 91, 'housing': 80},
        'Wales': {'base': 92, 'housing': 82},
        'Scotland': {'base': 97, 'housing': 90},
        'Northern Ireland': {'base': 94, 'housing': 85},
    }
    
    regional_records = []
    for year in range(2015, 2024):
        for region, indices in regions.items():
            # Add slight year-over-year variation
            year_adj = (year - 2015) * 0.5
            
            regional_records.append({
                'year': year,
                'region': region,
                'overall_index': round(indices['base'] + year_adj + np.random.normal(0, 1), 1),
                'housing_index': round(indices['housing'] + year_adj * 1.5 + np.random.normal(0, 2), 1),
                'food_index': round(100 + np.random.normal(0, 2), 1),
                'transport_index': round(100 + (indices['base'] - 100) * 0.3 + np.random.normal(0, 2), 1),
                'recreation_index': round(100 + (indices['base'] - 100) * 0.4 + np.random.normal(0, 2), 1),
            })
    
    regional_df = pd.DataFrame(regional_records)
    regional_df.to_csv('../data/raw/regional_prices.csv', index=False)
    print(f"  ✓ Created regional_prices.csv ({len(regional_df)} records)")
    
    # =================================================================
    # WAGES DATA
    # =================================================================
    
    wages_records = []
    base_wage = 480  # Starting average weekly earnings in 2015
    
    for date in dates:
        year, month = date.year, date.month
        
        # Wage growth pattern
        months_since_start = (year - 2015) * 12 + month
        wage_growth = months_since_start * 1.2  # ~2.5% annual growth
        
        # COVID impact
        if year == 2020 and 4 <= month <= 8:
            wage_adj = -20
        else:
            wage_adj = 0
        
        avg_wage = base_wage + wage_growth + wage_adj + np.random.normal(0, 5)
        
        wages_records.append({
            'date': date.strftime('%Y-%m-%d'),
            'year': year,
            'month': month,
            'avg_weekly_earnings': round(avg_wage, 2),
            'private_sector': round(avg_wage * 0.98 + np.random.normal(0, 5), 2),
            'public_sector': round(avg_wage * 1.02 + np.random.normal(0, 4), 2),
            'yoy_change': round(2.5 + np.random.normal(0, 0.5), 1) if year > 2015 else None,
        })
    
    wages_df = pd.DataFrame(wages_records)
    wages_df.to_csv('../data/raw/wages_data.csv', index=False)
    print(f"  ✓ Created wages_data.csv ({len(wages_df)} records)")
    
    # =================================================================
    # BASKET OF GOODS - Average Prices
    # =================================================================
    
    items = {
        'Bread (800g white loaf)': {'base': 1.10, 'category': 'Food'},
        'Milk (4 pints)': {'base': 1.35, 'category': 'Food'},
        'Eggs (12 large)': {'base': 2.20, 'category': 'Food'},
        'Butter (250g)': {'base': 1.80, 'category': 'Food'},
        'Cheese (500g cheddar)': {'base': 3.50, 'category': 'Food'},
        'Chicken breast (1kg)': {'base': 6.50, 'category': 'Food'},
        'Beef mince (500g)': {'base': 4.00, 'category': 'Food'},
        'Petrol (litre)': {'base': 1.15, 'category': 'Transport'},
        'Diesel (litre)': {'base': 1.18, 'category': 'Transport'},
        'Electricity (kWh)': {'base': 0.14, 'category': 'Energy'},
        'Gas (kWh)': {'base': 0.04, 'category': 'Energy'},
        'Cinema ticket': {'base': 10.50, 'category': 'Recreation'},
        'Pint of beer (pub)': {'base': 3.60, 'category': 'Alcohol'},
        'Coffee (cafe)': {'base': 2.80, 'category': 'Restaurants'},
        'Gym membership (monthly)': {'base': 35.00, 'category': 'Recreation'},
    }
    
    basket_records = []
    for year in range(2015, 2025):
        for item, details in items.items():
            # Price growth varies by category
            if details['category'] == 'Energy' and year >= 2022:
                growth_mult = 1.8 if year == 2022 else 1.5
            elif details['category'] == 'Food' and year >= 2022:
                growth_mult = 1.3
            else:
                growth_mult = 1.0
            
            years_growth = (year - 2015) * 0.025 * growth_mult
            price = details['base'] * (1 + years_growth) + np.random.normal(0, details['base'] * 0.02)
            
            basket_records.append({
                'year': year,
                'item': item,
                'category': details['category'],
                'average_price': round(max(price, details['base'] * 0.8), 2),
                'unit': 'GBP',
            })
    
    basket_df = pd.DataFrame(basket_records)
    basket_df.to_csv('../data/raw/basket_of_goods.csv', index=False)
    print(f"  ✓ Created basket_of_goods.csv ({len(basket_df)} records)")
    
    return cpi_df, regional_df, wages_df, basket_df


def process_ons_downloads():
    """Process any successfully downloaded ONS files"""
    
    print("\n📝 Processing Downloaded Files...")
    print("-" * 40)
    
    files_processed = 0
    
    # Check for downloaded ONS files and process them
    ons_files = [
        'cpi_annual_rate.csv',
        'cpih_annual_rate.csv',
        'food_inflation.csv',
        'housing_energy_inflation.csv',
        'transport_inflation.csv',
    ]
    
    for filename in ons_files:
        filepath = f'../data/raw/{filename}'
        if os.path.exists(filepath):
            try:
                # ONS CSV files have metadata rows at top
                df = pd.read_csv(filepath, skiprows=7)
                if len(df) > 0:
                    print(f"  ✓ Processed {filename}: {len(df)} rows")
                    files_processed += 1
            except Exception as e:
                print(f"  ⚠️ Could not process {filename}: {e}")
    
    if files_processed == 0:
        print("  ℹ️ No ONS files to process, using generated sample data")
    
    return files_processed


def main():
    """Main execution function"""
    
    # Step 1: Try downloading from ONS
    ons_success = download_ons_datasets()
    
    # Step 2: Process any downloaded files
    process_ons_downloads()
    
    # Step 3: Create comprehensive sample data (always create as backup/supplement)
    create_comprehensive_sample_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print("\nFiles saved to data/raw/:")
    
    raw_path = '../data/raw'
    if os.path.exists(raw_path):
        total_size = 0
        for f in sorted(os.listdir(raw_path)):
            filepath = os.path.join(raw_path, f)
            size_kb = os.path.getsize(filepath) / 1024
            total_size += size_kb
            print(f"  📄 {f} ({size_kb:.1f} KB)")
        print(f"\n  Total: {total_size:.1f} KB")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ Next step: Run 02_data_cleaning.py to process the data")


if __name__ == "__main__":
    main()
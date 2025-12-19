"""
UK Housing Market Analysis - Data Download Script
=================================================
Downloads HM Land Registry Price Paid Data for analysis.

Data Source: https://www.gov.uk/government/collections/price-paid-data
License: Open Government Licence v3.0

Author: Mounish Mesa
"""

import os
import requests
import pandas as pd
from datetime import datetime

# Configuration
DATA_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

# HM Land Registry Price Paid Data URLs
# Full dataset is very large (~4GB), so we'll use yearly files
BASE_URL = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com"

YEARLY_FILES = {
    "2024": f"{BASE_URL}/pp-2024.csv",
    "2023": f"{BASE_URL}/pp-2023.csv",
    "2022": f"{BASE_URL}/pp-2022.csv",
    "2021": f"{BASE_URL}/pp-2021.csv",
    "2020": f"{BASE_URL}/pp-2020.csv",
}

# Column names for the Price Paid Data
COLUMNS = [
    "transaction_id",
    "price",
    "date_of_transfer",
    "postcode",
    "property_type",
    "old_new",
    "duration",
    "paon",  # Primary Addressable Object Name
    "saon",  # Secondary Addressable Object Name
    "street",
    "locality",
    "town_city",
    "district",
    "county",
    "ppd_category",
    "record_status"
]

# Property type mapping
PROPERTY_TYPES = {
    "D": "Detached",
    "S": "Semi-Detached",
    "T": "Terraced",
    "F": "Flat/Maisonette",
    "O": "Other"
}

# Old/New mapping
OLD_NEW = {
    "Y": "New Build",
    "N": "Established"
}

# Duration mapping
DURATION = {
    "F": "Freehold",
    "L": "Leasehold"
}


def create_directories():
    """Create necessary directories for data storage."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"✓ Created directories: {DATA_DIR}, {PROCESSED_DIR}")


def download_file(url, filename):
    """Download a file from URL with progress indication."""
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"⏭ File already exists: {filename}")
        return filepath
    
    print(f"⬇ Downloading: {filename}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end="")
        
        print(f"\n✓ Downloaded: {filename}")
        return filepath
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {filename}: {e}")
        return None


def download_all_years(years=None):
    """Download Price Paid data for specified years."""
    if years is None:
        years = list(YEARLY_FILES.keys())
    
    downloaded_files = []
    
    for year in years:
        if year in YEARLY_FILES:
            url = YEARLY_FILES[year]
            filename = f"pp-{year}.csv"
            filepath = download_file(url, filename)
            if filepath:
                downloaded_files.append(filepath)
        else:
            print(f"⚠ Year {year} not available")
    
    return downloaded_files


def load_and_preview_data(filepath, nrows=1000):
    """Load CSV and preview the data."""
    print(f"\n📊 Loading preview of {filepath}...")
    
    df = pd.read_csv(
        filepath,
        names=COLUMNS,
        nrows=nrows,
        low_memory=False
    )
    
    # Convert date
    df['date_of_transfer'] = pd.to_datetime(df['date_of_transfer'])
    
    # Map categorical values
    df['property_type_name'] = df['property_type'].map(PROPERTY_TYPES)
    df['old_new_name'] = df['old_new'].map(OLD_NEW)
    df['duration_name'] = df['duration'].map(DURATION)
    
    print(f"\n✓ Loaded {len(df):,} rows")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData Types:\n{df.dtypes}")
    print(f"\nSample Data:\n{df.head()}")
    print(f"\nPrice Statistics:\n{df['price'].describe()}")
    
    return df


def filter_london_data(input_file, output_file):
    """Filter data for London boroughs only."""
    print(f"\n🏙 Filtering London data from {input_file}...")
    
    # London boroughs/districts
    london_districts = [
        'CITY OF LONDON', 'BARKING AND DAGENHAM', 'BARNET', 'BEXLEY',
        'BRENT', 'BROMLEY', 'CAMDEN', 'CROYDON', 'EALING', 'ENFIELD',
        'GREENWICH', 'HACKNEY', 'HAMMERSMITH AND FULHAM', 'HARINGEY',
        'HARROW', 'HAVERING', 'HILLINGDON', 'HOUNSLOW', 'ISLINGTON',
        'KENSINGTON AND CHELSEA', 'KINGSTON UPON THAMES', 'LAMBETH',
        'LEWISHAM', 'MERTON', 'NEWHAM', 'REDBRIDGE', 'RICHMOND UPON THAMES',
        'SOUTHWARK', 'SUTTON', 'TOWER HAMLETS', 'WALTHAM FOREST',
        'WANDSWORTH', 'WESTMINSTER'
    ]
    
    # Read in chunks to handle large files
    chunks = []
    chunk_size = 100000
    
    for chunk in pd.read_csv(input_file, names=COLUMNS, chunksize=chunk_size):
        # Filter for London
        london_chunk = chunk[chunk['district'].str.upper().isin(london_districts)]
        chunks.append(london_chunk)
        print(f"  Processed chunk: {len(london_chunk):,} London records")
    
    # Combine all chunks
    london_df = pd.concat(chunks, ignore_index=True)
    
    # Save filtered data
    output_path = os.path.join(PROCESSED_DIR, output_file)
    london_df.to_csv(output_path, index=False)
    
    print(f"✓ Saved {len(london_df):,} London records to {output_path}")
    
    return london_df


def main():
    """Main execution function."""
    print("=" * 60)
    print("UK Housing Market Analysis - Data Download")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Download data (start with recent years)
    print("\n" + "=" * 60)
    print("Downloading HM Land Registry Price Paid Data")
    print("=" * 60)
    
    # Download last 3 years for manageable size
    years_to_download = ["2024", "2023", "2022"]
    downloaded = download_all_years(years_to_download)
    
    # Step 3: Preview the data
    if downloaded:
        print("\n" + "=" * 60)
        print("Data Preview")
        print("=" * 60)
        df_preview = load_and_preview_data(downloaded[0])
    
    # Step 4: Filter London data
    print("\n" + "=" * 60)
    print("Filtering London Data")
    print("=" * 60)
    
    for filepath in downloaded:
        year = filepath.split("-")[-1].replace(".csv", "")
        output_file = f"london-pp-{year}.csv"
        filter_london_data(filepath, output_file)
    
    print("\n" + "=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print("1. Run 02_data_cleaning.py to clean and prepare the data")
    print("2. Run 03_analysis.ipynb for exploratory analysis")
    print("3. Run 04_modelling.py for price predictions")


if __name__ == "__main__":
    main()

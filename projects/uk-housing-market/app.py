"""
London Housing Market Dashboard
================================
Interactive Streamlit web application for exploring UK housing data.

Author: Mounish Mesa
Portfolio: https://mounishmesa.github.io
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="London Housing Market Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_data():
    """Load data from CSV file."""
    import os
    
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different file locations
    possible_paths = [
        os.path.join(current_dir, 'data', 'london_housing_sample.csv'),
        os.path.join(current_dir, 'data', 'processed', 'london_housing_cleaned.csv'),
        'data/london_housing_sample.csv',
        'london_housing_sample.csv'
    ]
    
    df = None
    for path in possible_paths:
        try:
            df = pd.read_csv(path)
            st.sidebar.success(f"Data loaded from: {path}")
            break
        except FileNotFoundError:
            continue
    
    if df is None:
        st.error(f"Data file not found! Tried: {possible_paths}")
        st.error(f"Current directory: {current_dir}")
        st.error(f"Files in current dir: {os.listdir(current_dir)}")
        st.stop()
    
    # Convert date
    df['date_of_transfer'] = pd.to_datetime(df['date_of_transfer'])
    df['year'] = df['date_of_transfer'].dt.year
    df['month'] = df['date_of_transfer'].dt.month
    df['month_name'] = df['date_of_transfer'].dt.strftime('%B')
    
    return df

# Load data
df = load_data()

# =============================================================================
# SIDEBAR FILTERS
# =============================================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Greater_London_UK_locator_map_2010.svg/300px-Greater_London_UK_locator_map_2010.svg.png", width=200)
st.sidebar.title("🔍 Filters")

# Year filter
years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options=years,
    default=years
)

# Borough filter
boroughs = sorted(df['district'].unique())
selected_boroughs = st.sidebar.multiselect(
    "Select Borough(s)",
    options=boroughs,
    default=boroughs
)

# Property type filter
property_types = df['property_type_name'].unique()
selected_types = st.sidebar.multiselect(
    "Select Property Type(s)",
    options=property_types,
    default=property_types
)

# Price range filter
min_price = int(df['price'].min())
max_price = int(df['price'].quantile(0.99))  # Cap at 99th percentile
price_range = st.sidebar.slider(
    "Price Range (£)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    format="£%d"
)

# Filter data
filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['district'].isin(selected_boroughs)) &
    (df['property_type_name'].isin(selected_types)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1])
]

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<h1 class="main-header">🏠 London Housing Market Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive analysis of 300,000+ property transactions across London</p>', unsafe_allow_html=True)

# =============================================================================
# KPI METRICS
# =============================================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📊 Total Transactions",
        value=f"{len(filtered_df):,}"
    )

with col2:
    avg_price = filtered_df['price'].mean()
    st.metric(
        label="💰 Average Price",
        value=f"£{avg_price:,.0f}"
    )

with col3:
    median_price = filtered_df['price'].median()
    st.metric(
        label="📈 Median Price",
        value=f"£{median_price:,.0f}"
    )

with col4:
    total_value = filtered_df['price'].sum()
    st.metric(
        label="🏦 Total Market Value",
        value=f"£{total_value/1e9:.1f}B"
    )

with col5:
    num_boroughs = filtered_df['district'].nunique()
    st.metric(
        label="🗺️ Boroughs",
        value=f"{num_boroughs}"
    )

st.markdown("---")

# =============================================================================
# MAIN CHARTS
# =============================================================================
col_left, col_right = st.columns(2)

# ----- LEFT COLUMN: Borough Prices -----
with col_left:
    st.subheader("🏆 Top 10 Most Expensive Boroughs")
    
    borough_avg = filtered_df.groupby('district')['price'].mean().sort_values(ascending=True).tail(10)
    
    fig_borough = px.bar(
        x=borough_avg.values,
        y=borough_avg.index,
        orientation='h',
        color=borough_avg.values,
        color_continuous_scale='Blues',
        labels={'x': 'Average Price (£)', 'y': 'Borough'}
    )
    fig_borough.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_tickformat='£,.0f'
    )
    fig_borough.update_traces(
        texttemplate='£%{x:,.0f}',
        textposition='outside'
    )
    st.plotly_chart(fig_borough, use_container_width=True)

# ----- RIGHT COLUMN: Price Trends -----
with col_right:
    st.subheader("📈 Price Trends Over Time")
    
    monthly_avg = filtered_df.groupby(filtered_df['date_of_transfer'].dt.to_period('M')).agg({
        'price': 'mean'
    }).reset_index()
    monthly_avg['date_of_transfer'] = monthly_avg['date_of_transfer'].astype(str)
    
    fig_trend = px.line(
        monthly_avg,
        x='date_of_transfer',
        y='price',
        labels={'date_of_transfer': 'Month', 'price': 'Average Price (£)'}
    )
    fig_trend.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_tickformat='£,.0f'
    )
    fig_trend.update_traces(line_color='#2563eb', line_width=2)
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# =============================================================================
# SECOND ROW OF CHARTS
# =============================================================================
col_left2, col_middle2, col_right2 = st.columns(3)

# ----- Property Type Distribution -----
with col_left2:
    st.subheader("🏗️ Property Types")
    
    type_counts = filtered_df['property_type_name'].value_counts()
    
    fig_donut = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_donut.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ----- Price by Property Type -----
with col_middle2:
    st.subheader("💷 Avg Price by Type")
    
    type_avg = filtered_df.groupby('property_type_name')['price'].mean().sort_values(ascending=False)
    
    fig_type_price = px.bar(
        x=type_avg.index,
        y=type_avg.values,
        color=type_avg.values,
        color_continuous_scale='Greens',
        labels={'x': 'Property Type', 'y': 'Average Price (£)'}
    )
    fig_type_price.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        coloraxis_showscale=False,
        yaxis_tickformat='£,.0f',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_type_price, use_container_width=True)

# ----- Regional Comparison -----
with col_right2:
    st.subheader("🧭 Regional Prices")
    
    if 'region' in filtered_df.columns:
        region_avg = filtered_df.groupby('region')['price'].mean().sort_values(ascending=False)
        
        fig_region = px.bar(
            x=region_avg.index,
            y=region_avg.values,
            color=region_avg.index,
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={'x': 'Region', 'y': 'Average Price (£)'}
        )
        fig_region.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            yaxis_tickformat='£,.0f'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("Regional data not available")

st.markdown("---")

# =============================================================================
# DATA TABLE
# =============================================================================
st.subheader("📋 Transaction Data")

# Show top transactions
show_rows = st.slider("Number of rows to display", 10, 100, 20)

display_df = filtered_df[['date_of_transfer', 'district', 'postcode', 'property_type_name', 'price']].copy()
display_df.columns = ['Date', 'Borough', 'Postcode', 'Property Type', 'Price']
display_df = display_df.sort_values('Price', ascending=False).head(show_rows)
display_df['Price'] = display_df['Price'].apply(lambda x: f"£{x:,.0f}")
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')

st.dataframe(display_df, use_container_width=True, hide_index=True)

# =============================================================================
# DOWNLOAD DATA
# =============================================================================
st.subheader("📥 Download Data")

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv,
        file_name="london_housing_filtered.csv",
        mime="text/csv"
    )

with col_dl2:
    # Download summary
    summary = filtered_df.groupby('district').agg({
        'price': ['mean', 'median', 'count']
    }).reset_index()
    summary.columns = ['Borough', 'Avg Price', 'Median Price', 'Transactions']
    summary_csv = summary.to_csv(index=False)
    st.download_button(
        label="Download Borough Summary (CSV)",
        data=summary_csv,
        file_name="borough_summary.csv",
        mime="text/csv"
    )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p>Built by <a href='https://mounishmesa.github.io' target='_blank'>Mounish Mesa</a> | 
    Data Source: <a href='https://www.gov.uk/government/collections/price-paid-data' target='_blank'>HM Land Registry</a></p>
    <p>💼 <a href='https://linkedin.com/in/mounish-jm' target='_blank'>LinkedIn</a> | 
    🐱 <a href='https://github.com/mounishmesa' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)

"""
UK Cost of Living Analysis - Streamlit Dashboard
================================================
Interactive dashboard for exploring UK inflation and cost of living data.

Author: Mounish Mesa
Date: December 2024

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Page configuration
st.set_page_config(
    page_title="UK Cost of Living Analysis",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    [data-testid="stMetricLabel"] {
        color: #334155 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #1e3a5f !important;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    .insight-box {
        background-color: #f0f9ff;
        border-left: 4px solid #2563eb;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data from CSV files"""
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible paths
    possible_paths = [
        os.path.join(current_dir, 'data', 'processed'),  # Same folder as app.py
        os.path.join(current_dir, '..', 'data', 'processed'),  # Parent folder
        'data/processed',  # Relative path
        '../data/processed',  # Relative parent
    ]
    
    # Find the correct path
    base_path = None
    for path in possible_paths:
        test_file = os.path.join(path, 'master_cpi_data.csv')
        if os.path.exists(test_file):
            base_path = path
            break
    
    if base_path is None:
        st.error(f"Data files not found. Searched in: {possible_paths}")
        st.error(f"Current directory: {current_dir}")
        st.error(f"Files in current dir: {os.listdir(current_dir) if os.path.exists(current_dir) else 'N/A'}")
        return {}
    
    data = {}
    
    # Load CPI data
    cpi_path = os.path.join(base_path, 'master_cpi_data.csv')
    if os.path.exists(cpi_path):
        data['cpi'] = pd.read_csv(cpi_path)
        data['cpi']['date'] = pd.to_datetime(data['cpi']['date'])
    
    # Load regional data
    regional_path = os.path.join(base_path, 'regional_prices_clean.csv')
    if os.path.exists(regional_path):
        data['regional'] = pd.read_csv(regional_path)
    
    # Load wages data
    wages_path = os.path.join(base_path, 'wages_clean.csv')
    if os.path.exists(wages_path):
        data['wages'] = pd.read_csv(wages_path)
        data['wages']['date'] = pd.to_datetime(data['wages']['date'])
    
    # Load basket data from raw
    raw_path = base_path.replace('processed', 'raw')
    basket_path = os.path.join(raw_path, 'basket_of_goods.csv')
    if os.path.exists(basket_path):
        data['basket'] = pd.read_csv(basket_path)
    
    return data


def main():
    # Load data
    data = load_data()
    
    if 'cpi' not in data:
        st.error("❌ Data not found. Please run the data processing scripts first.")
        st.stop()
    
    cpi = data['cpi']
    
    # Header
    st.markdown('<h1 class="main-header">🇬🇧 UK Cost of Living Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Exploring UK Inflation Trends, Regional Prices & Purchasing Power (1989-2024)</p>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Year range filter
    min_year = int(cpi['year'].min())
    max_year = int(cpi['year'].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_year, max_year,
        (2015, max_year)
    )
    
    # Filter data
    cpi_filtered = cpi[(cpi['year'] >= year_range[0]) & (cpi['year'] <= year_range[1])]
    
    # Quick stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    latest = cpi[cpi['date'] == cpi['date'].max()].iloc[0]
    st.sidebar.metric("Latest CPI", f"{latest['cpi_annual']:.1f}%")
    st.sidebar.metric("BOE Target", "2.0%")
    st.sidebar.metric("Gap", f"{latest['cpi_annual'] - 2:.1f}pp")
    
    # Main content - KPI Row
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Current CPI",
            f"{latest['cpi_annual']:.1f}%",
            delta=f"{latest.get('cpi_yoy_change', 0):.1f}pp vs last year" if pd.notna(latest.get('cpi_yoy_change')) else None
        )
    
    with col2:
        avg_2024 = cpi[cpi['year'] == 2024]['cpi_annual'].mean()
        st.metric("2024 Average", f"{avg_2024:.1f}%")
    
    with col3:
        peak = cpi['cpi_annual'].max()
        st.metric("Historical Peak", f"{peak:.1f}%")
    
    with col4:
        st.metric("Inflation Regime", latest.get('inflation_regime', 'N/A'))
    
    with col5:
        if 'cpih_annual' in latest and pd.notna(latest['cpih_annual']):
            st.metric("CPIH (inc. Housing)", f"{latest['cpih_annual']:.1f}%")
        else:
            st.metric("Data Points", f"{len(cpi_filtered):,}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Inflation Trends", 
        "🗺️ Regional Analysis", 
        "💷 Wages & Purchasing Power",
        "🛒 Basket of Goods",
        "📊 Data Explorer"
    ])
    
    # TAB 1: INFLATION TRENDS
    with tab1:
        st.markdown("### UK Inflation Over Time")
        
        # Main chart
        fig = go.Figure()
        
        # CPI line
        fig.add_trace(go.Scatter(
            x=cpi_filtered['date'],
            y=cpi_filtered['cpi_annual'],
            name='CPI Annual Rate',
            line=dict(color='#2563eb', width=2),
            hovertemplate='%{x|%b %Y}<br>CPI: %{y:.1f}%<extra></extra>'
        ))
        
        # CPIH line if available
        if 'cpih_annual' in cpi_filtered.columns:
            cpih_data = cpi_filtered.dropna(subset=['cpih_annual'])
            fig.add_trace(go.Scatter(
                x=cpih_data['date'],
                y=cpih_data['cpih_annual'],
                name='CPIH (inc. Housing)',
                line=dict(color='#7c3aed', width=2, dash='dot'),
                hovertemplate='%{x|%b %Y}<br>CPIH: %{y:.1f}%<extra></extra>'
            ))
        
        # BOE target line
        fig.add_hline(y=2, line_dash="dash", line_color="#dc2626", 
                      annotation_text="BOE 2% Target", annotation_position="right")
        
        fig.update_layout(
            title=f'UK Inflation Rate ({year_range[0]}-{year_range[1]})',
            xaxis_title='Date',
            yaxis_title='Annual Inflation Rate (%)',
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Inflation by Category")
            if 'food_inflation' in cpi_filtered.columns:
                cat_fig = go.Figure()
                
                for col, name, color in [
                    ('food_inflation', 'Food & Beverages', '#f59e0b'),
                    ('housing_energy_inflation', 'Housing & Energy', '#ef4444'),
                    ('cpi_annual', 'Overall CPI', '#2563eb')
                ]:
                    if col in cpi_filtered.columns:
                        subset = cpi_filtered.dropna(subset=[col])
                        cat_fig.add_trace(go.Scatter(
                            x=subset['date'], y=subset[col],
                            name=name, line=dict(color=color, width=2)
                        ))
                
                cat_fig.add_hline(y=2, line_dash="dash", line_color="gray", opacity=0.5)
                cat_fig.update_layout(height=400, showlegend=True)
                st.plotly_chart(cat_fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Monthly Heatmap")
            pivot = cpi_filtered.pivot_table(values='cpi_annual', index='month', columns='year', aggfunc='mean')
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            pivot.index = [month_names[i-1] for i in pivot.index]
            
            heat_fig = px.imshow(
                pivot, 
                color_continuous_scale='RdYlGn_r',
                aspect='auto',
                labels=dict(x="Year", y="Month", color="CPI %")
            )
            heat_fig.update_layout(height=400)
            st.plotly_chart(heat_fig, use_container_width=True)
    
    # TAB 2: REGIONAL ANALYSIS
    with tab2:
        st.markdown("### Regional Price Comparison")
        
        if 'regional' in data:
            regional = data['regional']
            latest_year = regional['year'].max()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### Overall Price Index ({latest_year})")
                reg_latest = regional[regional['year'] == latest_year].sort_values('overall_index', ascending=True)
                
                colors = ['#dc2626' if x > 100 else '#16a34a' for x in reg_latest['overall_index']]
                
                fig_reg = go.Figure(go.Bar(
                    x=reg_latest['overall_index'] - 100,
                    y=reg_latest['region'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.0f}" for x in reg_latest['overall_index']],
                    textposition='outside'
                ))
                
                fig_reg.add_vline(x=0, line_color="black", line_width=2)
                fig_reg.update_layout(
                    xaxis_title='Deviation from UK Average (Index=100)',
                    height=500,
                    showlegend=False
                )
                st.plotly_chart(fig_reg, use_container_width=True)
            
            with col2:
                st.markdown(f"#### Housing Cost Index ({latest_year})")
                reg_housing = regional[regional['year'] == latest_year].sort_values('housing_index', ascending=False)
                
                fig_house = px.bar(
                    reg_housing,
                    x='housing_index',
                    y='region',
                    orientation='h',
                    color='housing_index',
                    color_continuous_scale='Reds'
                )
                fig_house.add_vline(x=100, line_dash="dash", line_color="black")
                fig_house.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_house, use_container_width=True)
            
            # London premium over time
            st.markdown("#### London Premium Over Time")
            london_data = []
            for year in regional['year'].unique():
                year_data = regional[regional['year'] == year]
                london = year_data[year_data['region'] == 'London']['overall_index'].values
                rest = year_data[year_data['region'] != 'London']['overall_index'].mean()
                if len(london) > 0:
                    london_data.append({'year': year, 'london': london[0], 'rest_of_uk': rest})
            
            london_df = pd.DataFrame(london_data)
            london_df['premium'] = london_df['london'] - london_df['rest_of_uk']
            
            fig_london = px.line(london_df, x='year', y='premium', markers=True)
            fig_london.update_layout(
                yaxis_title='London Premium (Index Points)',
                xaxis_title='Year'
            )
            st.plotly_chart(fig_london, use_container_width=True)
        else:
            st.info("Regional data not available")
    
    # TAB 3: WAGES
    with tab3:
        st.markdown("### Wages vs Inflation")
        
        if 'wages' in data:
            wages = data['wages']
            
            # Merge with CPI
            merged = wages.merge(cpi[['date', 'cpi_annual']], on='date', how='inner')
            
            if len(merged) > 0:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_wages = go.Figure()
                    
                    fig_wages.add_trace(go.Scatter(
                        x=merged['date'], y=merged['yoy_change'],
                        name='Wage Growth', line=dict(color='#16a34a', width=2)
                    ))
                    
                    fig_wages.add_trace(go.Scatter(
                        x=merged['date'], y=merged['cpi_annual'],
                        name='Inflation', line=dict(color='#dc2626', width=2)
                    ))
                    
                    fig_wages.add_hline(y=0, line_color="gray", line_dash="dash")
                    fig_wages.update_layout(
                        title='Wage Growth vs Inflation',
                        yaxis_title='Percentage (%)',
                        height=400
                    )
                    st.plotly_chart(fig_wages, use_container_width=True)
                
                with col2:
                    st.markdown("#### Latest Wages")
                    latest_wage = wages[wages['date'] == wages['date'].max()].iloc[0]
                    st.metric("Avg Weekly Earnings", f"£{latest_wage['avg_weekly_earnings']:.0f}")
                    st.metric("Private Sector", f"£{latest_wage['private_sector']:.0f}")
                    st.metric("Public Sector", f"£{latest_wage['public_sector']:.0f}")
                
                # Real wage calculator
                st.markdown("---")
                st.markdown("#### 💰 Salary Calculator")
                st.markdown("See how inflation affects your purchasing power")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    salary = st.number_input("Enter your annual salary (£)", min_value=10000, max_value=500000, value=35000, step=1000)
                with col2:
                    base_year = st.selectbox("Compare from year", options=[2020, 2021, 2022, 2023], index=0)
                
                # Calculate cumulative inflation
                cpi_since = cpi[cpi['year'] >= base_year]['cpi_annual'].mean() * (2024 - base_year)
                real_value = salary / (1 + cpi_since/100)
                required_raise = salary * (cpi_since/100)
                
                with col3:
                    st.metric(f"Real Value (in {base_year} £)", f"£{real_value:,.0f}")
                
                st.info(f"💡 To maintain the same purchasing power as {base_year}, you would need a raise of approximately **£{required_raise:,.0f}** ({cpi_since:.1f}% cumulative inflation)")
        else:
            st.info("Wages data not available")
    
    # TAB 4: BASKET OF GOODS
    with tab4:
        st.markdown("### Basket of Goods Price Changes")
        
        if 'basket' in data:
            basket = data['basket']
            
            # Price comparison
            pivot = basket.pivot_table(values='average_price', index='item', columns='year')
            
            if 2020 in pivot.columns and 2024 in pivot.columns:
                pivot['change'] = ((pivot[2024] - pivot[2020]) / pivot[2020] * 100).round(1)
                pivot = pivot.sort_values('change', ascending=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    colors = ['#dc2626' if x > 20 else '#f59e0b' if x > 10 else '#16a34a' for x in pivot['change']]
                    
                    fig_basket = go.Figure(go.Bar(
                        x=pivot['change'],
                        y=pivot.index,
                        orientation='h',
                        marker_color=colors,
                        text=[f"{x:.0f}%" for x in pivot['change']],
                        textposition='outside'
                    ))
                    
                    fig_basket.update_layout(
                        title='Price Changes: 2020 vs 2024',
                        xaxis_title='Price Change (%)',
                        height=600
                    )
                    st.plotly_chart(fig_basket, use_container_width=True)
                
                with col2:
                    st.markdown("#### Price Comparison")
                    item_select = st.selectbox("Select item", options=pivot.index.tolist())
                    
                    if item_select:
                        price_2020 = pivot.loc[item_select, 2020]
                        price_2024 = pivot.loc[item_select, 2024]
                        change = pivot.loc[item_select, 'change']
                        
                        st.metric("2020 Price", f"£{price_2020:.2f}")
                        st.metric("2024 Price", f"£{price_2024:.2f}", delta=f"{change:.1f}%")
            
            # Category breakdown
            st.markdown("#### Price Trends by Category")
            cat_avg = basket.groupby(['year', 'category'])['average_price'].mean().reset_index()
            
            fig_cat = px.line(cat_avg, x='year', y='average_price', color='category', markers=True)
            fig_cat.update_layout(yaxis_title='Average Price (£)', height=400)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Basket of goods data not available")
    
    # TAB 5: DATA EXPLORER
    with tab5:
        st.markdown("### Data Explorer")
        
        dataset = st.selectbox("Select Dataset", options=['CPI Data', 'Regional Prices', 'Wages', 'Basket of Goods'])
        
        if dataset == 'CPI Data':
            df_display = cpi_filtered.copy()
        elif dataset == 'Regional Prices' and 'regional' in data:
            df_display = data['regional']
        elif dataset == 'Wages' and 'wages' in data:
            df_display = data['wages']
        elif dataset == 'Basket of Goods' and 'basket' in data:
            df_display = data['basket']
        else:
            df_display = pd.DataFrame()
        
        if len(df_display) > 0:
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Download button
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{dataset.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
            
            st.markdown(f"**Total Records:** {len(df_display):,}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 1rem;'>
        <p><strong>UK Cost of Living Analysis</strong> | Data Source: ONS (Office for National Statistics)</p>
        <p>Built by <a href='https://mounishmesa.github.io' target='_blank'>Mounish Mesa</a> | 
        <a href='https://linkedin.com/in/mounish-jm' target='_blank'>LinkedIn</a> | 
        <a href='https://github.com/mounishmesa' target='_blank'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

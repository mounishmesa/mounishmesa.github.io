"""
FTSE 100 Stock Analysis Dashboard
Interactive Streamlit dashboard for UK stock market analysis
Author: Mounish Mesa
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="FTSE 100 Analysis | Mounish Mesa",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .positive {
        color: #00c853;
    }
    .negative {
        color: #ff5252;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load stock data"""
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(current_dir, 'data/ftse_stock_data_raw.csv'))
    df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
    return df

@st.cache_data
def load_performance():
    """Load performance metrics"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return pd.read_csv(os.path.join(current_dir, 'outputs/stock_performance.csv'))

def format_return(value):
    """Format return with color"""
    if value > 0:
        return f"🟢 +{value:.2f}%"
    else:
        return f"🔴 {value:.2f}%"

def main():
    # Load data
    df = load_data()
    perf_df = load_performance()
    
    # Separate stocks and index
    stocks_perf = perf_df[perf_df['Sector'] != 'Index']
    ftse_perf = perf_df[perf_df['Sector'] == 'Index'].iloc[0]
    
    # Header
    st.markdown('<p class="main-header">📈 FTSE 100 Stock Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive analysis of UK\'s top companies | Data updated: ' + 
                df['Date'].max().strftime('%d %B %Y') + '</p>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Sector filter
    sectors = ['All Sectors'] + sorted(stocks_perf['Sector'].unique().tolist())
    selected_sector = st.sidebar.selectbox("Select Sector", sectors)
    
    # Time period filter
    time_period = st.sidebar.selectbox(
        "Return Period",
        ['1 Month', '3 Months', '6 Months', '1 Year', 'Total'],
        index=3
    )
    
    period_map = {
        '1 Month': 'Return_1M',
        '3 Months': 'Return_3M',
        '6 Months': 'Return_6M',
        '1 Year': 'Return_1Y',
        'Total': 'Return_Total'
    }
    return_col = period_map[time_period]
    
    # Filter data
    if selected_sector != 'All Sectors':
        filtered_perf = stocks_perf[stocks_perf['Sector'] == selected_sector]
    else:
        filtered_perf = stocks_perf
    
    # KPI Row
    st.markdown("### 📊 Market Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "FTSE 100 Index",
            f"{ftse_perf['Current_Price']:,.0f}",
            f"{ftse_perf['Return_1Y']:+.2f}% (1Y)"
        )
    
    with col2:
        avg_return = filtered_perf[return_col].mean()
        st.metric(
            f"Avg {time_period} Return",
            f"{avg_return:+.2f}%",
            f"{len(filtered_perf)} stocks"
        )
    
    with col3:
        top_stock = filtered_perf.loc[filtered_perf[return_col].idxmax()]
        st.metric(
            "Top Performer",
            top_stock['Company'],
            f"{top_stock[return_col]:+.2f}%"
        )
    
    with col4:
        bottom_stock = filtered_perf.loc[filtered_perf[return_col].idxmin()]
        st.metric(
            "Bottom Performer",
            bottom_stock['Company'],
            f"{bottom_stock[return_col]:+.2f}%"
        )
    
    with col5:
        avg_vol = filtered_perf['Volatility'].mean()
        st.metric(
            "Avg Volatility",
            f"{avg_vol:.2f}",
            "Daily Std Dev"
        )
    
    st.markdown("---")
    
    # Main charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Stock Performance Rankings")
        
        # Sort by selected return period
        chart_data = filtered_perf.sort_values(return_col, ascending=True).tail(15)
        
        fig = go.Figure()
        
        colors = ['#00c853' if x > 0 else '#ff5252' for x in chart_data[return_col]]
        
        fig.add_trace(go.Bar(
            x=chart_data[return_col],
            y=chart_data['Company'],
            orientation='h',
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in chart_data[return_col]],
            textposition='outside'
        ))
        
        fig.update_layout(
            height=500,
            xaxis_title=f"{time_period} Return (%)",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=0, r=50, t=20, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Sector Performance")
        
        # Calculate sector averages
        sector_perf = stocks_perf.groupby('Sector').agg({
            'Return_1M': 'mean',
            'Return_3M': 'mean',
            'Return_6M': 'mean',
            'Return_1Y': 'mean',
            'Volatility': 'mean'
        }).round(2).reset_index()
        
        sector_perf = sector_perf.sort_values(return_col, ascending=False)
        
        fig = px.bar(
            sector_perf,
            x='Sector',
            y=return_col,
            color=return_col,
            color_continuous_scale=['#ff5252', '#ffeb3b', '#00c853'],
            text=[f"{x:+.1f}%" for x in sector_perf[return_col]]
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title=f"{time_period} Return (%)",
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=20, b=40)
        )
        fig.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📉 Risk vs Return Analysis")
        
        fig = px.scatter(
            filtered_perf,
            x='Volatility',
            y=return_col,
            color='Sector',
            size='Avg_Volume',
            hover_name='Company',
            hover_data={
                'Volatility': ':.2f',
                return_col: ':.2f',
                'Sector': True,
                'Avg_Volume': ':,.0f'
            }
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=filtered_perf['Volatility'].mean(), line_dash="dash", line_color="gray")
        
        fig.update_layout(
            height=450,
            xaxis_title="Volatility (Risk)",
            yaxis_title=f"{time_period} Return (%)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Stock Price Trend")
        
        # Stock selector
        stock_options = df[df['Sector'] != 'Index']['Company'].unique().tolist()
        selected_stock = st.selectbox("Select Stock", sorted(stock_options), index=0)
        
        stock_data = df[df['Company'] == selected_stock].sort_values('Date')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1a73e8', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['MA_50'],
            mode='lines',
            name='50-Day MA',
            line=dict(color='#ea4335', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['MA_200'],
            mode='lines',
            name='200-Day MA',
            line=dict(color='#34a853', width=1, dash='dot')
        ))
        
        fig.update_layout(
            height=400,
            xaxis_title="",
            yaxis_title="Price (£)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # FTSE 100 Index trend
    st.markdown("### 📈 FTSE 100 Index Performance")
    
    ftse_data = df[df['Ticker'] == '^FTSE'].sort_values('Date')
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1,
                        row_heights=[0.7, 0.3])
    
    # Price chart
    fig.add_trace(
        go.Scatter(x=ftse_data['Date'], y=ftse_data['Close'],
                  mode='lines', name='FTSE 100',
                  line=dict(color='#1a73e8', width=2)),
        row=1, col=1
    )
    
    # Volume chart
    fig.add_trace(
        go.Bar(x=ftse_data['Date'], y=ftse_data['Volume'],
              name='Volume', marker_color='#90caf9'),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        hovermode='x unified'
    )
    fig.update_yaxes(title_text="Index Value", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Data table
    st.markdown("### 📋 Stock Data Table")
    
    display_cols = ['Company', 'Sector', 'Current_Price', 'Return_1M', 'Return_3M', 
                   'Return_6M', 'Return_1Y', 'Volatility']
    
    display_df = filtered_perf[display_cols].copy()
    display_df.columns = ['Company', 'Sector', 'Price (£)', '1M Return', '3M Return', 
                         '6M Return', '1Y Return', 'Volatility']
    
    # Format columns
    for col in ['1M Return', '3M Return', '6M Return', '1Y Return']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.2f}%")
    
    display_df['Price (£)'] = display_df['Price (£)'].apply(lambda x: f"£{x:,.2f}")
    display_df['Volatility'] = display_df['Volatility'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        display_df.sort_values('Company'),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = filtered_perf.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name=f"ftse100_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Built by <strong>Mounish Mesa</strong> | Data Source: Yahoo Finance</p>
        <p>
            <a href='https://linkedin.com/in/mounish-jm' target='_blank'>LinkedIn</a> | 
            <a href='https://github.com/mounishmesa' target='_blank'>GitHub</a> | 
            <a href='https://mounishmesa.github.io' target='_blank'>Portfolio</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

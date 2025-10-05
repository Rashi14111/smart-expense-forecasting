import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import io
import base64
from backend.data_loader import load_excel_data, preprocess_data, calculate_comprehensive_metrics
from backend.forecast_model import forecast_expenses, calculate_seasonal_trends, advanced_ml_analysis
from backend.pdf_generator import generate_comprehensive_pdf

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Smart Expense Forecasting Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= ATTRACTIVE GRADIENT CSS =================
st.markdown("""
<style>
    /* Main Background with Beautiful Gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Header Styling */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 40px;
        margin: 25px 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        text-align: center;
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
    }
    
    /* Premium KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px 20px;
        margin: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        text-align: center;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .kpi-card:hover::after {
        left: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .kpi-value {
        font-size: 32px;
        font-weight: 900;
        margin: 15px 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .kpi-label {
        font-size: 14px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-detail {
        font-size: 12px;
        color: #7f8c8d;
        line-height: 1.4;
        margin-top: 8px;
    }
    
    /* Enhanced Section Headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 20px;
        margin: 30px 0;
        font-weight: 800;
        font-size: 22px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        gap: 15px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Premium Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 18px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border-left: 6px solid;
        border-image: linear-gradient(135deg, #667eea, #764ba2) 1;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .insight-card:hover::before {
        opacity: 1;
    }
    
    .insight-card:hover {
        transform: translateY(-5px) translateX(5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.18);
    }
    
    .insight-title {
        font-weight: 800;
        color: #2c3e50;
        margin-bottom: 12px;
        font-size: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .insight-content {
        font-size: 15px;
        color: #555;
        line-height: 1.7;
        position: relative;
        z-index: 2;
    }
    
    /* Premium Chart Containers */
    .chart-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
        position: relative;
        backdrop-filter: blur(10px);
    }
    
    .chart-explanation {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #3498db;
        font-size: 14px;
        color: #555;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Enhanced Simple Explanation */
    .simple-explanation {
        background: linear-gradient(135deg, #e8f4fd 0%, #d4edfa 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid #b3d9f7;
        font-size: 14px;
        color: #2c3e50;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(179, 217, 247, 0.3);
    }
    
    /* Premium Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 700;
        transition: all 0.4s ease;
        width: 100%;
        font-size: 15px;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
    }
    
    /* Enhanced Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 8px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.8);
        border-radius: 12px;
        padding: 18px 30px;
        font-weight: 700;
        font-size: 15px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.9);
        border-color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        border-color: transparent;
    }
    
    /* Analysis Depth Badges */
    .analysis-badge {
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 13px;
        margin: 8px 0;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .quick-badge { 
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1976d2; 
        border: 2px solid #1976d2; 
    }
    
    .detailed-badge { 
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        color: #7b1fa2; 
        border: 2px solid #7b1fa2; 
    }
    
    .strategic-badge { 
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        color: #388e3c; 
        border: 2px solid #388e3c; 
    }
    
    .analysis-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Enhanced Tooltip */
    .tooltip-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffeaa7;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        font-size: 14px;
        color: #856404;
        box-shadow: 0 4px 15px rgba(255, 234, 167, 0.3);
    }
    
    /* Progress Bars */
    .progress-container {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        height: 20px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        margin: 5px 0;
        position: relative;
        overflow: hidden;
    }
    
    .progress-text {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: white;
        font-weight: 700;
        font-size: 12px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* Metric Value Enhancement */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Download Button Special */
    .download-btn {
        background: linear-gradient(135deg, #00b09b, #96c93d) !important;
        box-shadow: 0 6px 20px rgba(0, 176, 155, 0.4) !important;
    }
    
    .download-btn:hover {
        background: linear-gradient(135deg, #96c93d, #00b09b) !important;
        box-shadow: 0 8px 25px rgba(0, 176, 155, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= INITIALIZATION =================
def initialize_session_state():
    """Initialize session state variables safely"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_category' not in st.session_state:
        st.session_state.current_category = None
    if 'forecast_periods' not in st.session_state:
        st.session_state.forecast_periods = 6
    if 'show_forecast_help' not in st.session_state:
        st.session_state.show_forecast_help = False
    if 'analysis_depth' not in st.session_state:
        st.session_state.analysis_depth = "Detailed Analysis"

# ================= PREMIUM SIDEBAR =================
def render_sidebar():
    """Render the premium sidebar with enhanced UI"""
    with st.sidebar:
        # Premium Header
        st.markdown("""
        <div style='text-align: center; padding: 25px 0; background: linear-gradient(135deg, #667eea, #764ba2); 
                    border-radius: 20px; margin-bottom: 25px; color: white; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);'>
            <h2 style='color: white; margin-bottom: 10px; font-size: 1.6em;'>🎯 CONTROL CENTER</h2>
            <p style='color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500;'>Smart Expense Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Data Upload Section
        st.markdown("### 📁 DATA MANAGEMENT")
        uploaded_file = st.file_uploader(
            "**Upload Your Expense File**", 
            type=['xlsx'],
            help="Upload your Excel file with expense data for comprehensive analysis",
            key="file_uploader"
        )
        
        if uploaded_file:
            with st.spinner("🔄 Analyzing your financial data..."):
                data = load_excel_data(uploaded_file)
                st.session_state.data_loaded = True
                st.session_state.data = data
                st.success("✅ Data loaded successfully!")
        else:
            # Use default file
            try:
                with st.spinner("🔄 Loading sample dataset..."):
                    data = load_excel_data("Smart_Expense_Forecasting_Dummy (2).xlsx")
                    st.session_state.data_loaded = True
                    st.session_state.data = data
                    st.info("📊 Using sample data. Upload your own file for personalized insights!")
            except Exception as e:
                st.error("❌ Please upload an Excel file to begin analysis")
                return None
                
        if not st.session_state.data_loaded:
            return None
            
        data = st.session_state.data
        
        st.markdown("---")
        
        # Analysis Configuration
        st.markdown("### ⚙️ ANALYSIS CONFIGURATION")
        
        # Category Selection
        category = st.selectbox(
            "**Select Expense Category**",
            options=list(data.keys()),
            index=0,
            help="Choose which expense category to analyze in depth",
            key="category_selector"
        )
        
        # Forecast Settings
        st.markdown("**🔮 FORECAST SETTINGS**")
        forecast_periods = st.slider(
            "**Months to Forecast:**",
            min_value=3,
            max_value=12,
            value=6,
            help="Select how many future months you want to predict",
            key="forecast_slider"
        )
        
        st.session_state.forecast_periods = forecast_periods
        
        # Analysis Depth with Enhanced UI
        st.markdown("**🎯 ANALYSIS DEPTH**")
        
        analysis_depth = st.radio(
            "Choose Analysis Intensity:",
            ["Quick Overview", "Detailed Analysis", "Strategic Planning"],
            index=1,
            help="""
            **Quick Overview**: High-level metrics and key trends
            **Detailed Analysis**: Comprehensive charts and insights  
            **Strategic Planning**: Advanced forecasting and actionable recommendations
            """,
            key="analysis_depth_radio"
        )
        
        # Store analysis depth in session state
        st.session_state.analysis_depth = analysis_depth
        
        # Enhanced depth explanations with progress indicators
        depth_info = {
            "Quick Overview": {"desc": "Perfect for executive summary", "progress": 30},
            "Detailed Analysis": {"desc": "Ideal for comprehensive review", "progress": 70},
            "Strategic Planning": {"desc": "Best for long-term planning", "progress": 100}
        }
        
        current_depth = depth_info[analysis_depth]
        
        st.markdown(f"""
        <div class='analysis-badge {analysis_depth.lower().replace(" ", "-")}-badge'>
            {analysis_depth.upper()} MODE
        </div>
        <div class='tooltip-box'>
            💡 {current_depth['desc']}
        </div>
        <div class='progress-container'>
            <div>Analysis Intensity:</div>
            <div class='progress-bar' style='width: {current_depth['progress']}%'>
                <div class='progress-text'>{current_depth['progress']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### 🚀 QUICK ACTIONS")
        
        # Download PDF Report
        if st.button("📊 Generate PDF Report", use_container_width=True, key="pdf_report_btn"):
            st.session_state.generate_pdf = True
            
        if st.button("🔄 Reset Analysis", use_container_width=True, key="reset_btn"):
            for key in list(st.session_state.keys()):
                if key not in ['data_loaded', 'data']:
                    del st.session_state[key]
            st.rerun()
        
        # Quick Tips
        with st.expander("💡 Expert Tips", expanded=False):
            st.markdown("""
            **Pro Insights:**
            • Use Strategic Planning for budget preparation
            • Monitor efficiency scores monthly
            • Download PDF reports for meetings
            • Compare categories for optimization
            
            **Efficiency Guide:**
            • 8-10/10: Excellent control
            • 6-7/10: Good management  
            • 4-5/10: Needs improvement
            • 0-3/10: Immediate attention
            """)
        
        return category, data, analysis_depth

# ================= PREMIUM HEADER =================
def render_header():
    """Render the premium header with enhanced design"""
    st.markdown("""
    <div class='main-header'>
        <div style='text-align: center;'>
            <h1 style='color: #2c3e50; margin-bottom: 20px; font-size: 3em; font-weight: 900; text-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                📊 SMART EXPENSE FORECASTER
            </h1>
            <p style='color: #7f8c8d; font-size: 1.3em; font-weight: 600; line-height: 1.6; margin-bottom: 25px;'>
                Advanced Financial Intelligence • Predictive Analytics • Strategic Insights
            </p>
            <div style='display: flex; justify-content: center; gap: 20px; margin-top: 25px; flex-wrap: wrap;'>
                <span style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; border-radius: 25px; font-size: 1em; font-weight: 700; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);'>
                    🤖 AI-POWERED INSIGHTS
                </span>
                <span style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; border-radius: 25px; font-size: 1em; font-weight: 700; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);'>
                    📈 REAL-TIME ANALYTICS
                </span>
                <span style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; border-radius: 25px; font-size: 1em; font-weight: 700; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);'>
                    💡 STRATEGIC PLANNING
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= ENHANCED KPI DASHBOARD =================
def render_kpi_dashboard(metrics, category):
    """Render enhanced KPI dashboard with better efficiency calculation"""
    st.markdown(f"<div class='section-header'>📈 {category.upper()} - PERFORMANCE DASHBOARD</div>", unsafe_allow_html=True)
    
    # Enhanced efficiency calculation explanation
    st.markdown(f"""
    <div class='simple-explanation'>
    <strong>🎯 Efficiency Score Explained:</strong> Your score of {metrics['efficiency_score']}/10 is calculated based on spending consistency, 
    growth patterns, and budget adherence. Higher scores indicate better financial control and predictability.
    </div>
    """, unsafe_allow_html=True)
    
    # Create enhanced 2x3 grid for KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>💰 TOTAL EXPENDITURE</div>
            <div class='kpi-value'>₹{metrics['total_spent']:,.0f}</div>
            <div class='kpi-detail'>
                📅 Period: {metrics['period_start'].strftime('%b %Y')} - {metrics['period_end'].strftime('%b %Y')}<br>
                📊 {metrics['transaction_count']} transactions analyzed<br>
                📈 {metrics['analysis_period']} months of data
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>📊 MONTHLY AVERAGE</div>
            <div class='kpi-value'>₹{metrics['avg_monthly']:,.0f}</div>
            <div class='kpi-detail'>
                🎯 Budget planning baseline<br>
                💡 Consistent spending indicator<br>
                📐 Performance benchmark
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        efficiency_color = "#27ae60" if metrics['efficiency_score'] >= 8 else "#f39c12" if metrics['efficiency_score'] >= 6 else "#e74c3c"
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>⬆️ PEAK SPENDING</div>
            <div class='kpi-value'>₹{metrics['highest_month_amount']:,.0f}</div>
            <div class='kpi-detail'>
                📅 {metrics['highest_month_name']}<br>
                🔍 {metrics['highest_month_percentage']:.1f}% of total<br>
                💡 Identify peak patterns
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>📈 GROWTH TREND</div>
            <div class='kpi-value' style='color: {efficiency_color};'>{metrics['growth_rate']:+.1f}%</div>
            <div class='kpi-detail'>
                {metrics['trend_icon']} {metrics['trend_description']}<br>
                📊 {metrics['analysis_period']} month trend<br>
                🎯 Strategic planning indicator
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>⬇️ LOWEST SPENDING</div>
            <div class='kpi-value'>₹{metrics['lowest_month_amount']:,.0f}</div>
            <div class='kpi-detail'>
                📅 {metrics['lowest_month_name']}<br>
                💰 Cost efficiency reference<br>
                🔍 Optimization opportunity
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        efficiency_bg = "#27ae60" if metrics['efficiency_score'] >= 8 else "#f39c12" if metrics['efficiency_score'] >= 6 else "#e74c3c"
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🎯 EFFICIENCY SCORE</div>
            <div class='kpi-value' style='color: {efficiency_bg};'>{metrics['efficiency_score']}/10</div>
            <div class='kpi-detail'>
                📐 Based on {metrics['variance']*100:.1f}% variance<br>
                {metrics['efficiency_comment']}<br>
                💡 Higher = Better control
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Efficiency improvement tips
    if metrics['efficiency_score'] < 7:
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>🚀 IMPROVE YOUR EFFICIENCY SCORE</div>
            <div class='insight-content'>
            Your current efficiency score is {metrics['efficiency_score']}/10. Here's how to improve:
            • <strong>Reduce monthly variance</strong> (currently {metrics['variance']*100:.1f}%)<br>
            • <strong>Stabilize growth rate</strong> (currently {metrics['growth_rate']:+.1f}%)<br>
            • <strong>Implement budget controls</strong> for consistent spending<br>
            • <strong>Monitor weekly</strong> instead of monthly<br>
            Target: Achieve 8+ score for excellent financial management
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================= ENHANCED FORECAST CHART =================
def render_forecast_chart(monthly_df, forecast_df, category, metrics):
    """Render enhanced forecast chart with better insights"""
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    
    st.subheader("🔮 INTELLIGENT EXPENSE FORECAST")
    
    # Enhanced explanation
    st.markdown(f"""
    <div class='simple-explanation'>
    <strong>💡 Strategic Forecasting:</strong> This AI-powered forecast predicts your next {len(forecast_df)} months of expenses 
    based on {metrics['analysis_period']} months of historical data. Use these insights for proactive budget planning and resource allocation.
    </div>
    """, unsafe_allow_html=True)
    
    # Create enhanced forecast chart
    fig = go.Figure()
    
    # Historical data with enhanced styling
    fig.add_trace(go.Scatter(
        x=monthly_df['YearMonth'],
        y=monthly_df['Total_Amount'],
        mode='lines+markers',
        name='ACTUAL SPENDING',
        line=dict(color='#3498db', width=5, shape='spline'),
        marker=dict(size=10, color='#3498db', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x|%B %Y}</b><br>Actual: ₹%{y:,.0f}<extra></extra>'
    ))
    
    # Forecast data with enhanced styling
    if not forecast_df.empty:
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Forecast'],
            mode='lines+markers',
            name='AI PREDICTION',
            line=dict(color='#e74c3c', width=5, dash='dash', shape='spline'),
            marker=dict(size=8, color='#e74c3c', symbol='diamond'),
            hovertemplate='<b>%{x|%B %Y}</b><br>Forecast: ₹%{y:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="<b>TIMELINE</b>",
        yaxis_title="<b>AMOUNT (₹)</b>",
        showlegend=True,
        hovermode='x unified',
        font=dict(size=13, family='Arial'),
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced forecast insights
    if not forecast_df.empty:
        forecast_growth = ((forecast_df['Forecast'].iloc[-1] - forecast_df['Forecast'].iloc[0]) / forecast_df['Forecast'].iloc[0]) * 100
        peak_forecast_month = forecast_df.loc[forecast_df['Forecast'].idxmax(), 'Date']
        total_forecast = forecast_df['Forecast'].sum()
        
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>🎯 FORECAST INTELLIGENCE</div>
            <div class='insight-content'>
            • <strong>Predicted Trend:</strong> {forecast_growth:+.1f}% over {len(forecast_df)} months<br>
            • <strong>Peak Forecast:</strong> {peak_forecast_month.strftime('%B %Y')} (₹{forecast_df['Forecast'].max():,.0f})<br>
            • <strong>Total Forecasted:</strong> ₹{total_forecast:,.0f} over {len(forecast_df)} months<br>
            • <strong>Budget Recommendation:</strong> {"Increase allocation by 10-15%" if forecast_growth > 0 else "Maintain current levels"}<br>
            • <strong>Confidence Level:</strong> High (based on {metrics['analysis_period']} months historical data)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================= ENHANCED EXPENSE BREAKDOWN =================
def render_expense_breakdown(df, total_spent, category):
    """Render enhanced expense breakdown with better insights"""
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    
    st.subheader("📊 SMART EXPENSE CATEGORIZATION")
    
    st.markdown("""
    <div class='simple-explanation'>
    <strong>💡 Category Intelligence:</strong> This analysis reveals your spending distribution across different categories. 
    Identify optimization opportunities and reallocate resources strategically for maximum impact.
    </div>
    """, unsafe_allow_html=True)
    
    if "Expense Head" in df.columns:
        # Enhanced distribution calculation
        expense_dist = df.groupby('Expense Head').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        expense_dist.columns = ['Total_Amount', 'Transaction_Count', 'Average_Amount']
        expense_dist = expense_dist.sort_values('Total_Amount', ascending=False)
        expense_dist['Percentage'] = (expense_dist['Total_Amount'] / total_spent * 100).round(1)
        
        # Enhanced visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enhanced pie chart
            fig = px.pie(
                values=expense_dist['Total_Amount'],
                names=expense_dist.index,
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Bold,
                title=f"<b>{category} - Spending Distribution</b>"
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Total: ₹%{value:,.0f}<br>%{percent} of total<extra></extra>",
                textfont=dict(size=12)
            )
            fig.update_layout(
                height=500,
                showlegend=False,
                margin=dict(l=30, r=30, t=60, b=30),
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏆 TOP PERFORMING CATEGORIES")
            
            for i, (category_name, row) in enumerate(expense_dist.head(6).iterrows()):
                efficiency_color = "#27ae60" if row['Percentage'] < 30 else "#f39c12" if row['Percentage'] < 50 else "#e74c3c"
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 15px; border-radius: 12px; margin: 8px 0; border-left: 5px solid {efficiency_color}'>
                    <div style='font-weight: 800; color: #2c3e50; font-size: 14px;'>{i+1}. {category_name}</div>
                    <div style='font-size: 0.85em; color: #7f8c8d; line-height: 1.4; margin-top: 5px;'>
                    💰 <strong>₹{row['Total_Amount']:,.0f}</strong> ({row['Percentage']}%)<br>
                    📊 {int(row['Transaction_Count'])} transactions<br>
                    📈 Avg: ₹{row['Average_Amount']:,.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced optimization strategy
            top_category = expense_dist.index[0]
            top_percentage = expense_dist['Percentage'].iloc[0]
            
            if top_percentage > 40:
                suggestion = f"🚨 **CRITICAL FOCUS**: {top_category} consumes {top_percentage}% of budget. Immediate cost optimization required."
            elif top_percentage > 25:
                suggestion = f"📊 **STRATEGIC REVIEW**: {top_category} at {top_percentage}% warrants detailed analysis for savings."
            else:
                suggestion = "✅ **BALANCED ALLOCATION**: Spending distribution is optimal. Focus on incremental improvements."
                
            st.markdown(f"""
            <div class='insight-card' style='margin-top: 20px;'>
                <div class='insight-title'>💡 OPTIMIZATION STRATEGY</div>
                <div class='insight-content'>{suggestion}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================= ENHANCED MONTHLY PATTERNS =================
def render_monthly_patterns(monthly_df, category):
    """Render enhanced monthly patterns with better analysis"""
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    
    st.subheader("📅 ADVANCED MONTHLY PATTERN ANALYSIS")
    
    st.markdown("""
    <div class='simple-explanation'>
    <strong>💡 Pattern Intelligence:</strong> Discover seasonal trends, growth patterns, and spending volatility. 
    Use these insights for strategic planning, cash flow management, and budget optimization.
    </div>
    """, unsafe_allow_html=True)
    
    # Create comprehensive monthly analysis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('<b>Monthly Spending & Trend Analysis</b>', '<b>Monthly Growth Patterns</b>'),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    # Enhanced bar chart with trend line
    fig.add_trace(go.Bar(
        x=monthly_df['YearMonth'],
        y=monthly_df['Total_Amount'],
        name='Monthly Spend',
        marker_color='#3498db',
        opacity=0.8,
        hovertemplate='<b>%{x|%B %Y}</b><br>Amount: ₹%{y:,.0f}<extra></extra>'
    ), row=1, col=1)
    
    # Enhanced trend line
    if len(monthly_df) > 1:
        z = np.polyfit(range(len(monthly_df)), monthly_df['Total_Amount'], 1)
        p = np.poly1d(z)
        trend_line = p(range(len(monthly_df)))
        
        fig.add_trace(go.Scatter(
            x=monthly_df['YearMonth'],
            y=trend_line,
            name='Trend Line',
            line=dict(color='#e74c3c', width=4, dash='dot'),
            mode='lines',
            hovertemplate='Trend: ₹%{y:,.0f}<extra></extra>'
        ), row=1, col=1)
    
    # Enhanced growth analysis
    if len(monthly_df) > 1:
        monthly_df['MoM_Growth'] = monthly_df['Total_Amount'].pct_change() * 100
        
        colors = ['#27ae60' if x >= 0 else '#e74c3c' for x in monthly_df['MoM_Growth'].iloc[1:]]
        
        fig.add_trace(go.Bar(
            x=monthly_df['YearMonth'].iloc[1:],
            y=monthly_df['MoM_Growth'].iloc[1:],
            name='Monthly Growth %',
            marker_color=colors,
            opacity=0.7,
            hovertemplate='<b>%{x|%B %Y}</b><br>Growth: %{y:.1f}%<extra></extra>'
        ), row=2, col=1)
    
    fig.update_layout(
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        hovermode='x unified',
        font=dict(size=12)
    )
    
    fig.update_yaxes(title_text="<b>Amount (₹)</b>", row=1, col=1)
    fig.update_yaxes(title_text="<b>Growth (%)</b>", row=2, col=1)
    fig.update_xaxes(title_text="<b>Timeline</b>", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced pattern insights
    seasonal_insight = calculate_seasonal_trends(monthly_df)
    volatility = monthly_df['Total_Amount'].std() / monthly_df['Total_Amount'].mean() if monthly_df['Total_Amount'].mean() > 0 else 0
    
    st.markdown(f"""
    <div class='insight-card'>
        <div class='insight-title'>🎯 PATTERN INTELLIGENCE</div>
        <div class='insight-content'>
        • <strong>Seasonal Analysis:</strong> {seasonal_insight}<br>
        • <strong>Volatility Score:</strong> {volatility:.1%} monthly variation<br>
        • <strong>Data Quality:</strong> {len(monthly_df)} months analyzed<br>
        • <strong>Stability Rating:</strong> {'Excellent' if volatility < 0.2 else 'Good' if volatility < 0.4 else 'Needs Attention'}<br>
        • <strong>Planning Confidence:</strong> {'High' if volatility < 0.3 else 'Medium' if volatility < 0.6 else 'Low'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================= ENHANCED ACTIONABLE INSIGHTS =================
def render_actionable_insights(metrics, df, category):
    """Render enhanced actionable insights"""
    st.markdown("<div class='section-header'>💡 STRATEGIC ACTION PLAN</div>", unsafe_allow_html=True)
    
    # Create enhanced tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Immediate Actions", "📈 Growth Strategy", "🚀 90-Day Plan"])
    
    with tab1:
        st.markdown("### Priority Recommendations")
        
        # Efficiency-based recommendations
        if metrics['efficiency_score'] < 6:
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>⚠️ EFFICIENCY OPTIMIZATION</div>
                <div class='insight-content'>
                Your efficiency score of {metrics['efficiency_score']}/10 indicates improvement opportunities:
                • <strong>Implement weekly budget reviews</strong><br>
                • <strong>Set variance threshold at 20%</strong><br>
                • <strong>Create spending alerts for peaks</strong><br>
                • <strong>Establish monthly budget of ₹{metrics['avg_monthly'] * 1.1:,.0f}</strong><br>
                <em>Target: Achieve 8+ efficiency score in next quarter</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>✅ EXCELLENT PERFORMANCE</div>
                <div class='insight-content'>
                Your efficiency score of {metrics['efficiency_score']}/10 demonstrates strong financial control:
                • <strong>Maintain current review processes</strong><br>
                • <strong>Explore advanced optimization</strong><br>
                • <strong>Set stretch efficiency targets</strong><br>
                • <strong>Share best practices across organization</strong><br>
                <em>Goal: Sustain 8+ efficiency score consistently</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Growth-based recommendations
        if metrics['growth_rate'] > 15:
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>📈 RAPID GROWTH MANAGEMENT</div>
                <div class='insight-content'>
                Your {metrics['growth_rate']:+.1f}% growth rate requires strategic management:
                • <strong>Implement growth controls</strong><br>
                • <strong>Review supplier contracts</strong><br>
                • <strong>Optimize high-growth categories</strong><br>
                • <strong>Allocate 15% budget buffer</strong><br>
                <em>Focus: Sustainable growth at 5-10% annually</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Strategic Growth Initiatives")
        
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>💰 SMART BUDGET STRATEGY</div>
            <div class='insight-content'>
            • <strong>Optimal Allocation:</strong> ₹{metrics['avg_monthly']:,.0f} monthly base + 15% contingency<br>
            • <strong>Peak Preparation:</strong> Reserve ₹{metrics['highest_month_amount']:,.0f} for high-spend months<br>
            • <strong>Growth Buffer:</strong> Allocate additional 10% for expansion<br>
            • <strong>Efficiency Target:</strong> Achieve {min(10, metrics['efficiency_score'] + 2)}/10 next quarter<br>
            • <strong>Variance Control:</strong> Reduce from {metrics['variance']*100:.1f}% to under 25%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if "Expense Head" in df.columns:
            top_category = df.groupby('Expense Head')['Amount'].sum().idxmax()
            top_amount = df.groupby('Expense Head')['Amount'].sum().max()
            top_percentage = (top_amount / metrics['total_spent'] * 100)
            
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>🎯 CATEGORY OPTIMIZATION</div>
                <div class='insight-content'>
                • <strong>Focus Category:</strong> {top_category} ({top_percentage:.1f}% of total)<br>
                • <strong>Optimization Goal:</strong> Reduce by 10-15%<br>
                • <strong>Strategy:</strong> Vendor negotiation + process improvement<br>
                • <strong>Target Savings:</strong> ₹{top_amount * 0.12:,.0f} annually<br>
                • <strong>Implementation:</strong> 60-day optimization program
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 90-Day Implementation Roadmap")
        
        quarters = [
            {
                "title": "📋 QUARTER 1: FOUNDATION",
                "actions": [
                    f"Weeks 1-4: Comprehensive {category} audit",
                    f"Weeks 5-8: Implement budget control system",
                    f"Weeks 9-12: Establish monthly review cadence"
                ]
            },
            {
                "title": "🚀 QUARTER 2: OPTIMIZATION", 
                "actions": [
                    "Weeks 1-4: Vendor renegotiation program",
                    "Weeks 5-8: Process efficiency improvements",
                    "Weeks 9-12: Technology automation implementation"
                ]
            },
            {
                "title": "📈 QUARTER 3: GROWTH",
                "actions": [
                    "Weeks 1-4: Strategic budget reallocation",
                    "Weeks 5-8: Advanced forecasting implementation", 
                    "Weeks 9-12: Performance benchmarking"
                ]
            }
        ]
        
        for i, quarter in enumerate(quarters, 1):
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>{quarter['title']}</div>
                <div class='insight-content'>
                {"<br>".join([f"• {action}" for action in quarter['actions']])}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================= ANALYSIS DEPTH HANDLER =================
def handle_analysis_depth(analysis_depth, metrics, df, monthly_df, forecast_df, category):
    """Handle different analysis depth levels with enhanced content"""
    
    if analysis_depth == "Quick Overview":
        render_quick_overview(metrics, df, monthly_df, category)
    elif analysis_depth == "Detailed Analysis":
        render_detailed_analysis(metrics, df, monthly_df, forecast_df, category)
    else:  # Strategic Planning
        render_strategic_planning(metrics, df, monthly_df, forecast_df, category)

def render_quick_overview(metrics, df, monthly_df, category):
    """Quick overview - executive summary"""
    render_kpi_dashboard(metrics, category)
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_expense_breakdown(df, metrics['total_spent'], category)
    
    with col2:
        # Quick insights card
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("🚀 Executive Summary")
        
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>📋 QUICK ASSESSMENT</div>
            <div class='insight-content'>
            • <strong>Overall Health:</strong> {metrics['efficiency_comment']}<br>
            • <strong>Growth Status:</strong> {metrics['trend_description']}<br>
            • <strong>Budget Adherence:</strong> {metrics['variance']*100:.1f}% monthly variation<br>
            • <strong>Key Focus:</strong> {df.groupby('Expense Head')['Amount'].sum().idxmax() if 'Expense Head' in df.columns else 'General optimization'}<br>
            • <strong>Next Steps:</strong> Switch to Detailed Analysis for deeper insights
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        render_actionable_insights(metrics, df, category)

def render_detailed_analysis(metrics, df, monthly_df, forecast_df, category):
    """Detailed analysis - comprehensive insights"""
    render_kpi_dashboard(metrics, category)
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_forecast_chart(monthly_df, forecast_df, category, metrics)
        render_monthly_patterns(monthly_df, category)
    
    with col2:
        render_expense_breakdown(df, metrics['total_spent'], category)
        render_actionable_insights(metrics, df, category)

def render_strategic_planning(metrics, df, monthly_df, forecast_df, category):
    """Strategic planning - future-focused analysis"""
    st.markdown(f"<div class='section-header'>🎯 STRATEGIC PLANNING - {category.upper()}</div>", unsafe_allow_html=True)
    
    render_kpi_dashboard(metrics, category)
    
    # Strategic focus with enhanced layout
    col1, col2 = st.columns(2)
    
    with col1:
        render_forecast_chart(monthly_df, forecast_df, category, metrics)
        
        # Enhanced budget planning
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("💰 STRATEGIC BUDGET PLANNING")
        
        if not forecast_df.empty:
            avg_forecast = forecast_df['Forecast'].mean()
            total_forecast = forecast_df['Forecast'].sum()
            
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>📊 BUDGET RECOMMENDATIONS</div>
                <div class='insight-content'>
                • <strong>Historical Baseline:</strong> ₹{metrics['avg_monthly']:,.0f}/month<br>
                • <strong>Future Projection:</strong> ₹{avg_forecast:,.0f}/month<br>
                • <strong>Strategic Allocation:</strong> ₹{max(metrics['avg_monthly'], avg_forecast) * 1.15:,.0f}/month<br>
                • <strong>Total Forecast:</strong> ₹{total_forecast:,.0f} over {len(forecast_df)} months<br>
                • <strong>Contingency:</strong> 15% buffer for uncertainty<br>
                • <strong>Peak Reserve:</strong> ₹{metrics['highest_month_amount']:,.0f} for high-spend periods
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        render_expense_breakdown(df, metrics['total_spent'], category)
        
        # Enhanced risk management
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("🛡️ ADVANCED RISK MANAGEMENT")
        
        risk_level = "LOW" if metrics['variance'] < 0.3 else "MEDIUM" if metrics['variance'] < 0.6 else "HIGH"
        risk_color = "#27ae60" if risk_level == "LOW" else "#f39c12" if risk_level == "MEDIUM" else "#e74c3c"
        
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>📈 RISK ASSESSMENT</div>
            <div class='insight-content'>
            • <strong>Risk Level:</strong> <span style='color: {risk_color}; font-weight: 800;'>{risk_level}</span><br>
            • <strong>Volatility:</strong> {metrics['variance']*100:.1f}% monthly variation<br>
            • <strong>Efficiency Impact:</strong> {10 - metrics['efficiency_score']} points improvement possible<br>
            • <strong>Mitigation Strategy:</strong> {f"Maintain excellent controls" if risk_level == "LOW" else "Implement enhanced monitoring" if risk_level == "MEDIUM" else "Immediate intervention required"}<br>
            • <strong>Monitoring Frequency:</strong> {f"Monthly" if risk_level == "LOW" else "Bi-weekly" if risk_level == "MEDIUM" else "Weekly"}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    render_actionable_insights(metrics, df, category)

# ================= ENHANCED COMBINED VIEW =================
def render_combined_view(data):
    """Render enhanced combined view across all categories"""
    st.markdown("<div class='section-header'>🌐 ENTERPRISE-WIDE EXPENSE INTELLIGENCE</div>", unsafe_allow_html=True)
    
    if not data:
        st.warning("No data available for combined analysis")
        return
    
    # Calculate comprehensive combined metrics
    all_data = []
    category_metrics = {}
    total_enterprise_spend = 0
    
    for category_name, df in data.items():
        monthly_df = preprocess_data(df)
        if not monthly_df.empty:
            metrics = calculate_comprehensive_metrics(monthly_df, df, category_name)
            category_metrics[category_name] = metrics
            all_data.append(df)
            total_enterprise_spend += metrics['total_spent']
    
    if not all_data:
        st.warning("No valid data available for enterprise analysis")
        return
    
    # Combine all data for enterprise view
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_monthly = preprocess_data(combined_df)
    combined_metrics = calculate_comprehensive_metrics(combined_monthly, combined_df, "ENTERPRISE")
    
    # Enterprise Performance Dashboard
    st.markdown("### 🏢 ENTERPRISE PERFORMANCE DASHBOARD")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Enterprise Spend", f"₹{combined_metrics['total_spent']:,.0f}")
    with col2:
        st.metric("📈 Overall Growth Rate", f"{combined_metrics['growth_rate']:+.1f}%")
    with col3:
        st.metric("📊 Monthly Average", f"₹{combined_metrics['avg_monthly']:,.0f}")
    with col4:
        efficiency_color = "#27ae60" if combined_metrics['efficiency_score'] >= 7 else "#f39c12" if combined_metrics['efficiency_score'] >= 5 else "#e74c3c"
        st.metric("🎯 Efficiency Score", f"{combined_metrics['efficiency_score']}/10", 
                 delta_color="off" if combined_metrics['efficiency_score'] < 7 else "normal")
    
    # Enhanced Category Performance Comparison
    st.markdown("### 📊 STRATEGIC CATEGORY COMPARISON")
    
    comparison_data = []
    for category_name, metrics in category_metrics.items():
        risk_level = "LOW" if metrics['variance'] < 0.3 else "MEDIUM" if metrics['variance'] < 0.6 else "HIGH"
        comparison_data.append({
            'Category': category_name,
            'Total Spend': metrics['total_spent'],
            'Monthly Avg': metrics['avg_monthly'],
            'Growth Rate': metrics['growth_rate'],
            'Efficiency': metrics['efficiency_score'],
            'Risk Level': risk_level,
            'Share %': (metrics['total_spent'] / total_enterprise_spend * 100)
        })
    
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data)
        comp_df = comp_df.sort_values('Total Spend', ascending=False)
        
        # Enhanced styling
        def color_risk(val):
            if val == 'LOW': return 'background-color: #d4edda; color: #155724; font-weight: 700;'
            elif val == 'MEDIUM': return 'background-color: #fff3cd; color: #856404; font-weight: 700;'
            else: return 'background-color: #f8d7da; color: #721c24; font-weight: 700;'
        
        def color_efficiency(val):
            if val >= 8: return 'background-color: #d4edda; color: #155724; font-weight: 700;'
            elif val >= 6: return 'background-color: #fff3cd; color: #856404; font-weight: 700;'
            else: return 'background-color: #f8d7da; color: #721c24; font-weight: 700;'
        
        styled_df = comp_df.style.format({
            'Total Spend': '₹{:,.0f}',
            'Monthly Avg': '₹{:,.0f}',
            'Growth Rate': '{:+.1f}%',
            'Efficiency': '{:.1f}',
            'Share %': '{:.1f}%'
        }).applymap(color_risk, subset=['Risk Level']).applymap(color_efficiency, subset=['Efficiency'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Enhanced enterprise insights
        highest_category = comp_df.loc[comp_df['Total Spend'].idxmax()]
        most_efficient = comp_df.loc[comp_df['Efficiency'].idxmax()]
        fastest_growing = comp_df.loc[comp_df['Growth Rate'].idxmax()]
        
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>🎯 ENTERPRISE INTELLIGENCE</div>
            <div class='insight-content'>
            • <strong>Largest Category:</strong> {highest_category['Category']} (₹{highest_category['Total Spend']:,.0f}, {highest_category['Share %']:.1f}% of total)<br>
            • <strong>Most Efficient:</strong> {most_efficient['Category']} ({most_efficient['Efficiency']}/10 efficiency score)<br>
            • <strong>Fastest Growing:</strong> {fastest_growing['Category']} ({fastest_growing['Growth Rate']:+.1f}% growth rate)<br>
            • <strong>Overall Health:</strong> {f"Excellent" if combined_metrics['efficiency_score'] >= 8 else "Good" if combined_metrics['efficiency_score'] >= 6 else "Needs Attention"}<br>
            • <strong>Strategic Focus:</strong> Optimize {highest_category['Category']} for maximum impact
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================= ENHANCED SMART ANALYTICS =================
def render_smart_analytics(data, category):
    """Render enhanced smart analytics with better insights"""
    st.markdown("<div class='section-header'>🤖 ADVANCED AI ANALYTICS</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='simple-explanation'>
    <strong>💡 Intelligent Analysis:</strong> Our advanced AI algorithms analyze your expense patterns to provide 
    deep insights, predictive analytics, and strategic recommendations for optimal financial management.
    </div>
    """, unsafe_allow_html=True)
    
    if category in data:
        df = data[category]
        monthly_df = preprocess_data(df)
        
        if not monthly_df.empty:
            # Get enhanced ML insights
            ml_insights = advanced_ml_analysis(monthly_df, df)
            
            # Enhanced display layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔍 PATTERN INTELLIGENCE")
                st.markdown(f"""
                <div class='insight-card'>
                    <div class='insight-title'>📈 SPENDING PATTERNS</div>
                    <div class='insight-content'>
                    {ml_insights.get('patterns', 'Analyzing your unique spending patterns...')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='insight-card'>
                    <div class='insight-title'>💡 OPTIMIZATION OPPORTUNITIES</div>
                    <div class='insight-content'>
                    {ml_insights.get('optimization', 'Identifying strategic optimization areas...')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 🔮 PREDICTIVE INTELLIGENCE")
                st.markdown(f"""
                <div class='insight-card'>
                    <div class='insight-title'>📊 FUTURE TRENDS</div>
                    <div class='insight-content'>
                    {ml_insights.get('forecasting', 'Generating intelligent future predictions...')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='insight-card'>
                    <div class='insight-title'>🛡️ RISK INTELLIGENCE</div>
                    <div class='insight-content'>
                    {ml_insights.get('risk', 'Assessing financial risks and opportunities...')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Additional AI insights
            st.markdown("### 🧠 STRATEGIC RECOMMENDATIONS")
            st.markdown(f"""
            <div class='insight-card'>
                <div class='insight-title'>🚀 AI-POWERED STRATEGY</div>
                <div class='insight-content'>
                Based on comprehensive analysis of your expense data, our AI recommends:
                • <strong>Focus optimization efforts</strong> on highest-impact categories<br>
                • <strong>Implement predictive budgeting</strong> for better planning<br>
                • <strong>Leverage seasonal patterns</strong> for strategic allocation<br>
                • <strong>Monitor key risk indicators</strong> proactively<br>
                • <strong>Automate expense tracking</strong> for real-time insights
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================= ENHANCED DATA EXPLORER =================
def render_data_explorer(data, category):
    """Render enhanced data explorer with export functionality"""
    st.markdown("<div class='section-header'>📋 ADVANCED DATA EXPLORER</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='simple-explanation'>
    <strong>💡 Data Intelligence:</strong> Explore your detailed expense data with advanced filtering, 
    comprehensive analysis, and multiple export options for reporting and strategic planning.
    </div>
    """, unsafe_allow_html=True)
    
    if category in data:
        df = data[category]
        
        # Enhanced filtering options
        st.markdown("### 🔍 INTELLIGENT DATA FILTERS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "Expense Head" in df.columns:
                categories = st.multiselect(
                    "Filter by Category:",
                    options=df['Expense Head'].unique(),
                    default=df['Expense Head'].unique()[:3],
                    key="category_filter"
                )
            else:
                categories = None
        
        with col2:
            amount_range = st.slider(
                "Amount Range:",
                min_value=float(df['Amount'].min()),
                max_value=float(df['Amount'].max()),
                value=(float(df['Amount'].min()), float(df['Amount'].max())),
                key="amount_filter"
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range:",
                value=(df['Date'].min(), df['Date'].max()),
                min_value=df['Date'].min(),
                max_value=df['Date'].max(),
                key="date_range"
            )
        
        # Apply enhanced filters
        filtered_df = df.copy()
        if categories:
            filtered_df = filtered_df[filtered_df['Expense Head'].isin(categories)]
        filtered_df = filtered_df[
            (filtered_df['Amount'] >= amount_range[0]) & 
            (filtered_df['Amount'] <= amount_range[1])
        ]
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['Date'] >= pd.to_datetime(date_range[0])) & 
                (filtered_df['Date'] <= pd.to_datetime(date_range[1]))
            ]
        
        # Enhanced data display
        st.markdown("### 📊 FILTERED DATA ANALYSIS")
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Enhanced export options
        st.markdown("### 💾 ADVANCED EXPORT OPTIONS")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # CSV Export
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{category}_detailed_expenses.csv",
                mime="text/csv",
                use_container_width=True,
                key="csv_export"
            )
        
        with col_exp2:
            # Excel Export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name=category)
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Records', 'Total Amount', 'Average Amount', 'Date Range'],
                    'Value': [
                        len(filtered_df),
                        f"₹{filtered_df['Amount'].sum():,.0f}",
                        f"₹{filtered_df['Amount'].mean():,.0f}",
                        f"{filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Summary')
            
            st.download_button(
                label="📊 Download Excel Report",
                data=output.getvalue(),
                file_name=f"{category}_comprehensive_report.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True,
                key="excel_export"
            )
        
        with col_exp3:
            # PDF Report Generation
            if st.button("📄 Generate PDF Report", use_container_width=True, key="pdf_generate"):
                with st.spinner("🔄 Creating comprehensive PDF report..."):
                    try:
                        pdf_buffer = generate_comprehensive_pdf(filtered_df, category)
                        st.success("✅ PDF report generated successfully!")
                        
                        st.download_button(
                            label="📋 Download PDF Report",
                            data=pdf_buffer.getvalue(),
                            file_name=f"{category}_strategic_analysis.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="pdf_download"
                        )
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")

# ================= PDF GENERATION HANDLER =================
def handle_pdf_generation(data, category):
    """Handle PDF report generation for the current category"""
    if category in data:
        df = data[category]
        monthly_df = preprocess_data(df)
        
        if not monthly_df.empty:
            metrics = calculate_comprehensive_metrics(monthly_df, df, category)
            forecast_df = forecast_expenses(monthly_df, st.session_state.forecast_periods)
            
            with st.spinner("🔄 Generating comprehensive PDF report..."):
                try:
                    pdf_buffer = generate_comprehensive_pdf(df, category, metrics, monthly_df, forecast_df)
                    return pdf_buffer
                except Exception as e:
                    st.error(f"❌ Error generating PDF report: {str(e)}")
                    return None
    return None

# ================= MAIN APPLICATION =================
def main():
    # Initialize session state
    initialize_session_state()
    
    # Render premium header
    render_header()
    
    # Render sidebar and get controls
    sidebar_result = render_sidebar()
    if sidebar_result is None:
        st.warning("📁 Please upload an Excel file to begin intelligent expense analysis")
        return
        
    category, data, analysis_depth = sidebar_result
    
    # Handle PDF generation if requested
    if st.session_state.get('generate_pdf', False):
        pdf_buffer = handle_pdf_generation(data, category)
        if pdf_buffer:
            st.success("✅ Comprehensive PDF report generated!")
            
            # Provide download button
            st.download_button(
                label="📋 Download Comprehensive PDF Report",
                data=pdf_buffer.getvalue(),
                file_name=f"{category}_strategic_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="final_pdf_download"
            )
        
        # Reset the flag
        st.session_state.generate_pdf = False
    
    # Enhanced main content with premium tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 CATEGORY ANALYSIS", 
        "🌐 ENTERPRISE VIEW", 
        "🤖 AI ANALYTICS", 
        "📋 DATA EXPLORER"
    ])
    
    with tab1:
        if category in data:
            df = data[category]
            monthly_df = preprocess_data(df)
            
            if not monthly_df.empty:
                # Calculate enhanced metrics
                metrics = calculate_comprehensive_metrics(monthly_df, df, category)
                forecast_df = forecast_expenses(monthly_df, st.session_state.forecast_periods)
                
                # Handle analysis depth with enhanced content
                handle_analysis_depth(analysis_depth, metrics, df, monthly_df, forecast_df, category)
            else:
                st.warning(f"⚠️ Insufficient monthly data for comprehensive analysis of {category}")
        else:
            st.error("❌ Selected category not found in the dataset")
    
    with tab2:
        render_combined_view(data)
    
    with tab3:
        render_smart_analytics(data, category)
    
    with tab4:
        render_data_explorer(data, category)

# Run the application
if __name__ == "__main__":
    main()
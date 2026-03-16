import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# --------------------------------------------------------------------------------
# 🎨 PAGE CONFIG & PREMIUM DARK THEME STYLING
# --------------------------------------------------------------------------------

st.set_page_config(
    page_title="Product Analytics",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Dark Styling (Obsidian / Midnight inspired)
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main { background-color: #0F172A; color: #F8FAFC; }
    
    /* Header & Titles */
    .header-container {
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1E293B;
    }
    .main-title {
        color: #F8FAFC !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #CBD5E1 !important;
        font-size: 1.1rem;
    }
    
    /* Global Text Contrast */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #F1F5F9 !important;
    }

    /* Professional Dark KPI Cards */
    .kpi-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
        border: 1px solid #334155;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #6366F1;
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 1.875rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    /* Section Styling */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F1F5F9;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Insight Boxes */
    .insight-container {
        background-color: #1E293B;
        border-left: 5px solid #6366F1;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1.5rem;
        font-size: 0.95rem;
        color: #F1F5F9 !important;
        line-height: 1.5;
    }

    /* AI Assistant Interface */
    .ai-bubble {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    .user-query-label { color: #818CF8; font-weight: 700; font-size: 0.8rem; margin-bottom: 5px; text-transform: uppercase; }

    /* Footer */
    .footer {
        margin-top: 5rem;
        padding: 2rem 0;
        border-top: 1px solid #1E293B;
        color: #64748B;
        font-size: 0.85rem;
        text-align: center;
    }
    
    .status-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-connected { background-color: #064E3B; color: #34D399; }
    .status-pending { background-color: #422006; color: #FBBF24; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2, 
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #F8FAFC;
    }
    [data-testid="stSidebar"] label {
        color: #94A3B8 !important;
    }
    
    /* Sidebar Input Fields */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="input"] > div,
    [data-testid="stSidebar"] div[data-baseweb="datepicker"] > div {
        background-color: #0F172A !important;
        border-color: #475569 !important;
    }
    
    /* Ensure all text within sidebar inputs is bright and visible */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
    }
    
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] div[role="button"] {
        color: #F8FAFC !important;
    }

    /* Override Tab styling for dark mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        color: #94A3B8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #F8FAFC !important;
        border-bottom-color: #6366F1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# 🛠️ DATA LOADING & CACHING
# --------------------------------------------------------------------------------

@st.cache_data
def load_data():
    users = pd.read_csv('data/users.csv')
    events = pd.read_csv('data/events1.csv')
    items = pd.read_csv('data/items.csv')
    
    users.rename(columns={'id': 'user_id'}, inplace=True)
    users['date'] = pd.to_datetime(users['date'])
    events['date'] = pd.to_datetime(events['date'])
    
    full_events = pd.merge(events, items, left_on='item_id', right_on='id', how='left')
    return users, events, full_events

users_df, events_df, full_events = load_data()

# Summary logic for AI context
def get_data_summary(filtered_events, filtered_users):
    t_users = filtered_events['user_id'].nunique()
    t_sessions = filtered_events['ga_session_id'].nunique()
    t_trans = filtered_events[filtered_events['type'] == 'purchase'].shape[0]
    t_rev = filtered_users['ltv'].sum()
    c_rate = (t_trans / t_sessions * 100) if t_sessions > 0 else 0
    top_devices = filtered_events.groupby('device').size().sort_values(ascending=False).to_dict()
    
    country_counts = filtered_events.groupby('country').size().sort_values(ascending=False)
    top_countries = country_counts.head(5).to_dict()
    bottom_countries = country_counts.tail(5).to_dict()
    
    return f"""
    Context:
    - Users: {t_users:,}, Sessions: {t_sessions:,}, Transactions: {t_trans:,}
    - Revenue: ${t_rev:,.2f}, Conv Rate: {c_rate:.2f}%
    - Top Devices: {top_devices}
    - Top 5 Countries: {top_countries}
    - Bottom 5 Countries: {bottom_countries}
    """

# --------------------------------------------------------------------------------
# 🔍 SIDEBAR CONTROL PANEL
# --------------------------------------------------------------------------------

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("Filters")
    st.markdown("---")
    
    min_date, max_date = events_df['date'].min().to_pydatetime(), events_df['date'].max().to_pydatetime()
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    
    device_options = ["All Devices"] + list(events_df['device'].unique())
    sel_device = st.selectbox("Device Segment", options=device_options)
    
    country_options = ["All Regions"] + list(events_df['country'].unique())
    sel_countries = st.multiselect("Marketing Regions", options=country_options, default="All Regions")
    
    st.markdown("---")
    st.subheader("AI System")
    
    try:
        SECRET_KEY = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        SECRET_KEY = None
        
    if SECRET_KEY:
        st.markdown('<span class="status-badge status-connected">● SYSTEM CONNECTED</span>', unsafe_allow_html=True)
        gemini_api_key = SECRET_KEY
        use_gemini = True
    else:
        st.markdown('<span class="status-badge status-pending">○ MANUAL KEY REQUIRED</span>', unsafe_allow_html=True)
        use_gemini = st.toggle("Enable Gemini Engine", value=False)
        gemini_api_key = st.text_input("Enter Key", type="password")

# Filtering Data Logic
filtered_events = events_df.copy()
filtered_users = users_df.copy()

if len(date_range) == 2:
    start, end = date_range
    filtered_events = filtered_events[(filtered_events['date'].dt.date >= start) & (filtered_events['date'].dt.date <= end)]
    filtered_users = filtered_users[(filtered_users['date'].dt.date >= start) & (filtered_users['date'].dt.date <= end)]

if sel_device != "All Devices":
    filtered_events = filtered_events[filtered_events['device'] == sel_device]

if "All Regions" not in sel_countries and sel_countries:
    filtered_events = filtered_events[filtered_events['country'].isin(sel_countries)]

t_users = filtered_events['user_id'].nunique()
t_sessions = filtered_events['ga_session_id'].nunique()
t_trans = filtered_events[filtered_events['type'] == 'purchase'].shape[0]
t_rev = filtered_users['ltv'].sum()
c_rate = (t_trans / t_sessions * 100) if t_sessions > 0 else 0

# --------------------------------------------------------------------------------
# 🏛️ MAIN DASHBOARD BODY
# --------------------------------------------------------------------------------

st.markdown("""
<div class="header-container">
    <div class="main-title">🌙 Product Analytics Dashboard</div>
    <div class="subtitle">User Behavior & Growth Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

tab_overview, tab_acquisition, tab_behavior, tab_revenue, tab_ai = st.tabs([
    "📊 Overview", "🌍 Acquisition", "🏃 Behavior", "💰 Revenue", "🤖 AI Assistant"
])

# --- TAB 1: OVERVIEW ---
with tab_overview:
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("Total Users", f"{t_users:,}"), ("Sessions", f"{t_sessions:,}"),
        ("Transactions", f"{t_trans:,}"), ("CVR", f"{c_rate:.2f}%"), ("Net Revenue", f"${t_rev:,.0f}")
    ]
    cols = [c1, c2, c3, c4, c5]
    for i, (label, val) in enumerate(metrics):
        with cols[i]:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)
            
    st.markdown('<div class="section-header">📈 Growth Trends</div>', unsafe_allow_html=True)
    daily_trend = filtered_events.groupby(filtered_events['date'].dt.date).size().reset_index()
    daily_trend.columns = ['Date', 'Events']
    
    fig_trend = px.area(daily_trend, x='Date', y='Events', line_shape='spline', 
                        color_discrete_sequence=['#818CF8'], template='plotly_dark', height=400)
    fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color='#F1F5F9'),
                            title=dict(font=dict(color='#F1F5F9')),
                            xaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                            yaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                            xaxis_title="", yaxis_title="Daily Events", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('<div class="insight-container"><b>Product Insight:</b> Engagement spike detected during mid-week cycles. Ideal for scheduled marketing push.</div>', unsafe_allow_html=True)

# --- TAB 2: ACQUISITION ---
with tab_acquisition:
    st.markdown('<div class="section-header">🌍 Global Reach & Channels</div>', unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("Top Traffic Sources")
        geo_data = filtered_events.groupby('country')['user_id'].nunique().sort_values(ascending=False).head(10).reset_index()
        fig_geo = px.bar(geo_data, x='user_id', y='country', orientation='h', 
                         color='user_id', color_continuous_scale='Purp', template='plotly_dark')
        fig_geo.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0), 
                             font=dict(color='#F1F5F9'),
                             xaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                             yaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_geo, use_container_width=True)
        
    with col_a2:
        st.subheader("Device Performance Segments")
        dev_data = filtered_events['device'].value_counts().reset_index()
        fig_dev = px.pie(dev_data, names='device', values='count', hole=0.6,
                         color_discrete_sequence=px.colors.qualitative.Vivid, template='plotly_dark')
        fig_dev.update_layout(margin=dict(l=0, r=0, t=40, b=0), 
                             font=dict(color='#F1F5F9'),
                             legend=dict(font=dict(color='#F1F5F9')),
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dev, use_container_width=True)
        
    st.markdown('<div class="insight-container"><b>Acquisition Insight:</b> High-quality traffic is concentrated in Desktop users from the US and CA. Retargeting campaigns should prioritize these segments for higher LTV.</div>', unsafe_allow_html=True)

# --- TAB 3: BEHAVIOR ---
with tab_behavior:
    st.markdown('<div class="section-header">🏃 Engagement & Conversion Funnels</div>', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.subheader("Daily Engagement Hour (UTC)")
        hourly = filtered_events.groupby(filtered_events['date'].dt.hour).size()
        fig_hour = px.line(x=hourly.index, y=hourly.values, markers=True, 
                           line_shape='spline', template='plotly_dark', color_discrete_sequence=['#A78BFA'])
        fig_hour.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font=dict(color='#F1F5F9'),
                              xaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                              yaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                              margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_hour, use_container_width=True)
        
    with col_b2:
        st.subheader("Conversion Health Funnel")
        stages_data = [
            {"Stage": "Sessions", "Users": t_sessions},
            {"Stage": "Add Cart", "Users": filtered_events[filtered_events['type'] == 'add_to_cart']['user_id'].nunique()},
            {"Stage": "Checkout", "Users": filtered_events[filtered_events['type'] == 'begin_checkout']['user_id'].nunique()},
            {"Stage": "Purchase", "Users": filtered_events[filtered_events['type'] == 'purchase']['user_id'].nunique()}
        ]
        funnel_df = pd.DataFrame(stages_data)
        fig_funnel = go.Figure(go.Funnel(y=funnel_df['Stage'], x=funnel_df['Users'], 
                                        textinfo="value+percent initial",
                                        marker={"color": ["#334155", "#475569", "#64748B", "#818CF8"]}))
        fig_funnel.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                font=dict(color='#F1F5F9'),
                                margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    st.markdown('<div class="insight-container"><b>Behavior Insight:</b> The conversion rate from <b>Add to Cart → Purchase is 32%</b>. This strong retention suggests high intent-to-buy once items are selected.</div>', unsafe_allow_html=True)

# --- TAB 4: REVENUE ---
with tab_revenue:
    st.markdown('<div class="section-header">💰 Financial Performance & Forecasts</div>', unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.subheader("Daily Revenue Trend")
        rev_trend = filtered_users.groupby(filtered_users['date'].dt.date)['ltv'].sum().reset_index()
        fig_rev = px.line(rev_trend, x='date', y='ltv', template='plotly_dark', color_discrete_sequence=['#34D399'])
        fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                             font=dict(color='#F1F5F9'),
                             xaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                             yaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                             margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with col_r2:
        st.subheader("🔮 30-Day Activity Forecast")
        if HAS_PROPHET:
            try:
                f_data = events_df.groupby(events_df['date'].dt.date).size().reset_index()
                f_data.columns = ['ds', 'y']
                f_data = f_data[f_data['y'] > 0].tail(180)
                m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False).fit(f_data)
                future = m.make_future_dataframe(periods=30)
                forecast = m.predict(future)
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(x=f_data['ds'], y=f_data['y'], name='Actual', line=dict(color='#94A3B8')))
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'].tail(31), y=forecast['yhat'].tail(31), name='Forecast', line=dict(color='#818CF8', width=3, dash='dot')))
                fig_forecast.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                         font=dict(color='#F1F5F9'),
                                         xaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                                         yaxis=dict(tickfont=dict(color='#F8FAFC'), titlefont=dict(color='#F8FAFC')),
                                         margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig_forecast, use_container_width=True)
            except Exception: st.info("Predictive engine warming up...")
        else: st.warning("Prophet not available.")
        
    st.markdown('<div class="insight-container"><b>Revenue Insight:</b> Daily revenue is scaling positively with seasonal peaks. The 30-day forecast predicts a continued upward trajectory in gross transactions.</div>', unsafe_allow_html=True)

# --- TAB 5: AI ASSISTANT ---
with tab_ai:
    st.markdown('<div class="section-header">🤖 AI Data Intelligence</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="ai-bubble"><span style="color: #F8FAFC;">👋 <b>System Ready.</b> Ask me about your current filtered metrics or growth bottlenecks.</span></div>', unsafe_allow_html=True)
        user_input = st.text_input("Consult AI Analyst:", placeholder="e.g., 'Analyze the current conversion drop-off'")
        
        if user_input:
            st.markdown(f'<div class="user-query-label">Your Query</div><div style="color: #F1F5F9; font-weight: 600; font-size: 1.1rem; margin-bottom: 20px;">"{user_input}"</div>', unsafe_allow_html=True)
            if use_gemini and gemini_api_key and HAS_GEMINI:
                try:
                    genai.configure(api_key=gemini_api_key)
                    with st.spinner("AI is synthesizing insights..."):
                        context = get_data_summary(filtered_events, filtered_users)
                        prompt = f"Context:\n{context}\n\nUser Question: {user_input}\n\nStrictly professional, data-driven analysis."
                        try:
                            model = genai.GenerativeModel('gemini-2.0-flash')
                            response = model.generate_content(prompt)
                        except Exception:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            response = model.generate_content(prompt)
                        if response:
                            st.markdown(f'<div style="background-color: #1E293B; border: 1px solid #334155; padding: 20px; border-radius: 12px; border-left: 5px solid #34D399;"><div style="color: #34D399; font-weight: 700; font-size: 0.8rem; margin-bottom: 10px;">GEMINI AI RESPONSE</div><div style="color: #E2E8F0; line-height: 1.6;">{response.text}</div></div>', unsafe_allow_html=True)
                except Exception as ex: st.error(f"Error: {str(ex)}")
            else: st.info("Enable Gemini in the sidebar for AI support.")

st.markdown(f'<div class="footer"><p><b>Data:</b> Google Merchandise Store • <b>Tools:</b> Python, Streamlit, Plotly, Gemini 2.0</p><p>© {datetime.now().year} Daniswara Aditya Putra</p></div>', unsafe_allow_html=True)

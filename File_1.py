import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# ============================================================================
# PAGE CONFIG & DARK THEME CSS
# ============================================================================

st.set_page_config(
    page_title="RED ROOM - AI Stress Tester",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional SOC dark theme
soc_theme_css = """
<style>
    * {
        margin: 0;
        padding: 0;
    }

    /* Overall page background */
    .main {
        background-color: #0a0e1a !important;
        color: #e0e0e0 !important;
    }

    [data-testid="stMainBlockContainer"] {
        background-color: #0a0e1a !important;
        padding: 2rem;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #0f1419 !important;
    }

    [data-testid="stSidebarContent"] {
        background-color: #0f1419 !important;
    }

    /* Text colors */
    body {
        background-color: #0a0e1a !important;
        color: #e0e0e0 !important;
    }

    /* Streamlit headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00d4ff !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
    }

    /* Cards and containers */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
    }

    [data-testid="stMetricLabel"] {
        color: #b0b8c1 !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    /* Buttons */
    button[kind="primary"], button[kind="secondary"] {
        background-color: #00d4ff !important;
        color: #0a0e1a !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    button[kind="primary"]:hover, button[kind="secondary"]:hover {
        background-color: #00f0ff !important;
        transform: scale(1.02) !important;
    }

    /* Input fields */
    input, textarea, select {
        background-color: #141824 !important;
        color: #e0e0e0 !important;
        border: 1px solid #00d4ff !important;
        border-radius: 4px !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
    }

    input:focus, textarea:focus, select:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
    }

    /* Tables */
    .dataframe {
        background-color: #141824 !important;
        color: #e0e0e0 !important;
    }

    .dataframe th {
        background-color: #0a0e1a !important;
        color: #00d4ff !important;
        border-bottom: 2px solid #00d4ff !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    .dataframe td {
        background-color: #141824 !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid #1a2332 !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #141824 !important;
        border: 1px solid #1a2332 !important;
        border-radius: 4px !important;
    }

    [data-testid="stExpanderDetails"] {
        background-color: #0f1419 !important;
    }

    /* Multiselect */
    [role="combobox"] {
        background-color: #141824 !important;
        border: 1px solid #00d4ff !important;
    }

    /* Checkbox */
    [role="checkbox"] {
        accent-color: #00d4ff !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #0a0e1a;
    }

    ::-webkit-scrollbar-thumb {
        background: #00d4ff;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #00f0ff;
    }

    /* Dividers */
    hr {
        border: none !important;
        border-top: 2px solid #00d4ff !important;
        opacity: 0.3 !important;
        margin: 2rem 0 !important;
    }

    /* Links */
    a {
        color: #00d4ff !important;
        text-decoration: none !important;
    }

    a:hover {
        color: #00f0ff !important;
        text-decoration: underline !important;
    }

    /* Badge styling */
    .badge-high {
        background-color: #ff4757 !important;
        color: white !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    .badge-medium {
        background-color: #ffa502 !important;
        color: #0a0e1a !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    .badge-low {
        background-color: #2ed573 !important;
        color: #0a0e1a !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
</style>
"""

st.markdown(soc_theme_css, unsafe_allow_html=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_db_connection():
    """Connect to SQLite database"""
    conn = sqlite3.connect("logs.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_logs_df():
    """Fetch all logs as a pandas DataFrame"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.markdown("### 🔍 **FILTERS**")
    st.markdown("---")
    
    df_all = get_logs_df()
    
    # Severity filter
    severity_options = sorted(df_all['severity'].unique().tolist()) if not df_all.empty else []
    severity_filter = st.multiselect(
        "Severity Level",
        options=severity_options,
        default=severity_options,
        key="severity_filter"
    )
    
    # Category filter
    category_options = sorted(df_all['categories'].unique().tolist()) if not df_all.empty else []
    category_filter = st.multiselect(
        "Threat Category",
        options=category_options,
        default=category_options,
        key="category_filter"
    )
    
    # Action filter
    action_options = sorted(df_all['action'].unique().tolist()) if not df_all.empty else []
    action_filter = st.multiselect(
        "Action Taken",
        options=action_options,
        default=action_options,
        key="action_filter"
    )
    
    # Flagged only toggle
    flagged_only = st.checkbox("🚨 Show Flagged Only", value=False)
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 **REFRESH**", use_container_width=True, key="refresh_btn"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 **SIDEBAR STATS**")
    
    # Sidebar mini stats
    total = len(df_all)
    flagged = len(df_all[df_all['flagged'] == 1]) if not df_all.empty else 0
    blocked = len(df_all[df_all['action'] == 'block']) if not df_all.empty else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Requests", total, delta=None)
    with col2:
        st.metric("Flagged", flagged, delta=None)
    
    st.metric("Blocked", blocked, delta=None)

# ============================================================================
# APPLY FILTERS TO DATA
# ============================================================================

df = get_logs_df()

if not df.empty:
    if flagged_only:
        df = df[df['flagged'] == 1]
    
    df = df[df['severity'].isin(severity_filter)]
    df = df[df['categories'].isin(category_filter)]
    df = df[df['action'].isin(action_filter)]

# ============================================================================
# HERO / INTRO SECTION
# ============================================================================

hero_section = """
<div style="
    background: linear-gradient(135deg, #0f1a2e 0%, #16213e 50%, #0f1a2e 100%);
    border: 2px solid #00d4ff;
    border-radius: 8px;
    padding: 3rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    background-image: 
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 212, 255, 0.03) 2px,
            rgba(0, 212, 255, 0.03) 4px
        ),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 2px,
            rgba(0, 212, 255, 0.03) 2px,
            rgba(0, 212, 255, 0.03) 4px
        );
">
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="
            color: #00d4ff;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            font-family: 'Monaco', 'Courier New', monospace;
        ">🛡️ RED ROOM — AI STRESS TESTER</h1>
        <p style="
            color: #ff4757;
            font-size: 1.3rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
            font-family: 'Monaco', 'Courier New', monospace;
        ">Real-time Safety Monitoring & Threat Detection for Large Language Models</p>
        <p style="
            color: #b0b8c1;
            font-size: 0.95rem;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            font-family: 'Monaco', 'Courier New', monospace;
        ">
            Every message. Every response. Intercepted, analyzed, and scored in milliseconds.<br>
            No prompt goes undetected.
        </p>
    </div>

    <div style="
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    ">
        <!-- Feature Card 1 -->
        <div style="
            background: rgba(20, 24, 36, 0.8);
            border: 2px solid #ff4757;
            border-top: 3px solid #ff4757;
            border-radius: 6px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        ">
            <h3 style="
                color: #ff4757;
                font-size: 1.1rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
                font-family: 'Monaco', 'Courier New', monospace;
                letter-spacing: 0.05em;
            ">🔴 Proxy & Interceptor</h3>
            <p style="
                color: #b0b8c1;
                font-size: 0.85rem;
                line-height: 1.5;
                font-family: 'Monaco', 'Courier New', monospace;
            ">Sits between the user and the LLM. Captures every request and response in real time and routes it through the safety pipeline.</p>
        </div>

        <!-- Feature Card 2 -->
        <div style="
            background: rgba(20, 24, 36, 0.8);
            border: 2px solid #ffa502;
            border-top: 3px solid #ffa502;
            border-radius: 6px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        ">
            <h3 style="
                color: #ffa502;
                font-size: 1.1rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
                font-family: 'Monaco', 'Courier New', monospace;
                letter-spacing: 0.05em;
            ">🟡 Safety Classifier</h3>
            <p style="
                color: #b0b8c1;
                font-size: 0.85rem;
                line-height: 1.5;
                font-family: 'Monaco', 'Courier New', monospace;
            ">Detects jailbreak attempts, toxic language, prompt injections, and PII leaks using transformer models and regex pattern matching.</p>
        </div>

        <!-- Feature Card 3 -->
        <div style="
            background: rgba(20, 24, 36, 0.8);
            border: 2px solid #2ed573;
            border-top: 3px solid #2ed573;
            border-radius: 6px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        ">
            <h3 style="
                color: #2ed573;
                font-size: 1.1rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
                font-family: 'Monaco', 'Courier New', monospace;
                letter-spacing: 0.05em;
            ">🟢 Policy Engine & Logger</h3>
            <p style="
                color: #b0b8c1;
                font-size: 0.85rem;
                line-height: 1.5;
                font-family: 'Monaco', 'Courier New', monospace;
            ">Applies severity-based rules — block, warn, or allow. Logs every interaction with full metadata to SQLite for audit trails.</p>
        </div>
    </div>

    <div style="
        border: 2px solid #00d4ff;
        border-radius: 4px;
        padding: 1rem;
        text-align: center;
        background: rgba(0, 212, 255, 0.05);
    ">
        <p style="
            color: #00d4ff;
            font-size: 0.9rem;
            font-weight: bold;
            margin: 0;
            font-family: 'Monaco', 'Courier New', monospace;
            letter-spacing: 0.05em;
        ">
            ⚡ SYSTEM STATUS: All modules operational | Proxy: Active | Classifier: Online | Policy Engine: Running
        </p>
    </div>
</div>
"""

st.markdown(hero_section, unsafe_allow_html=True)

# Visual divider
st.markdown("---")

# ============================================================================
# LIVE CLOCK & PULSING INDICATOR
# ============================================================================

top_col1, top_col2, top_col3 = st.columns([2, 2, 1])

with top_col1:
    pass  # Reserved for logo/title

with top_col2:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style="text-align: center; font-family: 'Monaco', 'Courier New', monospace; color: #b0b8c1;">
        <p style="font-size: 0.9rem; margin: 0;">⏱️ {current_time}</p>
    </div>
    """, unsafe_allow_html=True)

with top_col3:
    st.markdown("""
    <div style="
        text-align: right;
        font-family: 'Monaco', 'Courier New', monospace;
        animation: pulse 1s infinite;
    ">
        <span style="
            color: #2ed573;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        ">● LIVE</span>
    </div>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# METRIC ROW - 5 CARDS
# ============================================================================

st.markdown("### 📊 **OPERATIONAL METRICS**")

if not df_all.empty:
    total_requests = len(df_all)
    threats_detected = len(df_all[df_all['flagged'] == 1])
    blocked_count = len(df_all[df_all['action'] == 'block'])
    warned_count = len(df_all[df_all['action'] == 'warn'])
    safe_count = len(df_all[df_all['action'] == 'allow'])
else:
    total_requests = threats_detected = blocked_count = warned_count = safe_count = 0

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric(
        label="TOTAL REQUESTS",
        value=total_requests,
        label_visibility="visible"
    )

with metric_col2:
    st.metric(
        label="THREATS DETECTED",
        value=threats_detected,
        label_visibility="visible"
    )

with metric_col3:
    st.metric(
        label="BLOCKED",
        value=blocked_count,
        label_visibility="visible"
    )

with metric_col4:
    st.metric(
        label="WARNED",
        value=warned_count,
        label_visibility="visible"
    )

with metric_col5:
    st.metric(
        label="SAFE",
        value=safe_count,
        label_visibility="visible"
    )

st.markdown("---")

# ============================================================================
# ROW 2: THREAT FEED (60%) + CHARTS (40%)
# ============================================================================

st.markdown("### 🔴 **LIVE THREAT FEED**")

left_col, right_col = st.columns([60, 40])

# LEFT COLUMN: THREAT FEED TABLE
with left_col:
    st.markdown("#### Recent Events")
    
    if not df.empty:
        # Display threat feed with color coding
        df_display = df.copy()
        
        # Truncate long text
        df_display['user_input'] = df_display['user_input'].str[:60] + "..."
        df_display['llm_output'] = df_display['llm_output'].str[:60] + "..."
        
        # Reorder and rename columns
        df_display = df_display[['timestamp', 'user_input', 'categories', 'severity', 'action']]
        df_display.columns = ['Timestamp', 'User Input', 'Category', 'Severity', 'Action']
        
        # Create styled HTML table
        html_table = "<div style='overflow-x: auto;'><table style='width: 100%; border-collapse: collapse; font-family: Monaco, Courier New, monospace; font-size: 0.85rem;'>"
        html_table += "<tr style='background-color: #0a0e1a; border-bottom: 2px solid #00d4ff;'>"
        
        for col in df_display.columns:
            html_table += f"<th style='padding: 12px; text-align: left; color: #00d4ff; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #00d4ff;'>{col}</th>"
        
        html_table += "</tr>"
        
        for idx, row in df_display.iterrows():
            severity = row['Severity']
            if severity == 'HIGH':
                row_color = 'rgba(255, 71, 87, 0.15)'
                border_left = '3px solid #ff4757'
            elif severity == 'MEDIUM':
                row_color = 'rgba(255, 165, 2, 0.15)'
                border_left = '3px solid #ffa502'
            else:  # LOW
                row_color = 'rgba(46, 213, 115, 0.15)'
                border_left = '3px solid #2ed573'
            
            html_table += f"<tr style='background-color: {row_color}; border-bottom: 1px solid #1a2332; border-left: {border_left};'>"
            
            for col in df_display.columns:
                if col == 'Severity':
                    if severity == 'HIGH':
                        badge = f"<span class='badge-high'>{severity}</span>"
                    elif severity == 'MEDIUM':
                        badge = f"<span class='badge-medium'>{severity}</span>"
                    else:
                        badge = f"<span class='badge-low'>{severity}</span>"
                    html_table += f"<td style='padding: 12px; color: #e0e0e0; border-bottom: 1px solid #1a2332;'>{badge}</td>"
                else:
                    html_table += f"<td style='padding: 12px; color: #e0e0e0; border-bottom: 1px solid #1a2332; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px;'>{row[col]}</td>"
            
            html_table += "</tr>"
        
        html_table += "</table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("No matching threats detected.")

# RIGHT COLUMN: CHARTS
with right_col:
    st.markdown("#### Threat Analytics")
    
    if not df_all.empty:
        # Chart 1: Category Distribution (Bar)
        category_counts = df_all['categories'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        fig_bar = go.Figure(
            data=[go.Bar(
                x=category_counts['Category'],
                y=category_counts['Count'],
                marker=dict(color='#00d4ff'),
                text=category_counts['Count'],
                textposition='auto',
            )]
        )
        
        fig_bar.update_layout(
            title='Threats by Category',
            xaxis_title='Category',
            yaxis_title='Count',
            template='plotly_dark',
            paper_bgcolor='rgba(20, 24, 36, 0.8)',
            plot_bgcolor='rgba(10, 14, 26, 0.5)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=250,
            font=dict(family='Monaco, Courier New, monospace', color='#e0e0e0'),
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Chart 2: Severity Distribution (Donut)
        severity_counts = df_all['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        
        color_map = {'HIGH': '#ff4757', 'MEDIUM': '#ffa502', 'LOW': '#2ed573'}
        colors = [color_map.get(severity, '#00d4ff') for severity in severity_counts['Severity']]
        
        fig_donut = go.Figure(
            data=[go.Pie(
                labels=severity_counts['Severity'],
                values=severity_counts['Count'],
                hole=0.4,
                marker=dict(colors=colors),
                text=severity_counts['Count'],
                textposition='auto',
            )]
        )
        
        fig_donut.update_layout(
            title='Severity Distribution',
            template='plotly_dark',
            paper_bgcolor='rgba(20, 24, 36, 0.8)',
            plot_bgcolor='rgba(10, 14, 26, 0.5)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=250,
            font=dict(family='Monaco, Courier New, monospace', color='#e0e0e0'),
            showlegend=True,
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# ============================================================================
# ROW 3: RECENT BLOCKED INTERACTIONS
# ============================================================================

st.markdown("### 🚨 **RECENT BLOCKED INTERACTIONS**")

if not df_all.empty:
    blocked_df = df_all[(df_all['action'] == 'block') & (df_all['severity'] == 'HIGH')]
    
    if not blocked_df.empty:
        for idx, row in blocked_df.head(5).iterrows():
            expander_title = f"🔴 [{row['timestamp']}] {row['categories'].upper()} - {row['user_input'][:50]}..."
            
            with st.expander(expander_title):
                st.markdown(f"""
                <div style="
                    background-color: rgba(255, 71, 87, 0.1);
                    border: 2px solid #ff4757;
                    border-radius: 6px;
                    padding: 1.5rem;
                    font-family: 'Monaco', 'Courier New', monospace;
                ">
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #ff4757; font-weight: bold; margin-bottom: 0.5rem;">📥 USER INPUT:</p>
                        <p style="color: #e0e0e0; background-color: #0a0e1a; padding: 1rem; border-radius: 4px; word-wrap: break-word; white-space: pre-wrap;">{row['user_input']}</p>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <p style="color: #ffa502; font-weight: bold; margin-bottom: 0.5rem;">📤 LLM OUTPUT:</p>
                        <p style="color: #e0e0e0; background-color: #0a0e1a; padding: 1rem; border-radius: 4px; word-wrap: break-word; white-space: pre-wrap;">{row['llm_output']}</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                        <div>
                            <p style="color: #b0b8c1; font-size: 0.85rem; margin-bottom: 0.3rem;">CATEGORY</p>
                            <p style="color: #00d4ff; font-weight: bold;">{row['categories']}</p>
                        </div>
                        <div>
                            <p style="color: #b0b8c1; font-size: 0.85rem; margin-bottom: 0.3rem;">SEVERITY</p>
                            <span class="badge-{row['severity'].lower()}">{row['severity']}</span>
                        </div>
                        <div>
                            <p style="color: #b0b8c1; font-size: 0.85rem; margin-bottom: 0.3rem;">TIMESTAMP</p>
                            <p style="color: #00d4ff; font-weight: bold;">{row['timestamp']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No blocked HIGH severity interactions — system operating normally.")
else:
    st.info("No data available yet.")

# ============================================================================
# AUTO-REFRESH
# ============================================================================

# Add auto-refresh every 5 seconds
st.markdown("""
<script>
    setTimeout(function() {
        window.location.reload();
    }, 5000);
</script>
""", unsafe_allow_html=True)

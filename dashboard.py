import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import time
import random

# CONFIGURATION
st.set_page_config(page_title="AI SOC | Executive View", page_icon="🛡️", layout="wide")
DB_FILE = "soc_database.db"

st.markdown("""
    <style>
        /* Global Styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        .stApp { 
            background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 50%, #0d1117 100%);
            color: #e8eaed;
            font-family: 'Inter', sans-serif;
        }
        
        /* Animated background pattern */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
            animation: bgShift 20s ease-in-out infinite;
        }
        
        @keyframes bgShift {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.1); }
        }
        
        /* Glassmorphism Container */
        .block-container {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            position: relative;
            z-index: 1;
        }
        
        /* Professional Icon Styling */
        .metric-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            animation: iconPulse 2s ease-in-out infinite;
        }
        
        .metric-icon svg {
            width: 28px;
            height: 28px;
        }
        
        @keyframes iconPulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 10px rgba(102, 126, 234, 0.2); }
            50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(102, 126, 234, 0.4); }
        }
        
        .critical-icon {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            animation: criticalPulse 1.5s ease-in-out infinite;
        }
        
        @keyframes criticalPulse {
            0%, 100% { 
                transform: scale(1); 
                box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
            }
            50% { 
                transform: scale(1.1); 
                box-shadow: 0 0 25px rgba(239, 68, 68, 0.6), 0 0 40px rgba(239, 68, 68, 0.3);
            }
        }
        
        .high-risk-icon {
            background: rgba(251, 146, 60, 0.1);
            border-color: rgba(251, 146, 60, 0.3);
        }
        
        .ai-icon {
            background: rgba(139, 92, 246, 0.1);
            border-color: rgba(139, 92, 246, 0.3);
            animation: aiGlow 3s ease-in-out infinite;
        }
        
        @keyframes aiGlow {
            0%, 100% { box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }
            50% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.6), 0 0 30px rgba(139, 92, 246, 0.3); }
        }
        
        .defense-icon {
            background: rgba(34, 197, 94, 0.1);
            border-color: rgba(34, 197, 94, 0.3);
        }
        
        /* Neomorphism Metric Cards */
        .metric-card { 
            background: linear-gradient(145deg, #1c1f35, #161929);
            padding: 30px 25px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 
                8px 8px 16px rgba(0, 0, 0, 0.4),
                -8px -8px 16px rgba(42, 47, 78, 0.15),
                inset 2px 2px 4px rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            transition: left 0.6s ease;
        }
        
        .metric-card:hover::before {
            left: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                12px 12px 24px rgba(0, 0, 0, 0.5),
                -12px -12px 24px rgba(42, 47, 78, 0.2),
                inset 2px 2px 4px rgba(255, 255, 255, 0.03),
                0 0 40px rgba(102, 126, 234, 0.1);
        }
        
        .metric-card h3 {
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 12px;
            margin-top: 8px;
            color: #8b92ab;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .metric-card h2 {
            font-size: 2.8rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: numberCount 0.5s ease-out;
        }
        
        @keyframes numberCount {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Title Styling */
        h1 {
            color: #ffffff;
            font-weight: 700;
            font-size: 2.5rem;
            text-align: center;
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            margin-bottom: 0.5rem;
            letter-spacing: 2px;
            animation: titleFadeIn 1s ease-out;
        }
        
        @keyframes titleFadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h2, h3, h4 { 
            color: #e8eaed;
            font-weight: 600;
        }
        
        /* Header Icons */
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        }
        
        .section-header::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 2px;
            animation: heightGrow 0.5s ease-out;
        }
        
        @keyframes heightGrow {
            from { height: 0; }
            to { height: 24px; }
        }
        
        .section-icon {
            width: 24px;
            height: 24px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Subtitle with glassmorphism */
        .stMarkdown h3 {
            text-align: center;
            color: #8b92ab;
            font-weight: 400;
            font-size: 1.1rem;
            letter-spacing: 1px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(5px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            display: inline-block;
            margin: 0 auto 2rem auto;
            animation: subtitleSlide 0.8s ease-out;
        }
        
        @keyframes subtitleSlide {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* Glassmorphism Panels */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        
        /* Subheaders with accent line */
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            position: relative;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        [data-testid="stMarkdownContainer"] h2::after,
        [data-testid="stMarkdownContainer"] h3::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        /* DataFrame Styling */
        .stDataFrame {
            background: rgba(28, 31, 53, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 
                inset 2px 2px 5px rgba(0, 0, 0, 0.3),
                0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        /* Table Styling */
        table {
            background: rgba(28, 31, 53, 0.6) !important;
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        thead tr th {
            background: rgba(102, 126, 234, 0.15) !important;
            color: #e8eaed !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 12px !important;
        }
        
        tbody tr td {
            background: rgba(28, 31, 53, 0.4) !important;
            color: #b8bcc8 !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            padding: 10px !important;
        }
        
        tbody tr:hover td {
            background: rgba(102, 126, 234, 0.08) !important;
        }
        
        /* Status Badge Styling */
        td:last-child {
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.75rem;
        }
        
        td:contains("Monitored") {
            color: #22c55e !important;
        }
        
        td:contains("ACTIVE") {
            color: #ef4444 !important;
            animation: statusBlink 2s ease-in-out infinite;
        }
        
        td:contains("Inactive") {
            color: #6b7280 !important;
        }
        
        @keyframes statusBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        /* Info boxes */
        .stAlert {
            background: rgba(102, 126, 234, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #e8eaed;
        }
        
        /* Divider */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
            margin: 2rem 0;
            animation: dividerExpand 0.8s ease-out;
        }
        
        @keyframes dividerExpand {
            from { width: 0; opacity: 0; }
            to { width: 100%; opacity: 1; }
        }
        
        /* Loading indicator */
        .loading-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
            background-size: 200% 100%;
            animation: loading 2s linear infinite;
            z-index: 9999;
            opacity: 0.7;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Data refresh pulse */
        .data-fresh {
            animation: dataRefresh 2s ease-in-out;
        }
        
        @keyframes dataRefresh {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* Map container */
        .stDeckGlJsonChart {
            background: rgba(28, 31, 53, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        
        /* Plotly charts glassmorphism */
        .js-plotly-plot {
            background: rgba(28, 31, 53, 0.6) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(28, 31, 53, 0.4);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2, #667eea);
        }
        
        /* Glow effects for critical indicators */
        .glow-red {
            animation: glowRed 2s ease-in-out infinite;
        }
        
        @keyframes glowRed {
            0%, 100% { text-shadow: 0 0 5px #ff0000, 0 0 10px #ff0000; }
            50% { text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000, 0 0 30px #ff0000; }
        }
        
        /* Column containers */
        [data-testid="column"] {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(8px);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def generate_threat_map(df):
    critical_logs = df[df['risk_level'] == 'critical'].copy()
    if critical_logs.empty:
        return pd.DataFrame(columns=['lat', 'lon'])
    
    critical_logs['lat'] = [random.uniform(20, 50) for _ in range(len(critical_logs))]
    critical_logs['lon'] = [random.uniform(-120, 140) for _ in range(len(critical_logs))]
    return critical_logs

# UI LAYOUT 
st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: 3px;">
            AI-POWERED SECURITY OPERATIONS CENTER
        </h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("### Executive Real-Time Dashboard")

# PLACEHOLDER FOR LIVE UPDATES
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        # 1. KPI ROW 
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        if not df.empty:
            crit_count = len(df[df['risk_level'] == 'critical'])
            high_count = len(df[df['risk_level'] == 'high'])
            ai_solved = len(df[df['ai_analysis'] != 'SKIPPED']) - len(df[df['ai_analysis'] == 'PENDING'])
            active_threats = len(df[df['status'] == 'failed'])
        else:
            crit_count, high_count, ai_solved, active_threats = 0, 0, 0, 0

        kpi1.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon critical-icon'>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 9V11M12 15H12.01M5.07183 19H18.9282C20.4678 19 21.4301 17.3333 20.6603 16L13.7321 4C12.9623 2.66667 11.0377 2.66667 10.2679 4L3.33975 16C2.56995 17.3333 3.53223 19 5.07183 19Z" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3>Critical Threats</h3>
                <h2>{crit_count}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        kpi2.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon high-risk-icon'>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="#fb923c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3>High Risk Events</h3>
                <h2>{high_count}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        kpi3.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon ai-icon'>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3>AI Interventions</h3>
                <h2>{ai_solved}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        kpi4.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon defense-icon'>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M9 12L11 14L15 10" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3>Active Defense</h3>
                <h2>{active_threats}</h2>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        #  2. MAP & CHARTS ROW 
        col1, col2 = st.columns([2, 1])
        
        unique_key = time.time()

        with col1:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="#667eea" stroke-width="2"/>
                        <circle cx="12" cy="12" r="3" fill="#667eea"/>
                        <path d="M12 2V4M12 20V22M22 12H20M4 12H2" stroke="#667eea" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600;">Global Threat Origin (Simulated C2)</h3>
                </div>
            """, unsafe_allow_html=True)
            map_data = generate_threat_map(df)
            if not map_data.empty:
                st.map(map_data, zoom=1, use_container_width=True)
            else:
                st.info("No External Threats Detected.")

        with col2:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="3" y="3" width="7" height="7" rx="1" stroke="#667eea" stroke-width="2"/>
                        <rect x="14" y="3" width="7" height="7" rx="1" stroke="#667eea" stroke-width="2"/>
                        <rect x="3" y="14" width="7" height="7" rx="1" stroke="#667eea" stroke-width="2"/>
                        <rect x="14" y="14" width="7" height="7" rx="1" stroke="#667eea" stroke-width="2"/>
                    </svg>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600;">Threat Distribution</h3>
                </div>
            """, unsafe_allow_html=True)
            if not df.empty:
                fig = px.pie(df, names='risk_level', hole=0.4, color='risk_level',
                             color_discrete_map={'critical':'red', 'high':'orange', 'low':'green', 'normal':'blue'})
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8eaed')
                )
                st.plotly_chart(fig, use_container_width=True, key=f"pie_{unique_key}")

        #  3. MITRE MATRIX & LOGS 
        st.markdown("---")
        c1, c2 = st.columns([1, 2])

        with c1:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 3H5C3.89543 3 3 3.89543 3 5V9M15 3H19C20.1046 3 21 3.89543 21 5V9M9 21H5C3.89543 21 3 20.1046 3 19V15M15 21H19C20.1046 21 21 20.1046 21 19V15" stroke="#667eea" stroke-width="2" stroke-linecap="round"/>
                        <rect x="9" y="9" width="6" height="6" stroke="#667eea" stroke-width="2"/>
                    </svg>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600;">MITRE ATT&CK Matrix</h3>
                </div>
            """, unsafe_allow_html=True)
            mitre_data = pd.DataFrame({
                "Tactic": ["Initial Access", "Credential Access", "Defense Evasion", "Impact"],
                "Technique": ["Phishing", "Brute Force (T1110)", "Process Killing (T1489)", "Data Encrypted"],
                "Status": ["Monitored", "ACTIVE", "Monitored", "Inactive"]
            })
            st.table(mitre_data)

        with c2:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 20H21" stroke="#667eea" stroke-width="2" stroke-linecap="round"/>
                        <path d="M16.5 3.5C16.8978 3.10217 17.4374 2.87868 18 2.87868C18.2786 2.87868 18.5544 2.93355 18.8118 3.04015C19.0692 3.14674 19.303 3.30301 19.5 3.5C19.697 3.69698 19.8532 3.9308 19.9598 4.18819C20.0665 4.44558 20.1213 4.72142 20.1213 5C20.1213 5.27857 20.0665 5.55442 19.9598 5.81181C19.8532 6.0692 19.697 6.30301 19.5 6.5L7 19L3 20L4 16L16.5 3.5Z" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600;">Live AI Analysis Feed</h3>
                </div>
            """, unsafe_allow_html=True)
            if not df.empty:
                display_df = df[['timestamp', 'user', 'risk_level', 'ai_analysis']].copy()
                st.dataframe(
                    display_df, 
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            else:
                st.info("Waiting for logs...")

    time.sleep(2)
"""
AuditFlow - Agentic & Explainable Claims Processing
5-Page App: Home, Process Claims, Claim History, Performance Analytics, Policy Library
Dark mode optimized for modern UI
"""

VERSION = "v1.2.0-dark"  # Version tracker for deployment verification

import os
import base64
from datetime import datetime
from pathlib import Path

import streamlit as st
import requests

# Service URLs
ROUTER_URL = os.getenv("ROUTER_SERVICE_URL", "http://localhost:8001")
AGENT_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8003")
REPORTER_URL = os.getenv("REPORTER_SERVICE_URL", "http://localhost:8004")

st.set_page_config(page_title="AuditFlow", page_icon="🔷", layout="wide", initial_sidebar_state="expanded")

# Hero image path
HERO_IMAGE_PATH = Path(__file__).parent / "hero.png"

def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def check_service_health():
    """Check health of all microservices and return status"""
    services_up = 0
    total_services = 3
    
    for url in [ROUTER_URL, AGENT_URL, REPORTER_URL]:
        try:
            resp = requests.get(f"{url}/health", timeout=5)  # Increased timeout for cloud
            if resp.status_code == 200:
                services_up += 1
        except:
            pass
    
    if services_up == total_services:
        return "AGENT ONLINE", "#22C55E"
    elif services_up > 0:
        return "SEMI-FUNCTIONAL", "#F59E0B"
    else:
        return "OFFLINE", "#DC2626"

# CSS - Warm Light Cream Theme  
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-primary: #0F0F0F;
        --bg-secondary: #1A1A1A;
        --bg-card: #1E1E1E;
        --bg-hover: #2A2A2A;
        
        --text-primary: #F5F5F5;
        --text-secondary: #A3A3A3;
        --text-muted: #6B6B6B;
        
        --teal: #14B8A6;
        --teal-light: #2DD4BF;
        --green: #22C55E;
        --amber: #F59E0B;
        --red: #EF4444;
        --blue: #3B82F6;
        --purple: #8B5CF6;
        
        --border: #2A2A2A;
        --border-hover: #3A3A3A;
        --shadow: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-lg: 0 10px 40px rgba(0,0,0,0.4);
    }
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp { 
        background: var(--bg-primary) !important;
    }
    
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 32px 48px !important; max-width: 1400px !important; margin: 0 auto !important; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { 
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
    
    section[data-testid="stSidebar"] button {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        text-align: left !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: var(--teal) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Form elements - FIXED CONTRAST */
    .stTextArea textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1) !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-hover) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--teal) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--teal-light) !important;
    }
    
    /* Sample claim buttons - uniform height */
    [data-testid="column"] .stButton > button {
        min-height: 80px !important;
        white-space: normal !important;
        text-align: left !important;
        padding: 12px 16px !important;
        line-height: 1.4 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; }
    
    /* Alerts */
    .stAlert { background: var(--bg-card) !important; border: 1px solid var(--border) !important; }
    
    /* ========== LAYOUT STYLES ========== */
    .page-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 48px;
    }
    
    .page-header {
        margin-bottom: 32px;
    }
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    .page-subtitle {
        font-size: 15px;
        color: var(--text-secondary);
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 60px 48px 40px;
        max-width: 900px;
        margin: 0 auto;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 100px;
        font-size: 12px;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 28px;
    }
    .hero-badge-dot {
        width: 6px;
        height: 6px;
        background: var(--green);
        border-radius: 50%;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
    }
    .hero-title {
        font-size: 52px;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        margin-bottom: 20px;
        letter-spacing: -0.02em;
    }
    .hero-gradient {
        background: linear-gradient(135deg, var(--teal) 0%, var(--blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 18px;
        color: var(--text-secondary);
        max-width: 560px;
        margin: 0 auto 36px;
        line-height: 1.7;
    }
    .hero-buttons {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-bottom: 48px;
    }
    .hero-btn {
        padding: 14px 28px;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none !important;
    }
    .hero-btn-primary {
        background: var(--text-primary);
        color: white !important;
    }
    .hero-btn-primary:hover { opacity: 0.9; }
    .hero-btn-secondary {
        background: var(--bg-card);
        color: var(--text-primary) !important;
        border: 1px solid var(--border);
    }
    .hero-btn-secondary:hover { background: var(--bg-hover); }
    
    .hero-image {
        max-width: 600px;
        margin: 0 auto;
        border-radius: 16px;
        box-shadow: var(--shadow-lg);
    }
    
    /* Features */
    .features-section {
        padding: 60px 48px;
        max-width: 1100px;
        margin: 0 auto;
    }
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
    }
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 28px;
        transition: all 0.2s;
    }
    .feature-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    .feature-icon {
        width: 48px;
        height: 48px;
        background: var(--bg-secondary);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .feature-title {
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 10px;
    }
    .feature-desc {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 48px;
        border-top: 1px solid var(--border);
        background: var(--bg-secondary);
    }
    .footer-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 16px;
    }
    .footer-copy {
        font-size: 13px;
        color: var(--text-muted);
    }
    
    /* Stats Grid */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
    }
    .stat-label {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
    }
    .stat-delta {
        font-size: 12px;
        margin-top: 6px;
        color: var(--green);
        font-weight: 500;
    }
    
    /* Content Card */
    .content-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .content-card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 16px;
    }
    
    /* Sample Claims - Equal sized grid */
    .sample-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 100%;
        min-height: 120px;
        display: flex;
        flex-direction: column;
    }
    .sample-card:hover {
        border-color: var(--teal);
        background: var(--bg-card);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .sample-id {
        font-size: 11px;
        font-weight: 700;
        color: var(--teal);
        font-family: 'SF Mono', Monaco, monospace;
        margin-bottom: 8px;
    }
    .sample-text {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
        flex: 1;
    }
    .sample-meta {
        font-size: 11px;
        color: var(--text-muted);
        margin-top: 10px;
    }
    
    /* Status dot styling */
    .status-dot {
        display: inline-block;
    }
    
    /* Workflow */
    .workflow-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
    }
    .workflow-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .workflow-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
    }
    .workflow-badge {
        font-size: 10px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        text-transform: uppercase;
        background: var(--bg-secondary);
        color: var(--text-muted);
    }
    .workflow-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        font-size: 13px;
        color: var(--text-secondary);
    }
    .workflow-step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--border);
    }
    
    /* Policy Card */
    .policy-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: all 0.2s;
    }
    .policy-card:hover {
        box-shadow: var(--shadow);
        border-color: var(--border-hover);
    }
    .policy-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 14px;
    }
    .policy-icon.home { background: #DBEAFE; }
    .policy-icon.auto { background: #FCE7F3; }
    .policy-icon.business { background: #EDE9FE; }
    .policy-icon.cyber { background: #CCFBF1; }
    .policy-icon.liability { background: #FEF3C7; }
    .policy-icon.workers { background: #FEE2E2; }
    .policy-name {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .policy-version {
        font-size: 11px;
        color: var(--text-muted);
        font-family: monospace;
    }
    .policy-badge {
        display: inline-block;
        font-size: 9px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    .policy-badge.active { background: #DCFCE7; color: #166534; }
    .policy-badge.review { background: #FEF3C7; color: #92400E; }
    .policy-badge.archived { background: #F3F4F6; color: #6B7280; }
    .policy-meta {
        font-size: 12px;
        color: var(--text-muted);
        margin: 10px 0;
    }
    .policy-sections {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 12px;
    }
    .policy-tag {
        font-size: 10px;
        padding: 4px 8px;
        background: var(--bg-secondary);
        border-radius: 4px;
        color: var(--text-secondary);
    }
    
    /* Table */
    .table-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    .table-header {
        display: grid;
        grid-template-columns: 140px 1fr 100px 100px 100px;
        gap: 12px;
        padding: 14px 20px;
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border);
    }
    .table-empty {
        padding: 48px;
        text-align: center;
        color: var(--text-muted);
    }
    
    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .kpi-card {
        background: var(--bg-secondary);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
    }
    .kpi-label {
        font-size: 10px;
        color: var(--text-muted);
        text-transform: uppercase;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# POLICIES - Matching backend (MSIG HomePlus SG + Zurich Business AU)
POLICIES = [
    {"name": "MSIG Enhanced HomePlus", "version": "v2.4", "status": "active", "icon": "🏠", "cat": "home", "region": "SG", "sections": ["Dwelling", "Personal Property", "Liability", "Loss of Use"]},
    {"name": "Zurich Business Insurance", "version": "v3.1", "status": "active", "icon": "🏢", "cat": "business", "region": "AU", "sections": ["Building", "Stock", "Business Interruption"]},

]

# SAMPLES
SAMPLES = [
    {"id": "CLM-001", "text": "Water leak from air-con unit in Bedok caused damage to living room floor and furniture.", "exp": "COVERED"},
    {"id": "CLM-002", "text": "Machinery breakdown at Sydney warehouse. Conveyor belt motor failed suddenly during operations.", "exp": "COVERED"},
    {"id": "CLM-003", "text": "Fire damage to Melbourne business premises. Electrical fault destroyed inventory and equipment.", "exp": "COVERED"},
    {"id": "CLM-004", "text": "Pipe burst in Tampines HDB flat flooding the kitchen, bedroom and living areas.", "exp": "COVERED"},
    {"id": "CLM-005", "text": "Ransomware attack encrypted all Adelaide office data and servers. Business operations halted.", "exp": "NOT_COVERED"},
    {"id": "CLM-006", "text": "Mould growing on Woodlands flat walls for several months. Gradual deterioration observed.", "exp": "NOT_COVERED"},
]

# Session state
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'claim_text' not in st.session_state: st.session_state.claim_text = ""
if 'history' not in st.session_state: st.session_state.history = []
if 'analysis_result' not in st.session_state: st.session_state.analysis_result = None
if 'override_logs' not in st.session_state: st.session_state.override_logs = []
if 'current_claim_id' not in st.session_state: st.session_state.current_claim_id = None

# SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 20px 16px; border-bottom: 1px solid #2A2A2A;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #14B8A6, #3B82F6); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 12px;">AF</div>
            <div>
                <div style="font-size: 16px; font-weight: 700; color: #F5F5F5;">AuditFlow</div>
                <div style="font-size: 10px; color: #6B6B6B;">AI Claims Processing • {VERSION}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    pages = [("🏠", "Home", "home"), ("📝", "Process Claims", "process"), ("📋", "Claim History", "history"), ("📊", "Performance", "performance"), ("📚", "Policy Library", "policies")]
    
    for icon, label, page in pages:
        if st.button(f"{icon}  {label}", use_container_width=True, type="primary" if st.session_state.page == page else "secondary", key=f"nav_{page}"):
            st.session_state.page = page
            st.rerun()

# ===== HOME =====
if st.session_state.page == 'home':
    hero_img = get_base64_image(HERO_IMAGE_PATH)
    status_text, status_color = check_service_health()
    
    st.markdown(f'''
    <div class="hero-section">
        <div class="hero-badge"><div class="status-dot" style="background: {status_color};"></div> {status_text}</div>
        <h1 class="hero-title">Modernizing Insurance<br>Audits <span class="hero-gradient">with AI</span></h1>
        <p class="hero-subtitle">Replace manual claim reviews with intelligent, real-time reasoning. AuditFlow brings clarity to complexity, instantly verifying policies and detecting anomalies.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Buttons using Streamlit
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.page = 'process'
            st.rerun()
    
    # Hero Image with animation wrapper
    if hero_img:
        st.markdown(f'<div class="hero-image-wrapper" style="text-align: center; padding: 20px 48px;"><img src="data:image/png;base64,{hero_img}" style="max-width: 550px; width: 100%; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    
    # Features
    st.markdown("""
    <div class="features-section">
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">The Problem</div>
                <div class="feature-desc">Manual auditing is slow, expensive, and error-prone. Claims sit in queues for days while adjusters struggle with document overload.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">The Solution</div>
                <div class="feature-desc">AuditFlow AI understands context, comprehending the "why" behind claims and cross-referencing policy pages in milliseconds.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✨</div>
                <div class="feature-title">Product Offering</div>
                <div class="feature-desc">Real-time analysis via Dashboard or API. Instant policy verification, fraud scoring, and automated decision drafting.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Documentation link
    st.markdown("<div style='text-align: center; padding: 20px;'><a href='https://github.com/SmridhVarma/AuditFlow' target='_blank' style='color: #A3A3A3; text-decoration: none; font-size: 14px;'>📖 View Documentation on GitHub →</a></div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div class="footer-logo">
            <div style="width: 24px; height: 24px; background: linear-gradient(135deg, #0D9488, #2563EB); border-radius: 6px;"></div>
            <span style="font-weight: 600; color: #1C1917;">AuditFlow</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== PROCESS CLAIMS =====
elif st.session_state.page == 'process':
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<div class="page-header"><div class="page-title">Claims Processing</div><div class="page-subtitle">Submit and analyze insurance claims with AI</div></div>', unsafe_allow_html=True)
    
    # Stats - 6 metrics including SLA and Avg Processing
    st.markdown("""
    <div class="stats-container" style="grid-template-columns: repeat(6, 1fr);">
        <div class="stat-card"><div class="stat-label">Total Claims</div><div class="stat-value">0</div></div>
        <div class="stat-card"><div class="stat-label">Approved</div><div class="stat-value" style="color:#22C55E;">0</div></div>
        <div class="stat-card"><div class="stat-label">Denied</div><div class="stat-value" style="color:#DC2626;">0</div></div>
        <div class="stat-card"><div class="stat-label">Avg Confidence</div><div class="stat-value">0%</div></div>
        <div class="stat-card"><div class="stat-label">Avg Processing</div><div class="stat-value">0s</div></div>
        <div class="stat-card"><div class="stat-label">SLA Compliance</div><div class="stat-value">0%</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### 📝 Claim Description")
        claim_text = st.text_area("", value=st.session_state.claim_text, height=120, placeholder="Describe the claim incident in detail, or select a sample claim below...", label_visibility="collapsed", key="claim_input")
        
        analyze_col, clear_col = st.columns([3, 1])
        with analyze_col:
            analyze_clicked = st.button("⚡ Analyze Claim", type="primary", use_container_width=True)
        with clear_col:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.claim_text = ""
                st.session_state.analysis_result = None
                st.session_state.pdf_data = None
                st.session_state.pdf_claim_id = None
                st.rerun()
        
        if analyze_clicked:
            if claim_text and len(claim_text) > 10:
                import random
                from datetime import datetime
                claim_id = f"CLM-{random.randint(1000, 9999)}"
                st.session_state.current_claim_id = claim_id
                
                # Find matching sample for expected result
                expected = "COVERED"
                for sample in SAMPLES:
                    if sample["text"] in claim_text or claim_text in sample["text"]:
                        expected = sample["exp"]
                        break
                
                # Simulate detailed analysis with workflow events
                confidence = random.uniform(0.75, 0.98)
                
                # Determine region and category first
                claim_region = "SG" if "singapore" in claim_text.lower() or "bedok" in claim_text.lower() or "tampines" in claim_text.lower() or "woodlands" in claim_text.lower() else "AU"
                claim_category = "home" if any(w in claim_text.lower() for w in ["flat", "hdb", "room", "kitchen", "bedroom"]) else "business"

                # Determine policy based on text
                policy_name = "MSIG Enhanced HomePlus" if "SG" == claim_region else "Zurich Business Insurance"
                section_cited = "Section 3.2 (Water Damage)" if "water" in claim_text.lower() or "leak" in claim_text.lower() else "Section 5.1 (Fire & Perils)" if "fire" in claim_text.lower() else "Section 2.4 (Machinery)" 
                
                st.session_state.analysis_result = {
                    "claim_id": claim_id,
                    "claim_text": claim_text,
                    "decision": expected,
                    "confidence": confidence,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "region": claim_region,
                    "category": claim_category,
                    "summary": f"Claim analyzed based on policy coverage criteria. Decision: {expected} with {confidence*100:.1f}% confidence.",
                    "events": [
                        {"time": "00:00.12", "component": "ROUTER", "icon": "🔀", "action": "Route Request", "details": f"Routing to {claim_region} / {claim_category} handler"},
                        {"time": "00:00.45", "component": "AGENT", "icon": "🧠", "action": "Analyze Intent", "details": "Identified claim type: Property Damage (Water/Fire)"},
                        {"time": "00:01.20", "component": "RAG", "icon": "📚", "action": "Retrieve Policy", "details": f"Searching vector DB for '{policy_name}'"},
                        {"time": "00:01.85", "component": "RAG", "icon": "📄", "action": "Cite Policy", "details": f"Retrieved {policy_name}", "citation": section_cited},
                        {"time": "00:02.30", "component": "AGENT", "icon": "⚖️", "action": "Evaluate Coverage", "details": f"Checking exclusions against {section_cited}"},
                        {"time": "00:02.90", "component": "AGENT", "icon": "✅", "action": "Generate Decision", "details": f"Determined outcome: {expected}"}
                    ],
                    "reasoning": [
                        {"step": 1, "type": "THINK", "content": "Parsing claim description to identify incident type and location..."},
                        {"step": 2, "type": "ACT", "content": "Querying policy database for relevant coverage clauses..."},
                        {"step": 3, "type": "OBSERVE", "content": f"Found matching policy for {('Singapore Home' if 'SG' in claim_text else 'Australia Business')} category."},
                        {"step": 4, "type": "THINK", "content": "Evaluating exclusions and coverage limits..."},
                        {"step": 5, "type": "DECIDE", "content": f"Final decision: {expected}. Confidence score: {confidence*100:.1f}%"},
                    ],
                    "flags": [
                        {"criteria": "High Value Claim", "triggered": confidence < 0.85, "reason": "Confidence below 85% threshold"},
                        {"criteria": "Gradual Damage", "triggered": "gradual" in claim_text.lower() or "mould" in claim_text.lower(), "reason": "Potential gradual damage - typically excluded"},
                        {"criteria": "Cyber Incident", "triggered": "ransomware" in claim_text.lower() or "cyber" in claim_text.lower(), "reason": "Cyber coverage requires separate policy"},
                    ],
                    "overridden": False,
                    "override_info": None
                }
                st.rerun()

            else:
                st.warning("Please enter a claim description or select a sample claim.")
        
        # Display Analysis Results
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            
            st.markdown("---")
            st.markdown("#### 📊 Analysis Results")
            
            # Decision card
            decision_color = "#22C55E" if result["decision"] == "COVERED" else "#DC2626" if result["decision"] == "NOT_COVERED" else "#F59E0B"
            final_decision = result.get("override_info", {}).get("new_decision", result["decision"]) if result.get("overridden") else result["decision"]
            
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, {decision_color}15, {decision_color}05); border: 2px solid {decision_color}; border-radius: 12px; padding: 20px; margin: 12px 0;">
                <div style="font-size: 12px; color: #57534E; margin-bottom: 8px;">CLAIM {result["claim_id"]} • {result["timestamp"]}</div>
                <div style="font-size: 28px; font-weight: 700; color: {decision_color};">{final_decision}</div>
                <div style="font-size: 14px; color: #57534E; margin-top: 8px;">Confidence: {result["confidence"]*100:.1f}%</div>
                {"<div style='font-size: 11px; color: #F59E0B; margin-top: 8px;'>⚠️ DECISION OVERRIDDEN</div>" if result.get("overridden") else ""}
            </div>
            ''', unsafe_allow_html=True)
            
            # Flagging Criteria
            active_flags = [f for f in result.get("flags", []) if f["triggered"]]
            if active_flags:
                st.markdown("##### 🚩 Flagging Criteria")
                for flag in active_flags:
                    st.warning(f"**{flag['criteria']}**: {flag['reason']}")
            
            # Agent Reasoning
            with st.expander("🧠 Agent Reasoning & Explanations", expanded=False):
                for step in result.get("reasoning", []):
                    step_color = {"THINK": "#3B82F6", "ACT": "#8B5CF6", "OBSERVE": "#22C55E", "DECIDE": "#0D9488"}.get(step["type"], "#6B7280")
                    st.markdown(f'''
                    <div style="border-left: 3px solid {step_color}; padding-left: 12px; margin: 8px 0;">
                        <div style="font-size: 11px; font-weight: 600; color: {step_color};">Step {step["step"]} [{step["type"]}]</div>
                        <div style="font-size: 13px; color: #44403C;">{step["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Download Report Button
            st.markdown("##### 📥 Download Report")
            
            # Initialize session state for PDF if not exists
            if 'pdf_data' not in st.session_state:
                st.session_state.pdf_data = None
            if 'pdf_claim_id' not in st.session_state:
                st.session_state.pdf_claim_id = None
            
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                # Check if we already have the PDF for this claim
                if st.session_state.pdf_data and st.session_state.pdf_claim_id == result["claim_id"]:
                    st.download_button(
                        "⬇️ Save PDF Report",
                        data=st.session_state.pdf_data,
                        file_name=f"audit_report_{result['claim_id']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    if st.button("📄 Generate PDF Report", use_container_width=True, type="primary"):
                        try:
                            with st.spinner("Generating PDF report..."):
                                report_data = {
                                    "claim_id": result["claim_id"],
                                    "claim_text": result["claim_text"],
                                    "region": result["region"],
                                    "category": result["category"],
                                    "decision": final_decision,
                                    "confidence": result["confidence"],
                                    "summary": result["summary"],
                                    "reasoning_trace": [{"step_number": r["step"], "step_type": r["type"], "content": r["content"]} for r in result.get("reasoning", [])],
                                    "evidence": [],
                                    "exclusions_found": [f["reason"] for f in active_flags],
                                    "limits_found": []
                                }
                                response = requests.post(f"{REPORTER_URL}/generate-report", json=report_data, timeout=30)
                                if response.status_code == 200:
                                    st.session_state.pdf_data = response.content
                                    st.session_state.pdf_claim_id = result["claim_id"]
                                    st.rerun()
                                else:
                                    st.error(f"Report service error: {response.status_code} - {response.text[:100]}")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Could not connect to Reporter service. Is it running?")
                        except requests.exceptions.Timeout:
                            st.error("❌ Reporter service timed out. Try again.")
                        except Exception as e:
                            st.error(f"Error generating report: {str(e)[:100]}")
            
            # Override Decision Module
            st.markdown("---")
            st.markdown("##### ⚖️ Override Decision")
            
            if result.get("overridden"):
                override = result["override_info"]
                st.info(f"✅ Decision overridden from **{override['original_decision']}** to **{override['new_decision']}** by {override['adjuster']} on {override['timestamp']}")
                st.caption(f"Reason: {override['reason']} | Notes: {override['notes']}")
            else:
                with st.form("override_form"):
                    st.caption("Override the AI decision if manual review indicates otherwise")
                    override_reason = st.selectbox("Override Reason", ["Manager Approval", "Additional Documentation", "Customer Exception", "Policy Clarification", "Error Correction", "Other"])
                    new_decision = st.selectbox("New Decision", ["COVERED", "NOT_COVERED", "PARTIAL", "NEEDS_REVIEW"])
                    adjuster_notes = st.text_area("Adjuster Notes", placeholder="Enter justification for override...", height=80)
                    
                    if st.form_submit_button("✓ Confirm Override", type="primary"):
                        if adjuster_notes.strip():
                            override_entry = {
                                "claim_id": result["claim_id"],
                                "original_decision": result["decision"],
                                "new_decision": new_decision,
                                "reason": override_reason,
                                "notes": adjuster_notes,
                                "adjuster": "Current User",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.analysis_result["overridden"] = True
                            st.session_state.analysis_result["override_info"] = override_entry
                            st.session_state.override_logs.append(override_entry)
                            st.rerun()
                        else:
                            st.warning("Please enter adjuster notes to justify the override.")
            
            # Override Logs
            if st.session_state.override_logs:
                with st.expander("📜 Override Log History", expanded=False):
                    for log in reversed(st.session_state.override_logs[-5:]):
                        st.markdown(f"**{log['claim_id']}**: {log['original_decision']} → {log['new_decision']} ({log['reason']}) - {log['timestamp']}")
        
        # Sample Claims section
        # Sample Claims in Expander to clean up UI
        with st.expander("🎯 Load Sample Claim", expanded=not st.session_state.analysis_result):
            st.caption("Select a sample to auto-fill the description:")
            for row in range(0, len(SAMPLES), 2):
                cols = st.columns(2, gap="small")
                for col_idx in range(2):
                    idx = row + col_idx
                    if idx < len(SAMPLES):
                        sample = SAMPLES[idx]
                        with cols[col_idx]:
                            if st.button(f"📋 {sample['id']}: {sample['text'][:40]}...", key=f"sample_{idx}", use_container_width=True, help=f"Expected: {sample['exp']}"):
                                st.session_state.claim_text = sample['text']
                                st.session_state.analysis_result = None
                                st.rerun()
    
    with col2:
        st.markdown("#### System Activity")
        
        if st.session_state.analysis_result:
            events = st.session_state.analysis_result.get("events", [])
            for event in events:
                citation_html = f'<div style="margin-top:4px; padding:4px 8px; background:#EFF6FF; border-left:2px solid #3B82F6; color:#1E40AF; font-size:11px; border-radius:4px;">⚖️ Cited: {event["citation"]}</div>' if event.get("citation") else ""
                
                st.markdown(f'''
                <div style="display:flex; gap:12px; margin-bottom:16px; align-items:flex-start;">
                    <div style="width:24px; font-size:18px; text-align:center;">{event["icon"]}</div>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:12px; color:#1C1917;">{event["component"]}</span>
                            <span style="font-size:10px; color:#9CA3AF; font-family:monospace;">{event["time"]}</span>
                        </div>
                        <div style="font-size:13px; color:#44403C; font-weight:500;">{event["action"]}</div>
                        <div style="font-size:12px; color:#57534E; margin-top:2px;">{event["details"]}</div>
                        {citation_html}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown(f'''
            <div style="text-align:center; padding-top:20px; border-top:1px dashed #E5E7EB;">
                <span style="color:#22C55E; font-weight:600; font-size:12px;">● PROCESSING COMPLETE</span>
            </div>
            ''', unsafe_allow_html=True)
            
        else:
            # Idle state
            st.info("System is ready. Submit a claim to view the agentic workflow in real-time.")
            st.markdown("""
            <div style="opacity:0.5; filter:grayscale(1);">
                <div style="display:flex; gap:12px; margin-bottom:16px; align-items:center;">
                    <div style="width:24px; font-size:18px;">🔀</div>
                    <div><div style="font-size:12px; font-weight:700;">ROUTER</div><div style="font-size:12px;">Route Request</div></div>
                </div>
                <div style="display:flex; gap:12px; margin-bottom:16px; align-items:center;">
                    <div style="width:24px; font-size:18px;">🧠</div>
                    <div><div style="font-size:12px; font-weight:700;">AGENT</div><div style="font-size:12px;">Analyze Intent</div></div>
                </div>
                <div style="display:flex; gap:12px; margin-bottom:16px; align-items:center;">
                    <div style="width:24px; font-size:18px;">📚</div>
                    <div><div style="font-size:12px; font-weight:700;">RAG</div><div style="font-size:12px;">Retrieve Policy</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== CLAIM HISTORY =====
elif st.session_state.page == 'history':
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<div class="page-header"><div class="page-title">Claim History</div><div class="page-subtitle">View and manage processed claims</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="stats-container">
        <div class="stat-card"><div class="stat-label">Approval Rate</div><div class="stat-value">0%</div></div>
        <div class="stat-card"><div class="stat-label">Avg Processing</div><div class="stat-value">0s</div></div>
        <div class="stat-card"><div class="stat-label">Avg Confidence</div><div class="stat-value">0%</div></div>
        <div class="stat-card"><div class="stat-label">SLA Compliance</div><div class="stat-value">0%</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="table-card">
        <div class="table-header"><div>CLAIM ID</div><div>DESCRIPTION</div><div>CATEGORY</div><div>AMOUNT</div><div>STATUS</div></div>
        <div class="table-empty">No claims processed yet. Submit a claim to get started.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== PERFORMANCE =====
elif st.session_state.page == 'performance':
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<div class="page-header"><div class="page-title">Performance Analytics</div><div class="page-subtitle">Monitor system KPIs and metrics</div></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="stats-container">
        <div class="stat-card"><div class="stat-label">Claims Processed</div><div class="stat-value">0</div></div>
        <div class="stat-card"><div class="stat-label">Approval Rate</div><div class="stat-value">0%</div></div>
        <div class="stat-card"><div class="stat-label">Avg Processing</div><div class="stat-value">0s</div></div>
        <div class="stat-card"><div class="stat-label">SLA Compliance</div><div class="stat-value">0%</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-card">
            <div class="content-card-title">🌍 Regional Distribution</div>
            <div style="margin-top: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;"><span style="color: #57534E;">🇸🇬 Singapore</span><span style="font-weight: 600;">0 (0%)</span></div>
                <div style="display: flex; justify-content: space-between;"><span style="color: #57534E;">🇦🇺 Australia</span><span style="font-weight: 600;">0 (0%)</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <div class="content-card-title">⏱️ Processing Efficiency</div>
            <div class="kpi-grid" style="margin-top: 12px;">
                <div class="kpi-card"><div class="kpi-value">0s</div><div class="kpi-label">Avg Time</div></div>
                <div class="kpi-card"><div class="kpi-value">10s</div><div class="kpi-label">SLA Target</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== POLICY LIBRARY =====
elif st.session_state.page == 'policies':
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    st.markdown('<div class="page-header"><div class="page-title">Policy Library</div><div class="page-subtitle">Manage insurance policy definitions and coverage rules</div></div>', unsafe_allow_html=True)
    
    # Use Streamlit columns for proper grid
    cols = st.columns(3)
    
    for i, policy in enumerate(POLICIES):
        with cols[i % 3]:
            sections_html = ''.join([f'<span class="policy-tag">{s}</span>' for s in policy['sections']])
            flag = {"US": "🇺🇸", "CA": "🇨🇦", "UK": "🇬🇧", "EU": "🇪🇺"}.get(policy['region'], "🌍")
            
            st.markdown(f"""
            <div class="policy-card">
                <div class="policy-icon {policy['cat']}">{policy['icon']}</div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div class="policy-name">{policy['name']}</div>
                        <div class="policy-version">{policy['version']}</div>
                    </div>
                    <span class="policy-badge {policy['status']}">{policy['status'].upper()}</span>
                </div>
                <div class="policy-meta">{flag} {policy['region']} Region</div>
                <div class="policy-sections">{sections_html}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

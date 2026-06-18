"""
Open Deep Research Agent
AI-Powered Research Automation System
======================================
Main Streamlit application entry point.
Run with: streamlit run app.py
"""

import time
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from agents.planner_agent import planner_agent, is_valid_url
from agents.searcher_agent import searcher_agent
from agents.writer_agent import writer_agent
from database.history_manager import (
    init_history, add_to_history, get_history, clear_history
)
from utils.helpers import (
    word_count_badge, generate_pdf_placeholder, sanitize_filename, truncate
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Open Deep Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── Root tokens ── */
:root {
    --blue-900: #0B1F4A;
    --blue-700: #1A3A8F;
    --blue-500: #2563EB;
    --blue-400: #3B82F6;
    --blue-100: #DBEAFE;
    --blue-50:  #EFF6FF;
    --accent:   #06B6D4;   /* cyan accent — the one risk */
    --white:    #FFFFFF;
    --gray-50:  #F8FAFC;
    --gray-100: #F1F5F9;
    --gray-200: #E2E8F0;
    --gray-500: #64748B;
    --gray-700: #334155;
    --gray-900: #0F172A;
    --success:  #10B981;
    --warning:  #F59E0B;
    --radius:   12px;
    --shadow:   0 4px 24px rgba(11,31,74,0.10);
    --shadow-lg:0 8px 40px rgba(11,31,74,0.16);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--gray-900);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 1100px; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, var(--blue-900) 0%, var(--blue-700) 60%, #1e40af 100%);
    border-radius: 0 0 var(--radius) var(--radius);
    padding: 48px 40px 40px;
    margin: -1rem -1rem 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    width: 500px; height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 70%);
    top: -150px; right: -100px;
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 12px;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(28px, 4vw, 44px);
    font-weight: 700;
    color: var(--white);
    line-height: 1.15;
    margin: 0 0 10px;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-size: 16px;
    color: rgba(255,255,255,0.72);
    max-width: 560px;
    line-height: 1.6;
    margin: 0 0 28px;
}
.hero-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.badge {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.88);
    backdrop-filter: blur(4px);
}

/* ── Section labels ── */
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--blue-500);
    margin-bottom: 6px;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--blue-900);
    margin: 0 0 20px;
}

/* ── Feature cards ── */
.feature-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 28px; }
.feature-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 20px;
    transition: box-shadow .2s, transform .2s;
}
.feature-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.feature-icon { font-size: 26px; margin-bottom: 10px; }
.feature-name { font-weight: 600; font-size: 14px; color: var(--blue-900); margin-bottom: 4px; }
.feature-desc { font-size: 13px; color: var(--gray-500); line-height: 1.5; }

/* ── Architecture boxes ── */
.arch-flow {
    display: flex; align-items: center; gap: 0;
    background: var(--blue-50);
    border-radius: var(--radius);
    padding: 18px 24px;
    margin-bottom: 28px;
    flex-wrap: wrap;
}
.arch-node {
    background: var(--white);
    border: 2px solid var(--blue-100);
    border-radius: 8px;
    padding: 12px 18px;
    text-align: center;
    min-width: 110px;
}
.arch-node-icon { font-size: 22px; }
.arch-node-label { font-size: 11px; font-weight: 600; color: var(--blue-700); margin-top: 4px; }
.arch-arrow { color: var(--blue-400); font-size: 20px; padding: 0 10px; font-weight: 700; }

/* ── Input card ── */
.input-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 28px 28px 20px;
    box-shadow: var(--shadow);
    margin-bottom: 24px;
}

/* ── Progress step ── */
.step-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.step-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }
.step-dot.done { background: var(--success); }
.step-dot.waiting { background: var(--gray-200); }
.step-text { font-size: 14px; color: var(--gray-700); }
.step-text.done { color: var(--success); font-weight: 500; }
.step-text.active { color: var(--blue-700); font-weight: 600; }

/* ── Result sections ── */
.result-card {
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(11,31,74,0.06);
}
.result-card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--blue-900);
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}
.result-card-title .icon { font-size: 18px; }

/* ── Finding item ── */
.finding-item {
    display: flex; gap: 12px; align-items: flex-start;
    background: var(--gray-50);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 14px;
    color: var(--gray-700);
    line-height: 1.55;
}
.finding-num {
    font-weight: 700;
    color: var(--blue-500);
    font-size: 13px;
    min-width: 20px;
}

/* ── Source pill ── */
.source-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px;
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 13px;
}
.source-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--blue-500); flex-shrink: 0; }
.source-title { font-weight: 500; color: var(--blue-900); }
.source-meta { color: var(--gray-500); font-size: 11px; margin-left: 4px; }
.source-url { color: var(--blue-400); font-size: 11px; margin-left: auto; word-break: break-all; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--blue-900) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--white) !important; }
.sidebar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px; font-weight: 700;
    color: var(--white) !important;
    margin-bottom: 4px;
}
.sidebar-sub { font-size: 11px; color: var(--accent) !important; letter-spacing: 1px; }
.sidebar-divider { border-top: 1px solid rgba(255,255,255,0.10); margin: 12px 0; }
.hist-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    cursor: pointer;
}
.hist-type { font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
.hist-type.topic { color: var(--accent) !important; }
.hist-type.url { color: #A78BFA !important; }
.hist-subject { font-size: 13px; color: rgba(255,255,255,0.9) !important; margin: 2px 0; }
.hist-time { font-size: 11px; color: rgba(255,255,255,0.45) !important; }

/* ── Info / alert strip ── */
.info-strip {
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: var(--blue-700);
    margin-bottom: 16px;
    display: flex; gap: 10px; align-items: flex-start;
}
.error-strip {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #B91C1C;
    margin-bottom: 16px;
}
.success-strip {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #15803D;
    margin-bottom: 16px;
}

/* ── Stat cards ── */
.stat-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 110px;
    background: var(--white);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: 16px;
    text-align: center;
}
.stat-val { font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700; color: var(--blue-700); }
.stat-lbl { font-size: 11px; color: var(--gray-500); font-weight: 500; letter-spacing: 0.5px; margin-top: 2px; }

/* ── Footer ── */
.footer {
    margin-top: 48px;
    padding: 28px 0 12px;
    border-top: 1px solid var(--gray-200);
    text-align: center;
}
.footer-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 15px;
    color: var(--blue-900);
    margin-bottom: 4px;
}
.footer-sub { font-size: 12px; color: var(--gray-500); }
.team-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 16px 0; }
.team-pill {
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 500;
    color: var(--blue-700);
}
.footer-links { display: flex; justify-content: center; gap: 20px; margin-top: 12px; }
.footer-link { font-size: 12px; color: var(--blue-500); text-decoration: none; }

/* ── Button overrides ── */
.stButton > button {
    background: linear-gradient(135deg, var(--blue-500), var(--blue-700)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 32px !important;
    transition: opacity .2s !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Responsive ── */
@media (max-width: 720px) {
    .feature-grid { grid-template-columns: 1fr; }
    .arch-flow { flex-direction: column; }
    .hero { padding: 32px 20px 28px; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
init_history()
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "nav" not in st.session_state:
    st.session_state.nav = "🏠 Home"
if "view_history_id" not in st.session_state:
    st.session_state.view_history_id = None


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">🔬 Open Deep Research</div>
    <div class="sidebar-sub">AI Research Automation System</div>
    <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "Navigate",
        ["🏠 Home", "🔍 Research", "📋 Results", "ℹ️ About"],
        index=["🏠 Home", "🔍 Research", "📋 Results", "ℹ️ About"].index(st.session_state.nav),
        label_visibility="collapsed",
    )
    st.session_state.nav = nav

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ── History panel ──
    history = get_history()
    st.markdown(f"**Research History** ({len(history)})")

    if not history:
        st.markdown(
            '<div style="font-size:12px;color:rgba(255,255,255,0.45);padding:8px 0">'
            "No research sessions yet.</div>",
            unsafe_allow_html=True,
        )
    else:
        for entry in history[:6]:
            type_cls = "topic" if entry["input_type"] == "topic" else "url"
            type_label = "📄 Topic" if entry["input_type"] == "topic" else "🔗 URL"
            st.markdown(
                f"""<div class="hist-card">
                    <div class="hist-type {type_cls}">{type_label}</div>
                    <div class="hist-subject">{entry['subject']}</div>
                    <div class="hist-time">{entry['timestamp']} · {entry['mode'][:5]}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"View #{entry['id']}", key=f"hist_{entry['id']}", use_container_width=True):
                st.session_state.current_report = entry["report"]
                st.session_state.nav = "📋 Results"
                st.rerun()

        if st.button("🗑 Clear History", use_container_width=True):
            clear_history()
            st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:11px;color:rgba(255,255,255,0.35);text-align:center">'
        "v1.0.0 · Final Year Project</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════
if st.session_state.nav == "🏠 Home":

    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Final Year Project · AI &amp; NLP</div>
        <div class="hero-title">Open Deep Research <span>Agent</span></div>
        <div class="hero-sub">
            An autonomous multi-agent system that researches any topic or paper URL,
            synthesises information from academic sources, and delivers structured
            reports in seconds — no manual searching required.
        </div>
        <div class="hero-badges">
            <span class="badge">🤖 Multi-Agent Architecture</span>
            <span class="badge">📚 Academic Sources</span>
            <span class="badge">⚡ Instant Reports</span>
            <span class="badge">📥 Downloadable Output</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature grid
    st.markdown('<div class="section-label">What It Does</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Three Agents, One Pipeline</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🧭</div>
            <div class="feature-name">Planner Agent</div>
            <div class="feature-desc">Detects whether your input is a research topic or a paper URL, then builds a step-by-step research workflow tailored to that input.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔎</div>
            <div class="feature-name">Searcher Agent</div>
            <div class="feature-desc">Queries academic databases, arXiv, IEEE Xplore, and open web sources. Returns structured data with ranked relevance and citation metadata.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">✍️</div>
            <div class="feature-name">Writer Agent</div>
            <div class="feature-desc">Synthesises raw findings into either a concise executive summary or a full research report with introduction, analysis, and references.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🗂</div>
            <div class="feature-name">Session History</div>
            <div class="feature-desc">Every session is saved locally. Revisit, compare, or download any past report directly from the sidebar — no account needed.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <div class="feature-name">Downloadable Reports</div>
            <div class="feature-desc">Export your report as a TXT file instantly. PDF export is one library integration away for production deployment.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🛡</div>
            <div class="feature-name">Input Validation</div>
            <div class="feature-desc">Smart validation catches empty inputs, malformed URLs, and edge cases before agents run — giving clear, actionable error messages.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Architecture flow
    st.markdown('<div class="section-label">System Design</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Agent Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="arch-flow">
        <div class="arch-node">
            <div class="arch-node-icon">👤</div>
            <div class="arch-node-label">User Input</div>
        </div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">
            <div class="arch-node-icon">🧭</div>
            <div class="arch-node-label">Planner</div>
        </div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">
            <div class="arch-node-icon">🔎</div>
            <div class="arch-node-label">Searcher</div>
        </div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">
            <div class="arch-node-icon">✍️</div>
            <div class="arch-node-label">Writer</div>
        </div>
        <div class="arch-arrow">→</div>
        <div class="arch-node">
            <div class="arch-node-icon">📄</div>
            <div class="arch-node-label">Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-strip">
        <span>💡</span>
        <span>Ready to try it? Head to <strong>Research</strong> in the sidebar, enter a topic or paste a paper URL, and hit <em>Start Research</em>.</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀  Go to Research →"):
        st.session_state.nav = "🔍 Research"
        st.rerun()


# ═══════════════════════════════════════════════
# PAGE: RESEARCH INPUT
# ═══════════════════════════════════════════════
elif st.session_state.nav == "🔍 Research":

    st.markdown("""
    <div style="padding-top:24px">
        <div class="section-label">Research Input</div>
        <div class="section-title">Start a New Research Session</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 Enter Your Research Query")
    st.markdown(
        '<div style="font-size:13px;color:#64748B;margin-bottom:16px">'
        "Fill in either a research topic <em>or</em> a paper URL — not both. "
        "If both are filled, the URL takes priority.</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        topic_input = st.text_area(
            "🔬 Research Topic",
            placeholder="e.g. Large Language Models for Medical Diagnosis",
            height=100,
            help="Describe the topic you want researched in 5–20 words for best results.",
        )

    with col2:
        url_input = st.text_input(
            "🔗 Research Paper URL",
            placeholder="https://arxiv.org/abs/2301.00303",
            help="Paste the full URL to any accessible research paper.",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Mode selection
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 Output Mode")
    mode = st.radio(
        "Select report type",
        ["Short Summary", "Detailed Research Report"],
        horizontal=True,
        label_visibility="collapsed",
        help="Short Summary is faster; Detailed Report includes methodology, analysis, and references.",
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(
            """<div style="background:#EFF6FF;border-radius:8px;padding:12px 14px;font-size:13px;color:#1e40af">
            <strong>Short Summary</strong><br>~200 words · Executive overview · Key findings · Conclusion
            </div>""", unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            """<div style="background:#F0FDF4;border-radius:8px;padding:12px 14px;font-size:13px;color:#15803D">
            <strong>Detailed Research Report</strong><br>~600+ words · Introduction · Methodology · Analysis · References
            </div>""", unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Submit button ──
    run_clicked = st.button("🚀  Start Research")

    if run_clicked:
        # Validation
        has_topic = bool(topic_input.strip())
        has_url = bool(url_input.strip())

        if not has_topic and not has_url:
            st.markdown(
                '<div class="error-strip">⚠️ <strong>Empty input.</strong> Please enter a research topic or paste a paper URL before starting.</div>',
                unsafe_allow_html=True,
            )
            st.stop()

        if has_url and not is_valid_url(url_input):
            st.markdown(
                '<div class="error-strip">⚠️ <strong>Invalid URL.</strong> The URL you entered doesn\'t look valid. '
                "Make sure it starts with https:// and points to an accessible page.</div>",
                unsafe_allow_html=True,
            )
            st.stop()

        # ── PIPELINE ──
        st.markdown("---")
        st.markdown("#### ⚙️ Agent Pipeline Running")

        steps = [
            ("🧭", "Planner Agent", "Analysing input and building workflow…"),
            ("🔎", "Searcher Agent", "Querying academic databases and sources…"),
            ("✍️", "Writer Agent", "Synthesising findings into report…"),
        ]

        progress_bar = st.progress(0)
        status_box = st.empty()

        results = {}

        for i, (icon, name, msg) in enumerate(steps):
            # Render step indicators
            step_html = ""
            for j, (s_icon, s_name, _) in enumerate(steps):
                if j < i:
                    dot_cls, text_cls = "done", "done"
                    label = f"✓ {s_name} — Done"
                elif j == i:
                    dot_cls, text_cls = "", "active"
                    label = f"{s_icon} {s_name} — Running…"
                else:
                    dot_cls, text_cls = "waiting", ""
                    label = f"{s_name}"
                step_html += f'<div class="step-row"><div class="step-dot {dot_cls}"></div><div class="step-text {text_cls}">{label}</div></div>'

            status_box.markdown(
                f'<div class="result-card">{step_html}</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress((i / len(steps)))

            # Run the actual agent
            try:
                if i == 0:
                    input_data = {
                        "topic": topic_input.strip(),
                        "url": url_input.strip(),
                        "mode": mode,
                    }
                    results["plan"] = planner_agent(input_data)
                elif i == 1:
                    results["research"] = searcher_agent(results["plan"])
                elif i == 2:
                    results["report"] = writer_agent(results["research"], mode)
            except Exception as e:
                st.markdown(
                    f'<div class="error-strip">❌ <strong>{name} failed.</strong> {str(e)}</div>',
                    unsafe_allow_html=True,
                )
                st.stop()

        progress_bar.progress(100)

        # Final status
        status_box.markdown(
            '<div class="success-strip">✅ <strong>All agents completed.</strong> Your research report is ready below.</div>',
            unsafe_allow_html=True,
        )

        # Attach metadata for display
        plan = results["plan"]
        report = results["report"]
        report["mode"] = mode
        report["input_type"] = plan["input_type"]
        report["subject"] = plan["subject"]
        report["sources"] = results["research"].get("sources", [])

        # Save to session state + history
        st.session_state.current_report = report
        add_to_history(
            subject=plan["subject"],
            input_type=plan["input_type"],
            mode=mode,
            report=report,
        )

        time.sleep(0.8)
        st.session_state.nav = "📋 Results"
        st.rerun()


# ═══════════════════════════════════════════════
# PAGE: RESULTS
# ═══════════════════════════════════════════════
elif st.session_state.nav == "📋 Results":

    report = st.session_state.current_report

    if report is None:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px">
            <div style="font-size:48px;margin-bottom:16px">📭</div>
            <div style="font-size:20px;font-weight:700;color:#0B1F4A;margin-bottom:8px">No report yet</div>
            <div style="font-size:14px;color:#64748B">Run a research session first to see results here.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Research"):
            st.session_state.nav = "🔍 Research"
            st.rerun()
        st.stop()

    mode = report.get("mode", "Short Summary")
    title = report.get("title", "Research Report")
    sources = report.get("sources", [])
    full_text = report.get("full_text", "")
    word_count = report.get("word_count", 0)
    generated_at = report.get("generated_at", "")
    subject = report.get("subject", "")
    input_type = report.get("input_type", "topic")

    # ── Report header ──
    type_badge = "📄 Topic Research" if input_type == "topic" else "🔗 Paper Analysis"
    st.markdown(f"""
    <div style="padding-top:20px">
        <div class="section-label">{type_badge}</div>
        <div class="section-title" style="margin-bottom:6px">{title}</div>
        <div style="font-size:13px;color:#64748B;margin-bottom:20px">
            Generated {generated_at} · {word_count_badge(word_count)} · Mode: <strong>{mode}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──
    num_findings = len(report.get("key_findings", []))
    num_sources = len(sources)
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-val">{num_findings}</div>
            <div class="stat-lbl">Key Findings</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{num_sources}</div>
            <div class="stat-lbl">Sources</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{word_count}</div>
            <div class="stat-lbl">Words</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">3</div>
            <div class="stat-lbl">Agents Used</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────── SHORT SUMMARY ───────────────
    if mode == "Short Summary":

        # Executive summary
        st.markdown(f"""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">📋</span> Executive Summary</div>
            <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('executive_summary','')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Key findings
        findings = report.get("key_findings", [])
        findings_html = "".join(
            f'<div class="finding-item"><span class="finding-num">{i+1}.</span><span>{f}</span></div>'
            for i, f in enumerate(findings)
        )
        st.markdown(f"""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">🔑</span> Key Findings</div>
            {findings_html}
        </div>
        """, unsafe_allow_html=True)

        # Conclusion
        st.markdown(f"""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">🎯</span> Conclusion</div>
            <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('conclusion','')}</p>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────── DETAILED REPORT ───────────────
    else:
        tabs = st.tabs(["📖 Introduction", "🔬 Methodology", "🔑 Findings", "📊 Analysis", "🎯 Conclusion", "📚 References"])

        with tabs[0]:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title"><span class="icon">📖</span> Introduction</div>
                <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('introduction','')}</p>
            </div>
            """, unsafe_allow_html=True)

        with tabs[1]:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title"><span class="icon">🔬</span> Methodology</div>
                <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('methodology','')}</p>
            </div>
            """, unsafe_allow_html=True)

        with tabs[2]:
            findings = report.get("key_findings", [])
            findings_html = "".join(
                f'<div class="finding-item"><span class="finding-num">{i+1}.</span><span>{f}</span></div>'
                for i, f in enumerate(findings)
            )
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title"><span class="icon">🔑</span> Research Findings</div>
                {findings_html}
            </div>
            """, unsafe_allow_html=True)

        with tabs[3]:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title"><span class="icon">📊</span> Analysis</div>
                <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('analysis','')}</p>
            </div>
            """, unsafe_allow_html=True)

        with tabs[4]:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title"><span class="icon">🎯</span> Conclusion</div>
                <p style="font-size:14px;color:#334155;line-height:1.7;margin:0">{report.get('conclusion','')}</p>
            </div>
            """, unsafe_allow_html=True)

        with tabs[5]:
            refs = report.get("references", [])
            if refs:
                refs_html = "".join(
                    f"""<div class="source-item">
                        <div class="source-dot"></div>
                        <div>
                            <span class="source-title">{r['title']}</span>
                            <span class="source-meta">({r['year']}) · {r['venue']}</span><br>
                            <a href="{r['url']}" target="_blank" style="font-size:11px;color:#3B82F6">{r['url']}</a>
                        </div>
                    </div>"""
                    for r in refs
                )
                st.markdown(f'<div>{refs_html}</div>', unsafe_allow_html=True)
            else:
                st.info("No references collected.")

    # ── Sources expander ──
    st.markdown("---")
    with st.expander(f"🌐  All Sources ({len(sources)} collected)", expanded=False):
        if sources:
            for i, s in enumerate(sources):
                st.markdown(
                    f"""<div class="source-item">
                        <div class="source-dot"></div>
                        <div style="flex:1">
                            <span class="source-title">[{i+1}] {s['title']}</span>
                            <span class="source-meta"> · {s['year']} · {s['venue']}</span><br>
                            <a href="{s['url']}" target="_blank" style="font-size:11px;color:#3B82F6">{s['url']}</a>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.write("No sources available.")

    # ── Downloads ──
    st.markdown("---")
    st.markdown("#### 📥 Download Report")
    dl1, dl2 = st.columns(2)

    safe_name = sanitize_filename(subject or "research_report")

    with dl1:
        st.download_button(
            label="⬇️  Download as TXT",
            data=full_text,
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl2:
        # PDF placeholder — provide as bytes download of text until pdf lib is added
        pdf_bytes = generate_pdf_placeholder(full_text)
        st.download_button(
            label="⬇️  Download as PDF (placeholder)",
            data=pdf_bytes,
            file_name=f"{safe_name}.pdf",
            mime="application/octet-stream",
            use_container_width=True,
            help="Production build: integrate reportlab or fpdf2 for true PDF output.",
        )

    # ── New research CTA ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍  Start New Research"):
        st.session_state.nav = "🔍 Research"
        st.rerun()


# ═══════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════
elif st.session_state.nav == "ℹ️ About":

    st.markdown("""
    <div style="padding-top:24px">
        <div class="section-label">About This Project</div>
        <div class="section-title">Open Deep Research Agent</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown("""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">🎯</span> Project Objective</div>
            <p style="font-size:14px;color:#334155;line-height:1.75">
            Open Deep Research Agent is a final-year B.Tech/M.Tech capstone project demonstrating
            how a <strong>multi-agent AI architecture</strong> can automate the most time-consuming
            parts of academic research: source discovery, information extraction, and report writing.
            </p>
            <p style="font-size:14px;color:#334155;line-height:1.75">
            The system accepts a plain-English research topic <em>or</em> a URL to any accessible
            research paper, routes the input through three specialised agents — Planner, Searcher,
            and Writer — and returns a structured, downloadable report in under 30 seconds.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">🛠</span> Technology Stack</div>
            <div class="finding-item"><span class="finding-num">UI</span><span>Streamlit · CSS3 · HTML5</span></div>
            <div class="finding-item"><span class="finding-num">AI</span><span>Multi-Agent Architecture · NLP Pipeline</span></div>
            <div class="finding-item"><span class="finding-num">Data</span><span>arXiv · IEEE Xplore · Google Scholar · Open Web</span></div>
            <div class="finding-item"><span class="finding-num">State</span><span>Streamlit Session State (client-side)</span></div>
            <div class="finding-item"><span class="finding-num">Export</span><span>TXT · PDF (reportlab-ready)</span></div>
            <div class="finding-item"><span class="finding-num">Lang</span><span>Python 3.11+</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">📐</span> System Modules</div>
            <div style="font-size:13px;color:#334155;line-height:2">
            📁 <code>app.py</code><br>
            📁 <code>agents/</code><br>
            &nbsp;&nbsp;├── <code>planner_agent.py</code><br>
            &nbsp;&nbsp;├── <code>searcher_agent.py</code><br>
            &nbsp;&nbsp;└── <code>writer_agent.py</code><br>
            📁 <code>database/</code><br>
            &nbsp;&nbsp;└── <code>history_manager.py</code><br>
            📁 <code>utils/</code><br>
            &nbsp;&nbsp;└── <code>helpers.py</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="result-card">
            <div class="result-card-title"><span class="icon">🔮</span> Roadmap</div>
            <div style="font-size:13px;color:#334155;line-height:1.8">
            ✅ Multi-agent pipeline<br>
            ✅ Topic &amp; URL modes<br>
            ✅ Session history<br>
            ✅ TXT export<br>
            🔲 Live LLM integration<br>
            🔲 Real web scraping<br>
            🔲 True PDF export<br>
            🔲 Citation formatting (APA/IEEE)<br>
            🔲 User accounts &amp; cloud sync
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Team section
    st.markdown("---")
    st.markdown('<div class="section-label">Team</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Project Contributors</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="team-grid">
        <div class="team-pill">👨‍💻 P.Sai Vishnu Vardhan Reddy · Frontend Developer</div>
        <div class="team-pill">👨‍💻 Team Member 1 · Lead Developer</div>
        <div class="team-pill">👩‍💻 Team Member 2 · AI / NLP</div>
        <div class="team-pill">👨‍💻 Team Member 3 · Backend / Data</div>
        <div class="team-pill">👩‍💻 Team Member 4 · UI / UX Design</div>
    </div>
    <div style="font-size:12px;color:#64748B;text-align:center;margin-top:4px">
        Department of Computer Science &amp; Engineering
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER (all pages)
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-title">🔬 Open Deep Research Agent</div>
    <div class="footer-sub">AI-Powered Research Automation System </div>
    <div class="footer-links">
        <a class="footer-link" href="https://github.com/vishnu20062002/open-deep-research-agent" target="_blank">📦 GitHub Repository</a>
    </div>
    <div style="font-size:11px;color:#94A3B8;margin-top:12px">
        Built with Streamlit · Python 3.11 · All rights reserved © 2025
    </div>
</div>
""", unsafe_allow_html=True)

import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient
from agents import (
    AgentExecutionError,
    grant_researcher_agent,
    requirements_analyzer_agent,
    proposal_writer_agent,
    judge_agent,
    fallback_grant_brief,
    fallback_requirements_analysis,
    fallback_proposal,
    fallback_judge_result,
)

load_dotenv()

st.set_page_config(
    page_title="GrantCraft | AI Grant Proposal Writer",
    page_icon="🏆",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --primary: #5B2D8E;
    --primary-container: #7C3AED;
    --primary-fixed: #C4B5FD;
    --secondary: #5C6166;
    --secondary-container: #EDE9FE;
    --tertiary: #D97706;
    --background: #F8F7FC;
    --surface-low: #F0EDF8;
    --surface-high: #E5E0F4;
    --surface-lowest: #FFFFFF;
    --on-surface: #1A1D21;
    --on-surface-variant: #2C3A4A;
    --outline-variant: #C4B5FD;
}

.stApp {
    background: var(--background) !important;
    font-family: 'Manrope', sans-serif !important;
    color: var(--on-surface) !important;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
.main .block-container { max-width: 100% !important; padding: 0 !important; }

/* NAV */
.app-nav {
    position: fixed; top: 0; width: 100%; z-index: 999;
    background: rgba(248,247,252,0.92);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    padding: 1rem 2rem;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid rgba(196,181,253,0.25);
}
.app-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    color: var(--primary); letter-spacing: -0.03em;
}
.app-brand span { color: var(--tertiary); }
.app-nav-links { display: flex; gap: 2rem; align-items: center; font-size: 0.9rem; font-weight: 500; }
.nav-active { color: var(--primary); font-weight: 700; border-bottom: 2px solid var(--primary); padding-bottom: 2px; }
.nav-muted { color: var(--secondary); }

/* HERO */
.app-hero {
    padding: 7rem 2rem 5rem; text-align: center; position: relative; overflow: hidden;
    background:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(91,45,142,0.14) 0%, transparent 70%),
        radial-gradient(ellipse 50% 40% at 20% 30%, rgba(124,58,237,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 80% 20%, rgba(217,119,6,0.10) 0%, transparent 60%),
        linear-gradient(180deg, rgba(196,181,253,0.2) 0%, rgba(248,247,252,1) 55%);
    border-bottom: 1px solid rgba(124,58,237,0.1);
}
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 800; color: var(--on-surface);
    letter-spacing: -0.03em; line-height: 1.05; margin-bottom: 1.2rem;
}
.hero-subtitle {
    font-size: 1.15rem; color: var(--on-surface-variant);
    max-width: 42rem; margin: 0 auto 1.5rem; line-height: 1.7;
}
.hero-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(91,45,142,0.08);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 999px; padding: 0.65rem 1.2rem;
    font-size: 0.88rem; color: var(--primary); font-weight: 600;
}

/* INPUT SECTION */
.input-section { max-width: 1100px; margin: 0 auto; padding: 3rem 2rem; }
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    text-align: center; color: var(--on-surface); margin-bottom: 0.5rem;
}
.section-sub { text-align: center; color: var(--on-surface-variant); font-size: 0.95rem; margin-bottom: 2.5rem; line-height: 1.6; }
.input-card {
    background: #1a1530; border-radius: 20px; border: 1px solid rgba(124,58,237,0.2);
    padding: 1.6rem; box-shadow: 0 20px 40px rgba(91,45,142,0.07); margin-bottom: 1.2rem;
}
.input-card-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem; font-weight: 700; color: #ffffff;
    margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;
}
.input-note { font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 0.6rem; }

/* Streamlit inputs */
.stTextArea textarea {
    background: #2a2040 !important; border: 1px solid rgba(124,58,237,0.35) !important;
    border-radius: 14px !important; padding: 1rem !important;
    font-family: 'Manrope', sans-serif !important; font-size: 0.95rem !important;
    color: #ffffff !important; resize: vertical !important; box-shadow: none !important;
}
.stTextArea textarea:focus { box-shadow: 0 0 0 2px rgba(124,58,237,0.3) !important; outline: none !important; }
.stTextArea label { display: none !important; }
.stSelectbox > div { background: #2a2040 !important; border: 1px solid rgba(124,58,237,0.35) !important; border-radius: 14px !important; }
.stSelectbox label { display: none !important; }

/* CTA Button */
.stButton > button {
    width: 100% !important; min-height: 3.5rem !important;
    border-radius: 999px !important; border: none !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-container) 100%) !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important; font-weight: 700 !important;
    box-shadow: 0 16px 32px rgba(91,45,142,0.25) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 20px 40px rgba(91,45,142,0.32) !important; }

/* PROGRESS */
.progress-shell {
    max-width: 800px; margin: 0 auto 3rem;
    background: var(--surface-low); border-radius: 24px; padding: 2rem;
}
.progress-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1rem; }
.progress-label-text { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; color: var(--primary); margin-bottom: 0.3rem; }
.progress-title-text { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--on-surface); }
.progress-pct { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2rem; font-weight: 800; color: var(--on-surface); }
.progress-track { width: 100%; height: 10px; background: rgba(91,45,142,0.08); border-radius: 999px; overflow: hidden; margin-bottom: 1.2rem; }
.progress-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--primary), var(--primary-container)); transition: width 0.4s ease; }
.progress-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.progress-item { font-size: 0.88rem; color: var(--on-surface-variant); display: flex; align-items: center; gap: 0.4rem; }
.progress-item.done { color: var(--primary); font-weight: 600; }
.log-box { background: rgba(255,255,255,0.7); border-radius: 14px; padding: 1rem 1.2rem; margin-top: 1rem; font-size: 0.88rem; color: var(--on-surface-variant); line-height: 1.8; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent !important; border-bottom: none !important; flex-wrap: wrap; margin-bottom: 1rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 999px !important; height: 2.8rem !important; padding: 0 1.2rem !important;
    background: #2a2040 !important; border: 1px solid rgba(124,58,237,0.35) !important;
    color: var(--on-surface) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.88rem !important; font-weight: 700 !important;
}
.stTabs [aria-selected="true"] { background: var(--surface-lowest) !important; color: var(--primary) !important; box-shadow: 0 8px 20px rgba(91,45,142,0.1) !important; }
.stTabs [data-baseweb="tab-panel"] { background: var(--surface-lowest) !important; border-radius: 20px !important; padding: 1.5rem !important; box-shadow: 0 20px 40px rgba(91,45,142,0.05) !important; }

/* SCORE CARD */
.score-card { background: #1a1530; border-radius: 20px; border: 1px solid rgba(124,58,237,0.2); padding: 2rem; box-shadow: 0 24px 48px rgba(91,45,142,0.08); position: sticky; top: 5rem; }
.score-kicker { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; color: var(--on-surface-variant); text-align: center; margin-bottom: 1rem; }
.score-ring-wrapper { display: flex; justify-content: center; align-items: center; position: relative; margin-bottom: 0.75rem; height: 132px; }
.score-ring-number { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: 'Plus Jakarta Sans', sans-serif; font-size: 28px; font-weight: 800; color: #1a1d21; line-height: 1; }
.score-match-label { text-align: center; font-weight: 700; color: var(--tertiary); font-size: 0.95rem; margin-bottom: 1.5rem; }
.metric-row { margin-bottom: 1rem; }
.metric-top { display: flex; justify-content: space-between; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: var(--on-surface); margin-bottom: 0.35rem; }
.mini-bar { width: 100%; height: 8px; border-radius: 999px; background: var(--surface-high); overflow: hidden; }
.mini-bar-fill { height: 100%; border-radius: 999px; background: var(--primary-container); }
.score-note { font-size: 0.88rem; color: var(--on-surface-variant); line-height: 1.6; margin-top: 0.5rem; }
.score-divider { border: none; border-top: 1px solid rgba(196,181,253,0.25); margin: 1.25rem 0; }

/* Profile card */
.profile-card {
    background: linear-gradient(135deg, rgba(91,45,142,0.07), rgba(124,58,237,0.04));
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 16px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
    font-size: 0.9rem; line-height: 1.8; color: var(--on-surface-variant);
}
.profile-card strong { color: var(--primary); }

/* Footer */
.app-footer { background: var(--surface-high); padding: 3rem 2rem; text-align: center; margin-top: 4rem; }
.footer-copy { color: var(--secondary); font-size: 0.82rem; line-height: 1.6; max-width: 40rem; margin: 0 auto 1rem; opacity: 0.8; }
.footer-links { display: flex; justify-content: center; gap: 2rem; font-size: 0.82rem; color: var(--secondary); }
.footer-links a { color: var(--primary); text-decoration: underline; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<nav class="app-nav">
    <div class="app-brand">Grant<span>Craft</span> 🏆</div>
    <div class="app-nav-links">
        <span class="nav-active">Write Proposal</span>
        <span class="nav-muted">How It Works</span>
        <span class="nav-muted">Help</span>
    </div>
</nav>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<section class="app-hero">
    <div style="position:relative;z-index:1;">
        <div style="
            display:inline-flex;align-items:center;gap:0.5rem;
            background:rgba(91,45,142,0.08);
            border:1px solid rgba(124,58,237,0.25);
            border-radius:999px;padding:0.4rem 1rem;
            font-size:0.8rem;font-weight:700;color:#5B2D8E;
            letter-spacing:0.08em;text-transform:uppercase;
            margin-bottom:1.2rem;">
            🤖 AI-Powered · Real Grants · Professional Proposals
        </div>
        <h1 class="hero-title">🏆 AI Grant Proposal<br>Writer</h1>
        <p class="hero-subtitle">
            Tell us about your project. Our AI finds active grants you can apply for,
            analyzes their requirements, and writes a complete, compelling proposal — ready to submit.
        </p>
        <div class="hero-pill">
            ✅ Searches real grants · Writes all 8 proposal sections · Evaluates quality
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ── INPUT SECTION ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="input-section">
    <h2 class="section-title">Your Project Details</h2>
    <p class="section-sub">
        The more specific you are, the better your proposal will be.
        Fill in all fields for the strongest output.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="input-card"><div class="input-card-label">📋 Project Info</div></div>', unsafe_allow_html=True)
    title = st.text_area("title", placeholder="Project Title: e.g. AI-Powered Rural Healthcare Diagnosis System", height=80, label_visibility="collapsed", key="title_input")
    description = st.text_area("description", placeholder="Project Description: Describe your project idea in 3-5 sentences. What problem does it solve? Who does it help? What is your approach?", height=160, label_visibility="collapsed", key="desc_input")
    st.markdown('<div class="input-note">💡 Be specific — vague descriptions produce generic proposals.</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-card"><div class="input-card-label">🎯 Grant Details</div></div>', unsafe_allow_html=True)
    category = st.selectbox("category", ["Select Grant Category", "Research", "Social Impact", "Innovation", "Education", "Health", "Environment", "Technology"], label_visibility="collapsed", key="category_input")
    region = st.selectbox("region", ["Select Target Region", "India", "Global", "USA", "European Union", "UK", "Other"], label_visibility="collapsed", key="region_input")
    budget = st.selectbox("budget", ["Select Budget Range", "Under ₹10 Lakh", "₹10 Lakh – ₹50 Lakh", "₹50 Lakh – ₹1 Crore", "Above ₹1 Crore", "Under $50,000", "$50,000 – $200,000", "Above $200,000", "Not Sure"], label_visibility="collapsed", key="budget_input")
    st.markdown('<div class="input-note">💡 Budget range helps us match grants you are realistically eligible for.</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="input-card"><div class="input-card-label">🏢 Organization Details</div></div>', unsafe_allow_html=True)
    org_type = st.selectbox("org_type", ["Select Organization Type", "NGO / Non-profit", "Startup", "University / Research Institution", "Individual / Independent Researcher", "Government Body", "Social Enterprise", "Hospital / Healthcare Org"], label_visibility="collapsed", key="org_input")
    team = st.text_area("team", placeholder="Team Background (optional): Briefly describe your team's relevant experience, qualifications, or past projects.", height=120, label_visibility="collapsed", key="team_input")
    st.markdown('<div class="input-note">💡 Team credentials significantly improve proposal scores.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate_btn = st.button("🚀 Generate My Grant Proposal", type="primary")

# ── PIPELINE ──────────────────────────────────────────────────────────────────
if generate_btn:
    if not title or not description:
        st.warning("Please fill in at least the Project Title and Description before generating.")
        st.stop()

    if category == "Select Grant Category":
        st.warning("Please select a Grant Category.")
        st.stop()

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    if not tavily_key:
        st.error("TAVILY_API_KEY is missing in your .env file.")
        st.stop()

    category_val = category
    region_val   = region   if region   != "Select Target Region"   else "Global"
    budget_val   = budget   if budget   != "Select Budget Range"    else "Not specified"
    org_val      = org_type if org_type != "Select Organization Type" else "Not specified"

    project_profile = f"""Project Title: {title}
Description: {description}
Grant Category: {category_val}
Target Region: {region_val}
Budget Range: {budget_val}
Organization Type: {org_val}
Team Background: {team or "Not specified"}"""

    client = genai.Client(api_key=gemini_key, vertexai=False) if gemini_key else None
    tavily_client = TavilyClient(api_key=tavily_key)

    # Profile summary
    st.markdown(
        f'<div style="max-width:1100px;margin:1.5rem auto 0;padding:0 2rem">'
        f'<div class="profile-card">'
        f'<strong>Your Project:</strong> {title} · '
        f'{category_val} Grant · {region_val} · {budget_val} · {org_val}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    logs = []
    progress_value = 10
    progress_placeholder = st.empty()

    def render_progress():
        steps = [
            ("🔍 Searching for active grants",        progress_value >= 35),
            ("📋 Analyzing grant requirements",       progress_value >= 60),
            ("✍️ Writing your proposal",              progress_value >= 82),
            ("⭐ Evaluating proposal quality",        progress_value >= 100),
        ]
        items_html = "".join(
            f'<div class="progress-item {"done" if done else ""}">'
            f'{"✓" if done else "○"} {label}</div>'
            for label, done in steps
        )
        log_html = (
            f'<div class="log-box">{"<br>".join(logs[-6:])}</div>'
            if logs else ""
        )
        progress_placeholder.markdown(f"""
        <div class="progress-shell">
            <div class="progress-header">
                <div>
                    <div class="progress-label-text">AI Agent Pipeline</div>
                    <div class="progress-title-text">Writing your proposal...</div>
                </div>
                <div class="progress-pct">{progress_value}%</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{progress_value}%"></div>
            </div>
            <div class="progress-grid">{items_html}</div>
            {log_html}
        </div>
        """, unsafe_allow_html=True)

    def log_step(msg):
        logs.append(f"✓ {msg}")
        render_progress()

    render_progress()

    # Agent 1 — Grant Researcher
    with st.spinner(""):
        if client is None:
            log_step("Researcher: Gemini unavailable — using Tavily fallback")
            grant_brief = fallback_grant_brief(tavily_client, project_profile)
        else:
            try:
                grant_brief = grant_researcher_agent(client, tavily_client, project_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Researcher: fallback mode")
                grant_brief = fallback_grant_brief(tavily_client, project_profile)
    progress_value = 35
    render_progress()

    # Agent 2 — Requirements Analyzer
    with st.spinner(""):
        if client is None:
            log_step("Requirements Analyzer: using built-in checklist")
            requirements = fallback_requirements_analysis(grant_brief, project_profile)
        else:
            try:
                requirements = requirements_analyzer_agent(client, grant_brief, project_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Requirements Analyzer: fallback mode")
                requirements = fallback_requirements_analysis(grant_brief, project_profile)
    progress_value = 60
    render_progress()

    # Agent 3 — Proposal Writer
    with st.spinner(""):
        if client is None:
            log_step("Proposal Writer: using template")
            proposal = fallback_proposal(grant_brief, requirements, project_profile)
        else:
            try:
                proposal = proposal_writer_agent(client, grant_brief, requirements, project_profile, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Proposal Writer: fallback mode")
                proposal = fallback_proposal(grant_brief, requirements, project_profile)
    progress_value = 82
    render_progress()

    # Agent 4 — Judge
    with st.spinner(""):
        if client is None:
            log_step("Judge: using estimated rubric")
            judge_result = fallback_judge_result()
        else:
            try:
                judge_result = judge_agent(client, project_profile, grant_brief, proposal, log_step=log_step)
            except AgentExecutionError as e:
                log_step("Judge: fallback mode")
                judge_result = fallback_judge_result()
    progress_value = 100
    render_progress()
    progress_placeholder.empty()

    # ── OUTPUT ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="max-width:1200px;margin:2rem auto;padding:0 2rem">
        <div style="display:flex;align-items:center;gap:0.85rem;margin-bottom:1.5rem">
            <div style="width:44px;height:44px;border-radius:14px;background:rgba(124,58,237,0.15);display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🏆</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.9rem;font-weight:800;color:#1a1d21;">Your Grant Proposal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    output_col, score_col = st.columns([1.9, 0.95], gap="large")

    with output_col:
        tabs = st.tabs(["🔍 Found Grants", "📋 Requirements", "📄 Full Proposal", "⭐ Quality Score"])

        with tabs[0]:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#5B2D8E,#7C3AED);color:white;
                        border-radius:18px;padding:1.3rem;margin-bottom:1rem">
                <h3 style="color:white;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.2rem;margin-bottom:0.25rem">
                    Active Grants Found For Your Project
                </h3>
                <p style="color:rgba(255,255,255,0.8);font-size:0.88rem">
                    Real grants from official funding bodies — searched in real time
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(grant_brief)

        with tabs[1]:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#D97706,#F59E0B);color:white;
                        border-radius:18px;padding:1.3rem;margin-bottom:1rem">
                <h3 style="color:white;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.2rem;margin-bottom:0.25rem">
                    What Your Proposal Needs to Win
                </h3>
                <p style="color:rgba(255,255,255,0.8);font-size:0.88rem">
                    Grant criteria analysis — tailored to your project and target funders
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(requirements)

        with tabs[2]:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#059669,#10B981);color:white;
                        border-radius:18px;padding:1.3rem;margin-bottom:1rem">
                <h3 style="color:white;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.2rem;margin-bottom:0.25rem">
                    Your Complete Grant Proposal
                </h3>
                <p style="color:rgba(255,255,255,0.8);font-size:0.88rem">
                    All 8 sections — ready to copy, edit, and submit
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(proposal)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Proposal as .txt",
                data=proposal,
                file_name=f"grant_proposal_{title[:30].replace(' ', '_')}.txt",
                mime="text/plain",
            )

        with tabs[3]:
            st.markdown(judge_result.get("summary", ""))
            st.markdown("---")
            labels = {
                "grant_alignment":  "Grant Alignment",
                "problem_clarity":  "Problem Clarity",
                "methodology":      "Methodology",
                "impact_outcomes":  "Impact & Outcomes",
                "budget_rationale": "Budget Rationale",
            }
            for key, label in labels.items():
                data  = judge_result.get("scores", {}).get(key, {})
                score = float(data.get("score", 0))
                st.markdown(f"**{label}** — {score}/5")
                st.progress(min(max(score / 5, 0.0), 1.0))
                st.caption(data.get("reasoning", ""))

    with score_col:
        overall = float(judge_result.get("overall_score", 0))
        pct     = min(int(round((overall / 5) * 100)), 100)
        match_label = (
            "Highly Competitive" if pct >= 85 else
            "Strong Proposal"    if pct >= 70 else
            "Needs Refinement"
        )
        scores          = judge_result.get("scores", {})
        alignment_pct   = int((float(scores.get("grant_alignment",  {}).get("score", 0)) / 5) * 100)
        methodology_pct = int((float(scores.get("methodology",      {}).get("score", 0)) / 5) * 100)
        impact_pct      = int((float(scores.get("impact_outcomes",  {}).get("score", 0)) / 5) * 100)
        offset_val      = round(351.8 - (pct / 100) * 351.8, 1)
        top_strength    = judge_result.get("top_strength", "")
        top_improvement = judge_result.get("top_improvement", "")

        st.markdown(f"""
<div class="score-card">
    <div class="score-kicker">Proposal Quality Score</div>
    <div class="score-ring-wrapper">
        <svg width="132" height="132" viewBox="0 0 132 132"
             xmlns="http://www.w3.org/2000/svg" style="transform:rotate(-90deg)">
            <circle cx="66" cy="66" r="56" stroke="#E5E0F4" stroke-width="8" fill="transparent"/>
            <circle cx="66" cy="66" r="56" stroke="#5B2D8E" stroke-width="8" fill="transparent"
                    stroke-dasharray="351.8" stroke-dashoffset="{offset_val}" stroke-linecap="round"/>
        </svg>
        <div class="score-ring-number">{pct}</div>
    </div>
    <div class="score-match-label">{match_label}</div>
    <div class="metric-row">
        <div class="metric-top"><span>Grant Alignment</span><span>{alignment_pct}%</span></div>
        <div class="mini-bar"><div class="mini-bar-fill" style="width:{alignment_pct}%"></div></div>
    </div>
    <div class="metric-row">
        <div class="metric-top"><span>Methodology</span><span>{methodology_pct}%</span></div>
        <div class="mini-bar"><div class="mini-bar-fill" style="width:{methodology_pct}%"></div></div>
    </div>
    <div class="metric-row">
        <div class="metric-top"><span>Impact & Outcomes</span><span>{impact_pct}%</span></div>
        <div class="mini-bar"><div class="mini-bar-fill" style="width:{impact_pct}%"></div></div>
    </div>
    <hr class="score-divider"/>
    <div class="score-note"><strong>Strength:</strong> {top_strength}</div>
    <div class="score-note" style="margin-top:0.75rem">
        <strong>To Improve:</strong> {top_improvement}
    </div>
    <hr class="score-divider"/>
    <div class="score-note" style="font-size:0.78rem;opacity:0.75">
        ⚠️ Always review and customize the proposal before submission to any funder.
    </div>
</div>
""", unsafe_allow_html=True)

    st.success("🎉 Your grant proposal is ready! Download it from the 'Full Proposal' tab and customize before submitting.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<footer class="app-footer">
    <p class="footer-copy">
        © 2024 GrantCraft. This tool generates AI-assisted proposal drafts for informational purposes.
        Always review, customize, and verify grant details before submitting to any funder.
    </p>
    <div class="footer-links">
        <a href="https://grants.gov" target="_blank">Grants.gov</a>
        <a href="https://serb.gov.in" target="_blank">SERB India</a>
        <a href="https://dst.gov.in" target="_blank">DST India</a>
        <span>Made with 🤖 AI</span>
    </div>
</footer>
""", unsafe_allow_html=True)

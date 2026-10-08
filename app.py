import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data import load_data
from utils import (
    calculate_risk_score, calculate_dependency_score, calculate_knowledge_risk,
    simulate_unavailability, get_candidates, calculate_workforce_resilience
)

st.set_page_config(page_title="WorkShield AI", layout="wide", initial_sidebar_state="expanded")

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Light application shell ── */
html, body, [data-testid="stAppViewContainer"] { background-color: #F8FAFC; }
[data-testid="stApp"] { background-color: #F8FAFC; }

/* Remove white top bar */
[data-testid="stHeader"] { background: transparent; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background-color: #FFFFFF !important;
  border-right: 1px solid #E2E8F0;
    min-width: 260px;
}
[data-testid="stSidebar"] * { color: #475569 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #0F172A !important; }

/* Radio button group → looks like nav pills */
div[role="radiogroup"] { gap: 4px; }
div[role="radiogroup"] > div[data-testid="stMarkdownContainer"] { display: none; }
div[role="radiogroup"] > div[role="radio"] {
    padding: 10px 14px !important;
    border-radius: 8px !important;
    margin-bottom: 2px !important;
    cursor: pointer;
    transition: background 0.15s;
    background: transparent !important;
    border: none !important;
}
div[role="radiogroup"] > div[role="radio"]:hover {
  background: #F1F5F9 !important;
}
div[role="radiogroup"] > div[role="radio"][aria-checked="true"] {
  background: #EEF2FF !important;
    border-left: 3px solid #6366F1 !important;
}
div[role="radiogroup"] > div[role="radio"] > div:first-child { display: none !important; }
div[role="radiogroup"] > div[role="radio"] p {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #64748B !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
div[role="radiogroup"] > div[role="radio"][aria-checked="true"] p {
  color: #4338CA !important;
    font-weight: 600 !important;
}

/* ── Card containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    padding: 2px !important;
    margin-bottom: 6px;
}
[data-testid="stVerticalBlockBorderWrapper"] h1,
[data-testid="stVerticalBlockBorderWrapper"] h2,
[data-testid="stVerticalBlockBorderWrapper"] h3,
[data-testid="stVerticalBlockBorderWrapper"] h4,
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stVerticalBlockBorderWrapper"] span {
    color: #1E293B !important;
}

/* Fix tabs inside containers */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTabs"] button {
    color: #64748B !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTabs"] button[aria-selected="true"] {
    color: #6366F1 !important;
    border-bottom-color: #6366F1 !important;
}

/* Plotly inside cards */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"] { background: transparent; }

/* Streamlit metric cards */
[data-testid="stMetric"] {
    background: #F8FAFC;
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #E2E8F0;
}
[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #111827 !important; font-size: 22px !important; font-weight: 700; }

/* ── BUTTONS ── high specificity to beat the card span color rule */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important;
}
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primary"] span,
[data-testid="stBaseButton-primary"] div { color: #FFFFFF !important; }
[data-testid="stBaseButton-primary"]:hover { opacity: 0.87; }

[data-testid="stBaseButton-secondary"] {
    background: #F1F5F9 !important;
    border: 1px solid #CBD5E1 !important; border-radius: 8px !important; font-weight: 500 !important;
}
[data-testid="stBaseButton-secondary"] p,
[data-testid="stBaseButton-secondary"] span,
[data-testid="stBaseButton-secondary"] div { color: #334155 !important; }
[data-testid="stBaseButton-secondary"]:hover { background: #E2E8F0 !important; }

/* legacy kind attribute fallback */
button[kind="primary"] p, button[kind="primary"] span { color: #FFFFFF !important; }
button[kind="secondary"] p, button[kind="secondary"] span { color: #334155 !important; }

/* Prevent card container's global span rule from hijacking button text */
[data-testid="stVerticalBlockBorderWrapper"] button p,
[data-testid="stVerticalBlockBorderWrapper"] button span,
[data-testid="stVerticalBlockBorderWrapper"] button div { color: inherit !important; }

/* Dataframe */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stDataFrame"] {
    border-radius: 8px; overflow: hidden;
}

/* Progress bars */
[data-testid="stProgressBar"] > div { background-color: #6366F1 !important; }

/* Selectbox label in cards */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] label { color: #64748B !important; }

/* ── TABS — all pages ── */
/* Tab strip */
[data-testid="stTabs"] { border-bottom: 1px solid #E2E8F0; }

/* Inactive tab */
button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 10px 20px !important;
    margin-right: 4px !important;
    transition: all 0.15s !important;
}
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    color: #64748B !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* Active tab */
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #6366F1 !important;
    background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] span {
    color: #6366F1 !important;
    font-weight: 700 !important;
}

/* Hover on inactive */
button[data-baseweb="tab"]:not([aria-selected="true"]):hover {
    border-bottom: 2px solid #CBD5E1 !important;
    background: rgba(99,102,241,0.04) !important;
}
button[data-baseweb="tab"]:not([aria-selected="true"]):hover p,
button[data-baseweb="tab"]:not([aria-selected="true"]):hover span { color: #334155 !important; }

/* Tab content panel */
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 14px; background: transparent !important; }

/* ── KPI cards (inline HTML) ── */
.kpi-row { display: flex; align-items: center; gap: 14px; padding: 6px 4px; }
.kpi-icon { width: 46px; height: 46px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
.kpi-green { background-color: #D1FAE5; }
.kpi-red   { background-color: #FEE2E2; }
.kpi-orange{ background-color: #FEF3C7; }
.kpi-purple{ background-color: #EDE9FE; }
.kpi-blue  { background-color: #DBEAFE; }
.kpi-content { flex: 1; min-width: 0; }
.kpi-title { font-size: 12px; color: #64748B !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 3px; }
.kpi-value { font-size: 26px; font-weight: 800; color: #0F172A !important; line-height: 1.1; }
.kpi-up   { color: #10B981 !important; font-size: 13px; font-weight: 600; }
.kpi-down { color: #EF4444 !important; font-size: 13px; font-weight: 600; }
.kpi-sub  { font-size: 12px; color: #94A3B8 !important; margin-top: 2px; }

/* ── Badges ── */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.03em; }
.badge-critical{ background-color: #FEE2E2; color: #DC2626 !important; }
.badge-high    { background-color: #FFEDD5; color: #EA580C !important; }
.badge-medium  { background-color: #FEF3C7; color: #D97706 !important; }
.badge-low     { background-color: #D1FAE5; color: #059669 !important; }
.badge-info    { background-color: #DBEAFE; color: #2563EB !important; }

/* ── Skill pills ── */
.skill-pill { display: inline-block; padding: 5px 13px; background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 12px; font-weight: 500; color: #334155 !important; margin: 3px 4px 3px 0; }

/* ── List in cards ── */
.card-list { list-style: none; padding: 0; margin: 0; }
.card-list li { display: flex; justify-content: space-between; align-items: center; padding: 9px 0; border-bottom: 1px solid #F1F5F9; font-size: 13px; color: #334155 !important; }
.card-list li:last-child { border-bottom: none; }

/* ── Profile header ── */
.profile-header { display: flex; align-items: center; justify-content: space-between; }
.profile-info   { display: flex; align-items: center; gap: 16px; }
.avatar { width: 54px; height: 54px; border-radius: 50%; background: linear-gradient(135deg,#6366F1,#8B5CF6); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700; flex-shrink:0; }
.profile-name { font-size: 18px; font-weight: 700; color: #0F172A !important; }
.profile-role { font-size: 13px; color: #64748B !important; margin-top: 2px; }

/* ── Dep chain ── */
.dep-chain { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 20px; flex-wrap: wrap; }
.dep-node { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; text-align: center; min-width: 110px; }
.dep-node .icon { font-size: 26px; margin-bottom: 6px; }
.dep-node .label { font-size: 13px; font-weight: 600; color: #1E293B !important; }
.dep-node .sub   { font-size: 11px; color: #94A3B8 !important; }
.dep-arrow { color: #CBD5E1; font-size: 22px; }

/* ── Impact banner ── */
.impact-critical { background: linear-gradient(135deg,#FEF2F2,#FEE2E2); border-left: 6px solid #EF4444; border-radius: 12px; padding: 18px 24px; margin-bottom: 18px; }
.impact-high     { background: linear-gradient(135deg,#FFF7ED,#FFEDD5); border-left: 6px solid #F97316; border-radius: 12px; padding: 18px 24px; margin-bottom: 18px; }
.impact-medium   { background: linear-gradient(135deg,#FFFBEB,#FEF3C7); border-left: 6px solid #F59E0B; border-radius: 12px; padding: 18px 24px; margin-bottom: 18px; }
.impact-title { font-size: 22px; font-weight: 800; margin: 0; }

/* ── Candidate card rank ── */
.rank-medal { font-size: 28px; margin-right: 10px; }
.cand-name  { font-size: 18px; font-weight: 700; color: #0F172A !important; }
.cand-match { font-size: 14px; font-weight: 700; color: #6366F1 !important; }

/* ── AI Copilot message ── */
.ai-msg { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px; }
.ai-step { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 14px; }
.ai-step-num { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; color: white; }
.ai-step-body strong { font-size: 14px; color: #0F172A !important; }
.ai-step-body p { font-size: 13px; color: #64748B !important; margin: 2px 0 0; }

/* ── RAI notice ── */
.rai-notice { margin-top: 40px; padding: 14px 20px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 12px; color: #64748B !important; line-height: 1.6; }

/* ── Page header ── */
.page-hdr { margin-bottom: 24px; }
.page-hdr h1 { font-size: 26px; font-weight: 800; color: #0F172A !important; margin-bottom: 4px; }
.page-hdr p  { font-size: 14px; color: #64748B !important; margin: 0; }
.page-hdr-row { display: flex; justify-content: space-between; align-items: flex-end; }
.status-dot { display: inline-block; width: 8px; height: 8px; background: #10B981; border-radius: 50%; margin-right: 6px; }
.status-text { font-size: 12px; color: #10B981 !important; }

/* ── Empty state ── */
.empty-state { text-align: center; padding: 50px 20px; color: #94A3B8 !important; }
.empty-state .icon { font-size: 40px; margin-bottom: 12px; }
.empty-state p { font-size: 14px; }

/* Divider in light shell */
hr.dark-hr { border: none; border-top: 1px solid #E2E8F0; margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def get_initial_data():
    return load_data()

if 'initialized' not in st.session_state:
    emp_df, proj_df, proc_df = get_initial_data()
    st.session_state.employees_df = emp_df.copy()
    st.session_state.projects_df  = proj_df.copy()
    st.session_state.processes_df = proc_df.copy()
    st.session_state.initialized   = True

employees_df = st.session_state.employees_df
projects_df  = st.session_state.projects_df
processes_df = st.session_state.processes_df

employees_df['risk_score']       = employees_df.apply(calculate_risk_score, axis=1)
employees_df['dependency_score'] = employees_df.apply(calculate_dependency_score, axis=1)
processes_df['knowledge_risk']   = processes_df.apply(calculate_knowledge_risk, axis=1)

# Pin Rahul's demo values
employees_df.loc[employees_df['name'] == 'Rahul Sharma', 'dependency_score'] = 93
employees_df.loc[employees_df['name'] == 'Rahul Sharma', 'risk_score']       = 87

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:6px 0 18px;">
        <div style="width:38px;height:38px;background:linear-gradient(135deg,#6366F1,#8B5CF6);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🛡️</div>
        <div>
            <div style="font-size:16px;font-weight:800;color:#0F172A;">WorkShield AI</div>
            <div style="font-size:11px;color:#64748B;">Protect People, Secure Tomorrow.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("NAVIGATION", [
        "🏠  Dashboard",
        "👥  Employee Dependency",
        "⚡  What-If Simulator",
        "🔄  Replacement",
        "🧠  Knowledge Risk",
        "✨  AI HR Copilot"
    ])

    st.markdown('<hr class="dark-hr">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px;color:#64748B;padding:6px 0;">
        <div style="margin-bottom:4px;">ResiliTech · AI for Karaikal 2026</div>
      <div style="color:#475569;">Hackathon Prototype</div>
    </div>
    """, unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def badge(text, level):
    return f'<span class="badge badge-{level}">{text}</span>'

def risk_level(score):
    if score >= 81: return "critical"
    if score >= 61: return "high"
    if score >= 31: return "medium"
    return "low"

def risk_label(score):
    return {"critical":"Critical","high":"High","medium":"Medium","low":"Low"}[risk_level(score)]

def page_header(title, sub):
    st.markdown(f"""
    <div class="page-hdr">
      <div class="page-hdr-row">
        <div>
          <h1 class="page-hdr">{title}</h1>
          <p>{sub}</p>
        </div>
        <div><span class="status-dot"></span><span class="status-text">System Operational</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def plotly_dark(fig, height=260):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=24, b=10),
        height=height,
        font=dict(color="#334155", size=12),
    )
    fig.update_xaxes(showgrid=False, color="#94A3B8")
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", color="#94A3B8")
    return fig

def rai():
    st.markdown("""<div class="rai-notice">
        <strong>Responsible AI Notice:</strong> WorkShield AI is a decision-support tool using work-related
        operational signals. It does not predict resignation, diagnose mental health, or make automated
        employment decisions. HR and management remain the final decision-makers.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    page_header("Welcome back, HR Manager", "Here's how your workforce looks today.")

    # ── KPI row ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        with st.container(border=True):
            st.markdown("""<div class="kpi-row">
              <div class="kpi-icon kpi-green">🛡️</div>
              <div class="kpi-content">
                <div class="kpi-title">Workforce Resilience</div>
                <div class="kpi-value">78/100 <span class="kpi-up">↑ 6%</span></div>
                <div class="kpi-sub">Overall company resilience score</div>
              </div></div>""", unsafe_allow_html=True)
    with k2:
        with st.container(border=True):
            st.markdown("""<div class="kpi-row">
              <div class="kpi-icon kpi-red">👥</div>
              <div class="kpi-content">
                <div class="kpi-title">Critical Employees</div>
                <div class="kpi-value">8</div>
                <div class="kpi-sub">High risk &amp; high dependency</div>
              </div></div>""", unsafe_allow_html=True)
    with k3:
        with st.container(border=True):
            st.markdown("""<div class="kpi-row">
              <div class="kpi-icon kpi-orange">⚠️</div>
              <div class="kpi-content">
                <div class="kpi-title">Without Backup</div>
                <div class="kpi-value">14</div>
                <div class="kpi-sub">No alternate resource available</div>
              </div></div>""", unsafe_allow_html=True)
    with k4:
        with st.container(border=True):
            st.markdown("""<div class="kpi-row">
              <div class="kpi-icon kpi-purple">🧠</div>
              <div class="kpi-content">
                <div class="kpi-title">Knowledge Gaps</div>
                <div class="kpi-value">6</div>
                <div class="kpi-sub">Unique skills / knowledge at risk</div>
              </div></div>""", unsafe_allow_html=True)

    # ── Table + Heatmap ──────────────────────────────────────────────────────
    tl, tr = st.columns([3, 2])
    with tl:
        with st.container(border=True):
            st.markdown("### High Dependency Employees")
            df_disp = employees_df[['name','department','dependency_score','risk_score','backup_owner']].copy()
            df_disp = df_disp.sort_values('dependency_score', ascending=False).head(5)
            df_disp['Impact'] = ["Critical","High","High","Medium","Low"]
            df_disp['Backup'] = df_disp['backup_owner'].apply(lambda x: "✓" if pd.notna(x) and x else "✗")
            st.dataframe(
                df_disp[['name','department','dependency_score','risk_score','Backup','Impact']],
                column_config={
                    "name": "Employee", "department": "Dept",
                    "dependency_score": st.column_config.ProgressColumn("Dependency", format="%d", min_value=0, max_value=100),
                    "risk_score":       st.column_config.ProgressColumn("Work Risk",  format="%d", min_value=0, max_value=100),
                    "Backup": "Backup", "Impact": "Impact"
                },
                hide_index=True, use_container_width=True
            )

    with tr:
        with st.container(border=True):
            st.markdown("### Critical Skills Heatmap")
            st.caption("Darker = higher concentration of that skill in one dept")
            skills = ['Python','AWS','ML','SQL','React','Docker']
            depts  = ['Engineering','Product','Data Sci','Design']
            np.random.seed(42)
            z = np.random.randint(1, 10, size=(len(skills), len(depts)))
            fig = px.imshow(z, x=depts, y=skills, color_continuous_scale="RdPu", aspect="auto")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=0,r=0,t=10,b=0), height=290,
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Analytics row ─────────────────────────────────────────────────────────
    a1, a2, a3 = st.columns(3)
    with a1:
        with st.container(border=True):
            st.markdown("### Risk Overview")
            risk_df = pd.DataFrame({
                'Level': ['Low','Medium','High','Critical'],
                'Count': [162, 58, 20, 8]
            })
            fig2 = px.pie(risk_df, values='Count', names='Level', hole=0.72,
                          color='Level', color_discrete_map={
                              'Low':'#10B981','Medium':'#F59E0B','High':'#F97316','Critical':'#EF4444'})
            fig2.update_traces(textinfo='none', hovertemplate='%{label}: %{value}<extra></extra>')
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=0,r=0,t=10,b=0), height=240,
                               legend=dict(orientation='h', yanchor='bottom', y=-0.25, font=dict(size=11)))
            fig2.add_annotation(text="248<br><span style='font-size:11px'>Employees</span>",
                                showarrow=False, font=dict(size=18, color='#111827'))
            st.plotly_chart(fig2, use_container_width=True)

    with a2:
        with st.container(border=True):
            st.markdown("### Dependency by Dept")
            dept_df = pd.DataFrame({
                'Dept': ['Engineering','Product','Data Sci','Design','Operations'],
                'Score': [82, 67, 54, 38, 29]
            })
            fig3 = px.bar(dept_df, x='Dept', y='Score', color='Score',
                          color_continuous_scale=['#10B981','#F59E0B','#F97316','#EF4444'],
                          range_color=[0,100])
            fig3.update_traces(hovertemplate='%{x}: %{y}<extra></extra>')
            fig3.update_coloraxes(showscale=False)
            fig3 = plotly_dark(fig3, 240)
            st.plotly_chart(fig3, use_container_width=True)

    with a3:
        with st.container(border=True):
            st.markdown("### Resilience Radar")
            comp_df = pd.DataFrame({
                'Component':['Backup','Skills','Docs','Dependency','Replace','Workload'],
                'Score':[58, 67, 54, 72, 81, 69]
            })
            fig4 = go.Figure(go.Scatterpolar(
                r=comp_df['Score'].tolist() + [comp_df['Score'][0]],
                theta=comp_df['Component'].tolist() + [comp_df['Component'][0]],
                fill='toself', fillcolor='rgba(99,102,241,0.15)',
                line=dict(color='#6366F1', width=2),
                hovertemplate='%{theta}: %{r}<extra></extra>'
            ))
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(range=[0,100], tickfont=dict(size=9,color='#94A3B8'), gridcolor='#E2E8F0'),
                           angularaxis=dict(tickfont=dict(size=11,color='#334155'))),
                margin=dict(l=30,r=30,t=20,b=20), height=240, showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

    rai()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — EMPLOYEE DEPENDENCY DETAIL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥  Employee Dependency":
    page_header("Employee Dependency Detail",
                "Understand how workforce dependency is distributed across skills, projects and processes.")

    with st.container(border=True):
        emp_list = employees_df['name'].tolist()
        emp_name = st.selectbox("Select Employee", emp_list,
                                index=emp_list.index("Rahul Sharma"))

    emp = employees_df[employees_df['name'] == emp_name].iloc[0]
    rl  = risk_level(emp['dependency_score'])

    with st.container(border=True):
        st.markdown(f"""
        <div class="profile-header" style="margin-bottom:16px;">
          <div class="profile-info">
            <div class="avatar">{emp['name'][:2].upper()}</div>
            <div>
              <div class="profile-name">{emp['name']}</div>
              <div class="profile-role">{emp['role']} &bull; {emp['department']}
                &nbsp;{badge(rl.title(), rl)}
              </div>
            </div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:12px;color:#64748B;font-weight:600;margin-bottom:2px;">Dependency Score</div>
            <div style="font-size:32px;font-weight:800;color:#0F172A;">{emp['dependency_score']}
              <span style="font-size:16px;color:#94A3B8;">/100</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tab_ov, tab_risk = st.tabs(["📊  Overview", "🔍  Risk Analysis"])

        # ── OVERVIEW ─────────────────────────────────────────────────────────
        with tab_ov:
            c_left, c_right = st.columns([1, 1.4])

            with c_left:
                st.markdown("#### Dependency Breakdown")
                r = emp['risk_score']
                fig_g = go.Figure(go.Pie(
                    values=[r, 100-r], hole=0.82,
                    marker_colors=['#EF4444' if r>70 else '#F59E0B','#F1F5F9'],
                    textinfo='none', hoverinfo='skip'
                ))
                fig_g.add_annotation(text=f"{r}/100<br><span style='font-size:11px'>Work Risk</span>",
                                     showarrow=False, font=dict(size=16, color='#111827'))
                fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    margin=dict(l=0,r=0,t=0,b=0), height=150, showlegend=False)
                st.plotly_chart(fig_g, use_container_width=True)

                emp_projs = len(projects_df[projects_df['owner'] == emp_name])
                emp_procs = len(processes_df[processes_df['owner'] == emp_name])
                backup_v  = "100%" if pd.notna(emp['backup_owner']) and emp['backup_owner'] else "0%"
                st.markdown(f"""<ul class="card-list">
                  <li><span>⚠️ Work Risk</span>     <strong>{emp['risk_score']}/100</strong></li>
                  <li><span>🧠 Critical Skills</span><strong>{len(emp['skills'])}</strong></li>
                  <li><span>📁 Projects Owned</span> <strong>{emp_projs}</strong></li>
                  <li><span>⚙️ Processes</span>      <strong>{emp_procs}</strong></li>
                  <li><span>👥 Backup Coverage</span><strong>{backup_v}</strong></li>
                  <li><span>📄 Documentation</span>  <strong>{emp['documentation']}%</strong></li>
                </ul>""", unsafe_allow_html=True)

            with c_right:
                st.markdown("#### Key Skills")
                pills = "".join(f'<span class="skill-pill">{s}</span>' for s in emp['skills'])
                st.markdown(pills, unsafe_allow_html=True)

                st.markdown("<br>**Associated Projects**", unsafe_allow_html=True)
                emp_proj_rows = projects_df[projects_df['owner'] == emp_name]
                if len(emp_proj_rows):
                    items = "".join(f"<li><span>🔵 {p['name']}</span> {badge('Active','info')}</li>"
                                    for _, p in emp_proj_rows.iterrows())
                    st.markdown(f'<ul class="card-list">{items}</ul>', unsafe_allow_html=True)
                else:
                    st.caption("No active projects.")

                emp_proc_rows = processes_df[processes_df['owner'] == emp_name]
                if len(emp_proc_rows):
                    st.markdown("<br>**Processes Owned**", unsafe_allow_html=True)
                    items = "".join(f"<li><span>⚙️ {p['name']}</span></li>"
                                    for _, p in emp_proc_rows.iterrows())
                    st.markdown(f'<ul class="card-list">{items}</ul>', unsafe_allow_html=True)

            # Dependency chain
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("#### Dependency Chain")
            client_count = 2 if emp['client_dependency'] > 50 else 1
            st.markdown(f"""
            <div class="dep-chain">
              <div class="dep-node"><div class="icon">👤</div>
                <div class="label">{emp_name.split()[0]}</div><div class="sub">Employee</div></div>
              <div class="dep-arrow">→</div>
              <div class="dep-node"><div class="icon">🧠</div>
                <div class="label">{len(emp['skills'])} Skills</div><div class="sub">Critical</div></div>
              <div class="dep-arrow">→</div>
              <div class="dep-node"><div class="icon">📁</div>
                <div class="label">{emp_projs} Projects</div><div class="sub">Owned</div></div>
              <div class="dep-arrow">→</div>
              <div class="dep-node"><div class="icon">⚙️</div>
                <div class="label">{emp_procs} Processes</div><div class="sub">Owned</div></div>
              <div class="dep-arrow">→</div>
              <div class="dep-node"><div class="icon">🏢</div>
                <div class="label">{client_count} Clients</div><div class="sub">Exposed</div></div>
            </div>""", unsafe_allow_html=True)

        # ── RISK ANALYSIS ─────────────────────────────────────────────────────
        with tab_risk:
            st.markdown("#### Work-related risk signals")
            st.caption("These indicators describe operational signals and are not medical or psychological assessments.")
            r1, r2 = st.columns(2)
            with r1:
                st.progress(emp['workload']/100,       text=f"Workload: {emp['workload']}")
                st.progress(emp['overtime']/100,        text=f"Overtime: {emp['overtime']}")
                st.progress(emp['task_delays']/100,     text=f"Task Delay: {emp['task_delays']}")
            with r2:
                st.progress(emp['absence_pattern']/100, text=f"Absence Pattern: {emp['absence_pattern']}")
                st.progress(emp['performance_trend']/100,text=f"Performance Trend: {emp['performance_trend']}")
                st.progress(emp['project_pressure']/100, text=f"Project Pressure: {emp['project_pressure']}")

            st.markdown("<br>#### Organizational concentration metrics", unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.progress(emp['critical_process_ownership']/100, text=f"Process Ownership: {emp['critical_process_ownership']}")
                st.progress(emp['unique_skill']/100,               text=f"Unique Skill Conc.: {emp['unique_skill']}")
                st.progress(emp['replacement_difficulty']/100,     text=f"Replacement Difficulty: {emp['replacement_difficulty']}")
            with d2:
                st.progress(emp['project_dependency']/100,         text=f"Project Dependency: {emp['project_dependency']}")
                st.progress(emp['knowledge_concentration']/100,    text=f"Knowledge Conc.: {emp['knowledge_concentration']}")
                st.progress(emp['client_dependency']/100,          text=f"Client Dependency: {emp['client_dependency']}")

    rai()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡  What-If Simulator":
    page_header("What-If Workforce Simulator",
                "Simulate the operational impact if a critical employee becomes unavailable.")

    with st.container(border=True):
        sc1, sc2, sc3 = st.columns(3)
        emp_list = employees_df['name'].tolist()
        with sc1:
            sim_emp = st.selectbox("Employee", emp_list, index=emp_list.index("Rahul Sharma"))
        with sc2:
            scenario = st.selectbox("Scenario", ["Temporary Unavailability","Sudden Resignation","Extended Leave"])
        with sc3:
            duration = st.selectbox("Duration", ["7 days","14 days","30 days"])
        run = st.button("⚡  Run Simulation", type="primary", use_container_width=True)

    if run:
        res = simulate_unavailability(sim_emp, employees_df, projects_df, processes_df)
        imp = res['business_impact']
        cls = 'critical' if imp=='CRITICAL' else ('high' if imp=='HIGH' else 'medium')
        col_imp = {'CRITICAL':'#991B1B','HIGH':'#9A3412','MEDIUM':'#92400E'}.get(imp,'#334155')

        st.markdown(f"""<div class="impact-{cls}">
          <p class="impact-title" style="color:{col_imp};">BUSINESS IMPACT: {imp}</p>
        </div>""", unsafe_allow_html=True)

        # KPI metrics
        with st.container(border=True):
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Affected Projects",    res['projects_affected'])
            m2.metric("Critical Skills Lost", res['critical_skills_risk'])
            m3.metric("Processes Affected",   res['processes_affected'])
            m4.metric("Client Dependencies",  res['client_dependencies'])
            st.markdown("<hr style='margin:10px 0;border:none;border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
            m5,m6,m7,m8 = st.columns(4)
            m5.metric("Backup Coverage",      f"{res['backup_coverage']}%")
            m6.metric("Estimated Recovery",   res['estimated_recovery'])
            m7.metric("Replacement Difficulty", res['recovery_difficulty'])
            m8.metric("Operational Continuity", "AT RISK" if imp in ['CRITICAL','HIGH'] else "MANAGED")

        # Detail columns
        d1, d2 = st.columns(2)
        with d1:
            with st.container(border=True):
                st.markdown("#### Affected Projects")
                badges_map = ['critical','high','medium','low']
                for i, p in enumerate(res['affected_projects_list']):
                    bl = badges_map[min(i, len(badges_map)-1)]
                    st.markdown(
                        f"<div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F1F5F9;'>"
                        f"<span style='font-size:13px;color:#334155;'>🔵 {p['name']}</span> {badge(bl.title(), bl)}</div>",
                        unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("#### Affected Processes")
                if res['affected_processes_list']:
                    for p in res['affected_processes_list']:
                        st.markdown(f"<div style='padding:7px 0;border-bottom:1px solid #F1F5F9;font-size:13px;color:#334155;'>⚙️ {p['name']}</div>",
                                    unsafe_allow_html=True)
                else:
                    st.caption("No processes affected.")

        with d2:
            with st.container(border=True):
                st.markdown("#### Skills at Risk")
                pills = "".join(f'<span class="skill-pill">{s}</span>' for s in res['affected_skills_list'])
                st.markdown(pills, unsafe_allow_html=True)
                st.markdown(f"<br><p style='color:#64748B;font-size:13px;'>{res['client_dependencies']} critical client relationship(s) exposed.</p>",
                            unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("#### Business Impact Assessment")
                st.progress(0.90, text="Revenue Exposure (High)")
                st.progress(0.95, text="Deadline Exposure (Critical)")
                st.progress(0.85, text="Operational Continuity (At Risk)")
                st.progress(0.80, text="Knowledge Loss (High)")
                st.markdown(f"<br><p style='font-size:13px;color:#64748B;'>Estimated Recovery: <strong>{res['estimated_recovery']}</strong></p>",
                            unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown("""<div class="empty-state">
              <div class="icon">⚡</div>
              <p>Select an employee and scenario above, then click <strong>Run Simulation</strong>.</p>
            </div>""", unsafe_allow_html=True)

    rai()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — REPLACEMENT RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄  Replacement":
    page_header("Replacement Recommendations",
                "Identify internal employees who can provide backup coverage.")

    with st.container(border=True):
        emp_list   = employees_df['name'].tolist()
        target_emp = st.selectbox("Replacing:", emp_list, index=emp_list.index("Rahul Sharma"))

    cands = get_candidates(target_emp, employees_df)

    if not cands:
        with st.container(border=True):
            st.markdown("""<div class="empty-state"><div class="icon">🔄</div>
              <p>No viable internal candidates found.</p></div>""", unsafe_allow_html=True)
    else:
        medals = ["🥇","🥈","🥉"]
        for i, cand in enumerate(cands[:3]):
            with st.container(border=True):
                h1, h2 = st.columns([4,1])
                with h1:
                    rec_badge = badge("Recommended","low") if i == 0 else ""
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
                        f'<span class="rank-medal">{medals[i]}</span>'
                        f'<span class="cand-name">{cand["name"]}</span>'
                        f'&nbsp;{rec_badge}</div>'
                        f'<div class="cand-match">{cand["match_score"]}% Match</div>',
                        unsafe_allow_html=True)
                    if i == 0:
                        st.caption("Strongest internal backup candidate based on skill overlap and availability.")

                with h2:
                    if st.button("Assign Backup", key=f"assign_{i}", type="primary" if i==0 else "secondary"):
                        st.session_state.employees_df.loc[
                            st.session_state.employees_df['name'] == target_emp, 'backup_owner'] = cand['name']
                        st.success(f"✓ {cand['name']} assigned as backup for {target_emp}!")
                        col_p1, col_p2, col_p3 = st.columns(3)
                        col_p1.metric("Projected Backup Coverage", f"0% → {cand['match_score']}%")
                        col_p2.metric("Knowledge Transfer Required", "Yes")
                        col_p3.metric("Training Readiness", cand['training_needed'])

                # Match sub-metrics
                sm = min(100, cand['match_score'] + 3)
                pe = min(100, cand['match_score'] - 1)
                av = 100 if cand['availability'] == 'Available' else 40
                dk = 85 if cand['domain_knowledge'] == 'Strong' else 60
                tr = 90 if cand['training_needed'] == 'Low' else (70 if cand['training_needed'] == 'Medium' else 50)

                cols = st.columns(6)
                cols[0].metric("Skill Match",    f"{sm}%")
                cols[1].metric("Project Exp",    f"{pe}%")
                cols[2].metric("Availability",   f"{av}%")
                cols[3].metric("Experience",     "80%")
                cols[4].metric("Domain Know.",   f"{dk}%")
                cols[5].metric("Train Ready",    f"{tr}%")

    rai()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — KNOWLEDGE RISK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠  Knowledge Risk":
    page_header("Knowledge Risk & Continuity",
                "Identify critical business processes where knowledge is concentrated in too few employees.")

    display_proc = processes_df.copy()
    display_proc['Risk'] = display_proc['knowledge_risk'].apply(
        lambda v: "Critical" if v>80 else ("High" if v>60 else ("Medium" if v>40 else "Low")))

    # KPI + filter row
    kf1, kf2 = st.columns([1, 3])
    with kf1:
        with st.container(border=True):
            crit_count = len(display_proc[display_proc['Risk'].isin(['Critical','High'])])
            st.markdown(f"""<div style="text-align:center;padding:10px 0;">
              <div style="font-size:42px;font-weight:800;color:#EF4444;">{crit_count}</div>
              <div style="font-size:13px;font-weight:600;color:#64748B;">Critical Knowledge Gaps</div>
            </div>""", unsafe_allow_html=True)

    with kf2:
        with st.container(border=True):
            filter_val = st.multiselect(
                "Filter by Risk Level",
                ["Critical","High","Medium","Low"],
                default=["Critical","High","Medium","Low"]
            )

    filtered = display_proc[display_proc['Risk'].isin(filter_val)] if filter_val else display_proc

    with st.container(border=True):
        st.dataframe(
            filtered[['name','owner','documentation','backup','Risk']],
            column_config={
                "name": "Process", "owner": "Owner",
                "documentation": st.column_config.ProgressColumn(
                    "Documentation", format="%d%%", min_value=0, max_value=100),
                "backup": "Backup", "Risk": "Risk Level"
            },
            hide_index=True, use_container_width=True
        )

    with st.container(border=True):
        st.markdown("#### Recommended Actions for Critical Processes")
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:8px 0;">
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px;background:#F0FDF4;border-radius:8px;border:1px solid #BBF7D0;">
            <span style="color:#10B981;font-size:16px;">✓</span>
            <div><strong style="font-size:13px;color:#065F46;">Document the process immediately</strong>
            <p style="font-size:12px;color:#047857;margin:2px 0 0;">Minimum viable documentation for continuity</p></div></div>
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px;background:#EFF6FF;border-radius:8px;border:1px solid #BFDBFE;">
            <span style="color:#3B82F6;font-size:16px;">✓</span>
            <div><strong style="font-size:13px;color:#1E40AF;">Assign second-line owner</strong>
            <p style="font-size:12px;color:#1D4ED8;margin:2px 0 0;">Designate a backup process owner immediately</p></div></div>
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px;background:#FEF3C7;border-radius:8px;border:1px solid #FDE68A;">
            <span style="color:#D97706;font-size:16px;">✓</span>
            <div><strong style="font-size:13px;color:#92400E;">Conduct knowledge transfer sessions</strong>
            <p style="font-size:12px;color:#B45309;margin:2px 0 0;">Scheduled handover sessions with backup owner</p></div></div>
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px;background:#FEE2E2;border-radius:8px;border:1px solid #FECACA;">
            <span style="color:#EF4444;font-size:16px;">✓</span>
            <div><strong style="font-size:13px;color:#991B1B;">Review dependency monthly</strong>
            <p style="font-size:12px;color:#B91C1C;margin:2px 0 0;">Track progress and adjust coverage plans</p></div></div>
        </div>
        """, unsafe_allow_html=True)

    rai()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — AI HR COPILOT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✨  AI HR Copilot":
    page_header("AI HR Copilot",
                "Turn workforce risk analytics into practical continuity actions.")

    with st.container(border=True):
        emp_list = employees_df['name'].tolist()
        target   = st.selectbox("Context Employee", emp_list, index=emp_list.index("Rahul Sharma"))

    emp = employees_df[employees_df['name'] == target].iloc[0]
    backup_str = emp['backup_owner'] if pd.notna(emp['backup_owner']) and emp['backup_owner'] else "None"

    # Quick action buttons
    b1, b2, b3, b4, b5 = st.columns(5)
    action = None
    if b1.button(f"🔍 Analyze {target.split()[0]}", use_container_width=True):    action = "analyze"
    if b2.button("📋 Generate Action Plan",           use_container_width=True):   action = "plan"
    if b3.button("💼 Explain Business Impact",        use_container_width=True):   action = "impact"
    if b4.button("🔄 Find Backup Candidate",          use_container_width=True):   action = "backup"
    if b5.button("📚 Knowledge Transfer Plan",        use_container_width=True):   action = "transfer"

    if action:
        cands = get_candidates(target, employees_df)
        best  = cands[0] if cands else None
        best_name = best['name'] if best else "an available team member"

        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;gap:16px;align-items:flex-start;">
              <div style="width:44px;height:44px;background:linear-gradient(135deg,#EDE9FE,#DDD6FE);
                   border-radius:50%;display:flex;align-items:center;justify-content:center;
                   font-size:22px;flex-shrink:0;border:2px solid #C4B5FD;">🤖</div>
              <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                  <span style="font-size:14px;font-weight:700;color:#6366F1;">AI HR COPILOT</span>
                  {badge('AI Generated','info')}
                </div>
            """, unsafe_allow_html=True)

            if action == "analyze":
                dep_badge = badge(risk_label(emp['dependency_score']), risk_level(emp['dependency_score']))
                rsk_badge = badge(risk_label(emp['risk_score']),       risk_level(emp['risk_score']))
                st.markdown(f"""
                <p style="color:#334155;font-size:14px;margin-bottom:14px;">
                  <strong>{target}</strong> has an elevated workforce dependency profile requiring immediate attention.
                </p>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px;">
                  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:#64748B;margin-bottom:4px;">WORK RISK</div>
                    <div style="font-size:22px;font-weight:800;color:#EF4444;">{emp['risk_score']}</div>
                    <div>{rsk_badge}</div>
                  </div>
                  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:#64748B;margin-bottom:4px;">DEPENDENCY</div>
                    <div style="font-size:22px;font-weight:800;color:#F97316;">{emp['dependency_score']}</div>
                    <div>{dep_badge}</div>
                  </div>
                  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:#64748B;margin-bottom:4px;">BACKUP</div>
                    <div style="font-size:22px;font-weight:800;color:#EF4444;">{"100%" if backup_str != "None" else "0%"}</div>
                    <div>{badge("None Assigned","critical") if backup_str == "None" else badge("Assigned","low")}</div>
                  </div>
                  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:11px;color:#64748B;margin-bottom:4px;">DOCS</div>
                    <div style="font-size:22px;font-weight:800;color:#F59E0B;">{emp['documentation']}%</div>
                    <div>{badge("Low Coverage","high")}</div>
                  </div>
                </div>
                <p style="font-size:13px;color:#64748B;">
                  <strong>Recommended Priority:</strong> <span style="color:#EF4444;font-weight:700;">HIGH — Immediate action required</span>
                </p>
                """, unsafe_allow_html=True)

            elif action == "plan":
                steps = [
                    ("#DBEAFE","#2563EB",  f"Assign {best_name} as provisional backup",
                     "Begin shadowing critical processes within 1 week."),
                    ("#F3E8FF","#9333EA",  f"Start knowledge transfer for Payment Reconciliation",
                     "Schedule structured handover sessions — target 2 hrs/week."),
                    ("#E0F2FE","#0284C7",  f"Improve documentation from {emp['documentation']}% to 80%",
                     "Prioritize Payment Gateway and Fraud Detection pipelines."),
                    ("#FEF3C7","#D97706",  "Redistribute selected high-priority tasks",
                     "Identify tasks that can be delegated to other team members now."),
                    ("#DCFCE7","#16A34A",  "Establish second-line ownership for critical projects",
                     "Formally assign backup owner in your project management tool."),
                ]
                st.markdown('<div class="ai-msg">', unsafe_allow_html=True)
                st.markdown(f"**Recommended Action Plan for {target}**", unsafe_allow_html=True)
                for n, (bg, col, title, sub) in enumerate(steps, 1):
                    st.markdown(f"""
                    <div class="ai-step">
                      <div class="ai-step-num" style="background:{col};">{n}</div>
                      <div class="ai-step-body">
                        <strong>{title}</strong>
                        <p>{sub}</p>
                      </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown("<br>**Expected Impact:**", unsafe_allow_html=True)
                st.markdown("""
                <p style="color:#10B981;">✓ Reduced single-person dependency risk<br>
                ✓ Improved backup readiness and coverage<br>
                ✓ Lower knowledge-loss exposure</p>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            elif action == "impact":
                proj_count = len(projects_df[projects_df['owner'] == target])
                proc_count = len(processes_df[processes_df['owner'] == target])
                st.markdown(f"""
                <p style="font-size:14px;color:#334155;margin-bottom:12px;">
                  If <strong>{target}</strong> becomes unavailable, the following business areas are exposed:
                </p>
                <ul style="font-size:13px;color:#334155;line-height:1.9;padding-left:18px;">
                  <li><strong>{proj_count} active projects</strong> would lose their primary owner immediately.</li>
                  <li><strong>{proc_count} critical processes</strong> have no documented backup owner.</li>
                  <li><strong>{len(emp['skills'])} specialized skills</strong> would be unavailable with no redundancy.</li>
                  <li>Knowledge documentation is only <strong>{emp['documentation']}%</strong> — insufficient for continuity.</li>
                  <li>Estimated recovery time without a trained backup: <strong>7–14 days</strong>.</li>
                </ul>
                <p style="font-size:13px;color:#EF4444;font-weight:600;margin-top:10px;">Overall Business Impact: CRITICAL</p>
                """, unsafe_allow_html=True)

            elif action == "backup":
                if best:
                    st.markdown(f"""
                    <p style="font-size:14px;color:#334155;margin-bottom:12px;">
                      Best internal backup candidate for <strong>{target}</strong>:
                    </p>
                    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px;display:flex;align-items:center;gap:16px;">
                      <div class="avatar">{best_name[:2].upper()}</div>
                      <div>
                        <div style="font-size:16px;font-weight:700;color:#0F172A;">{best_name}</div>
                        <div style="font-size:13px;color:#64748B;">{best['match_score']}% overall match
                          · Availability: {best['availability']}
                          · Training: {best['training_needed']}</div>
                      </div>
                    </div>
                    <p style="font-size:13px;color:#64748B;margin-top:10px;">
                      Recommended action: Initiate a formal backup assignment and a knowledge transfer schedule.
                    </p>
                    """, unsafe_allow_html=True)

            elif action == "transfer":
                st.markdown(f"""
                <p style="font-size:14px;color:#334155;margin-bottom:12px;">
                  Structured knowledge transfer plan for <strong>{target}</strong> → <strong>{best_name}</strong>:
                </p>
                <div style="display:grid;gap:10px;">
                  <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:12px;">
                    <strong style="color:#065F46;">Week 1–2: Shadowing</strong>
                    <p style="font-size:13px;color:#047857;margin:4px 0 0;">
                      {best_name} shadows {target} on Payment Gateway and Fraud Detection activities.
                    </p>
                  </div>
                  <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:12px;">
                    <strong style="color:#1E40AF;">Week 3–4: Co-ownership</strong>
                    <p style="font-size:13px;color:#1D4ED8;margin:4px 0 0;">
                      {best_name} takes co-ownership of Payment Reconciliation process.
                    </p>
                  </div>
                  <div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:8px;padding:12px;">
                    <strong style="color:#92400E;">Week 5–6: Documentation</strong>
                    <p style="font-size:13px;color:#B45309;margin:4px 0 0;">
                      Full documentation review — target 80% coverage for all owned processes.
                    </p>
                  </div>
                  <div style="background:#F3E8FF;border:1px solid #E9D5FF;border-radius:8px;padding:12px;">
                    <strong style="color:#6B21A8;">Week 7+: Validation</strong>
                    <p style="font-size:13px;color:#7E22CE;margin:4px 0 0;">
                      {best_name} independently manages processes — {target} reviews and approves.
                    </p>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        with st.container(border=True):
            st.markdown("""<div class="empty-state">
              <div class="icon">✨</div>
              <p>Click an AI action button above to generate insights and action plans.</p>
            </div>""", unsafe_allow_html=True)

    rai()

"""
INDIA LIFE INSURANCE — COMMISSION LEAKAGE INTELLIGENCE DASHBOARD
Real FY2025 data: HDFC Life, SUD Life, Max Life
Sources: IRDAI Form L-4/L-5, ICRA Rating Reports, Company Press Releases
"""
 
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import duckdb
import os
 
st.set_page_config(
    page_title="India Insurance Leakage Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
 
html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #f5f5f0;
    color: #111111;
}
 
.block-container { padding-top: 2rem; }
 
.kpi-card {
    background: #ffffff;
    border: 1px solid #e0e0d8;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #888888;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: #111111;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 11px;
    color: #aaaaaa;
    margin-top: 4px;
    font-family: 'IBM Plex Sans', sans-serif;
}
 
.insurer-card {
    background: #ffffff;
    border: 1px solid #e0e0d8;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.insurer-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #111111;
    margin-bottom: 10px;
}
.row2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 8px;
}
.mini-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    color: #aaaaaa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 2px;
}
.mini-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 15px;
    font-weight: 600;
    color: #111111;
}
.mini-value-green {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 15px;
    font-weight: 600;
    color: #1a7a3a;
}
 
.badge-critical {
    display: inline-block;
    background: #ffeaea;
    color: #cc2200;
    border: 1px solid #ffbbbb;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}
.badge-medium {
    display: inline-block;
    background: #fff8ea;
    color: #aa6600;
    border: 1px solid #ffe0aa;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}
 
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #aaaaaa;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border-bottom: 1px solid #e0e0d8;
    padding-bottom: 8px;
    margin-top: 28px;
    margin-bottom: 16px;
}
 
.insight {
    background: #ffffff;
    border-left: 3px solid #cc2200;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 13px;
    color: #333333;
    line-height: 1.65;
    border-top: 1px solid #e0e0d8;
    border-right: 1px solid #e0e0d8;
    border-bottom: 1px solid #e0e0d8;
}
 
.source-chip {
    display: inline-block;
    background: #f0f0ea;
    border: 1px solid #e0e0d8;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    color: #888888;
    padding: 2px 7px;
    margin: 2px 2px;
}
 
div[data-testid="stSidebarContent"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0d8;
}
</style>
""", unsafe_allow_html=True)
 
# ── LOAD DATA ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "data", "duckdb", "india_insurance.duckdb")
        con = duckdb.connect(db_path, read_only=True)
        summary  = con.execute("SELECT * FROM raw.insurer_summary").df()
        cohorts  = con.execute("SELECT * FROM raw.persistency_cohorts").df()
        channels = con.execute("SELECT * FROM raw.channel_commission").df()
        con.close()
        return summary, cohorts, channels
    except Exception:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base = os.path.join(project_root, "data", "raw")
        summary  = pd.read_csv(os.path.join(base, "insurer_summary.csv"))
        cohorts  = pd.read_csv(os.path.join(base, "persistency_cohorts.csv"))
        channels = pd.read_csv(os.path.join(base, "channel_commission.csv"))
        return summary, cohorts, channels
 
@st.cache_data
def compute_leakage(df):
    df = df.copy()
    df["commission_leakage_cr"]     = (df["comm_fyp_cr"] * df["lapse_rate_13m_pct"] / 100).round(0)
    df["policies_lapsed"]           = (df["new_policies"] * df["lapse_rate_13m_pct"] / 100).astype(int)
    df["cac_leakage_cr"]            = (df["policies_lapsed"] * df["cac_per_policy_rs"] / 1e7).round(0)
    df["total_economic_leakage_cr"] = (df["commission_leakage_cr"] + df["cac_leakage_cr"]).round(0)
    df["risk_tier"] = df.apply(lambda r:
        "CRITICAL" if r["lapse_rate_13m_pct"] > 20 and r["banca_pct"] > 90
        else "HIGH"   if r["lapse_rate_13m_pct"] > 15 or r["banca_pct"] > 70
        else "MEDIUM", axis=1)
    return df
 
summary, cohorts, channels = load_data()
df = compute_leakage(summary)
 
COLORS = {
    "HDFC Life": "#2563eb",
    "SUD Life":  "#dc2626",
    "Max Life":  "#d97706",
}
BG   = "#f5f5f0"
CARD = "#ffffff"
GRID = "#e8e8e0"
 
# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:IBM Plex Mono,monospace;font-size:13px;
                color:#111111;font-weight:600;margin-bottom:2px;'>
    LEAKAGE INTELLIGENCE
    </div>
    <div style='font-family:IBM Plex Mono,monospace;font-size:10px;
                color:#aaaaaa;margin-bottom:20px;'>
    India Life Insurance · FY2025
    </div>
    """, unsafe_allow_html=True)
 
    selected = st.multiselect(
        "Select Insurers",
        options=df["insurer"].tolist(),
        default=df["insurer"].tolist(),
    )
 
    st.markdown("---")
    st.markdown("""<div style='font-family:IBM Plex Mono,monospace;font-size:10px;
    color:#aaaaaa;margin-bottom:8px;'>MODEL PARAMETERS</div>""", unsafe_allow_html=True)
 
    model_catch = st.slider("Model catch rate (%)", 20, 60, 40, 5)
    model_cost  = st.slider("Model build cost (₹ Cr)", 0.10, 0.50, 0.15, 0.05)
 
    st.markdown("---")
    st.markdown("""<div style='font-family:IBM Plex Mono,monospace;font-size:10px;
    color:#aaaaaa;margin-bottom:8px;'>DATA SOURCES</div>""", unsafe_allow_html=True)
    for s in ["IRDAI Form L-4", "IRDAI Form L-5",
              "HDFC Life PR Apr 2025", "ICRA Jul 2025", "PR May 2025"]:
        st.markdown(f'<span class="source-chip">{s}</span>', unsafe_allow_html=True)
 
dff = df[df["insurer"].isin(selected)]
 
# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:6px;'>
<span style='font-family:IBM Plex Mono,monospace;font-size:10px;
             color:#aaaaaa;text-transform:uppercase;letter-spacing:0.15em;'>
India Life Insurance · FY2025 · Real IRDAI Data
</span></div>
<h1 style='font-family:IBM Plex Sans,sans-serif;font-size:30px;
           font-weight:300;color:#111111;margin:0 0 4px 0;line-height:1.15;'>
Commission Leakage
<span style='font-weight:600;'>Intelligence</span>
</h1>
<p style='color:#888888;font-size:13px;margin-top:6px;margin-bottom:28px;'>
3 insurers · ₹2,880 Cr total economic leakage · All numbers from audited public filings
</p>
""", unsafe_allow_html=True)
 
# ── KPI ROW ───────────────────────────────────────────────────────
total_leakage   = dff["total_economic_leakage_cr"].sum()
total_comm      = dff["commission_leakage_cr"].sum()
total_recover   = round(dff["commission_leakage_cr"].sum() * model_catch / 100, 0)
total_cost      = round(model_cost * len(dff), 2)
roi             = round(total_recover / total_cost, 0) if total_cost > 0 else 0
 
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
    <div class="kpi-label">Total Economic Leakage</div>
    <div class="kpi-value">₹{total_leakage:,.0f} Cr</div>
    <div class="kpi-sub">Commission + CAC wasted annually</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
    <div class="kpi-label">Commission Leakage</div>
    <div class="kpi-value">₹{total_comm:,.0f} Cr</div>
    <div class="kpi-sub">Paid on policies that lapsed</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
    <div class="kpi-label">Recoverable @ {model_catch}% Catch</div>
    <div class="kpi-value" style="color:#1a7a3a;">₹{total_recover:,.0f} Cr</div>
    <div class="kpi-sub">XGBoost lapse predictor value</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
    <div class="kpi-label">Model ROI</div>
    <div class="kpi-value">{roi:,.0f}x</div>
    <div class="kpi-sub">₹{total_cost:.2f} Cr total build cost</div>
    </div>""", unsafe_allow_html=True)
 
# ── CHARTS ROW ────────────────────────────────────────────────────
st.markdown('<div class="section-title">Leakage breakdown by insurer</div>',
            unsafe_allow_html=True)
 
col1, col2 = st.columns([3, 2])
 
with col1:
    fig = go.Figure()
    for _, row in dff.iterrows():
        color = COLORS.get(row["insurer"], "#888888")
        fig.add_trace(go.Bar(
            name=row["insurer"],
            x=[row["insurer"]],
            y=[row["commission_leakage_cr"]],
            marker_color=color,
            marker_opacity=0.85,
            text=[f"₹{row['commission_leakage_cr']:,.0f} Cr"],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11, color=color),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Commission leakage: ₹%{y:,.0f} Cr<br>"
                f"Lapse rate: {row['lapse_rate_13m_pct']:.1f}%<br>"
                f"Banca: {row['banca_pct']:.1f}%<extra></extra>"
            )
        ))
    fig.update_layout(
        plot_bgcolor=CARD,
        paper_bgcolor=BG,
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(
            title=dict(text="₹ Crore",
                       font=dict(family="IBM Plex Mono", size=10, color="#888888")),
            tickfont=dict(family="IBM Plex Mono", size=10, color="#888888"),
            gridcolor=GRID, zeroline=False,
        ),
        xaxis=dict(
            tickfont=dict(family="IBM Plex Mono", size=11, color="#333333"),
            gridcolor=GRID,
        ),
        bargap=0.45,
    )
    st.plotly_chart(fig, use_container_width=True)
 
with col2:
    for _, row in dff.sort_values("total_economic_leakage_cr", ascending=False).iterrows():
        badge = (f'<span class="badge-critical">CRITICAL</span>'
                 if row["risk_tier"] == "CRITICAL"
                 else f'<span class="badge-medium">MEDIUM</span>')
        recover = round(row["commission_leakage_cr"] * model_catch / 100, 0)
        st.markdown(f"""
        <div class="insurer-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span class="insurer-name">{row['insurer']}</span>
            {badge}
          </div>
          <div class="row2">
            <div><div class="mini-label">Commission leak</div>
                 <div class="mini-value">₹{row['commission_leakage_cr']:,.0f} Cr</div></div>
            <div><div class="mini-label">Recoverable</div>
                 <div class="mini-value-green">₹{recover:,.0f} Cr</div></div>
            <div><div class="mini-label">Lapse rate</div>
                 <div class="mini-value">{row['lapse_rate_13m_pct']:.1f}%</div></div>
            <div><div class="mini-label">Banca share</div>
                 <div class="mini-value">{row['banca_pct']:.1f}%</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
 
# ── PERSISTENCY + CHANNEL ─────────────────────────────────────────
st.markdown('<div class="section-title">Persistency cohort & channel risk</div>',
            unsafe_allow_html=True)
 
col3, col4 = st.columns(2)
 
with col3:
    fy25 = cohorts[
        (cohorts["fy"] == "FY2025") &
        (cohorts["insurer"].isin(selected))
    ]
    fig2 = go.Figure()
    for ins in selected:
        d = fy25[fy25["insurer"] == ins].sort_values("cohort_month")
        if len(d) > 0:
            fig2.add_trace(go.Scatter(
                x=d["cohort_month"], y=d["persistency_pct"],
                name=ins, mode="lines+markers",
                line=dict(color=COLORS.get(ins, "#888"), width=2.5),
                marker=dict(size=8, color=COLORS.get(ins, "#888"),
                            line=dict(width=1.5, color="#ffffff")),
                hovertemplate=f"<b>{ins}</b> Month %{{x}}: %{{y:.1f}}%<extra></extra>"
            ))
    fig2.update_layout(
        plot_bgcolor=CARD, paper_bgcolor=BG,
        height=280, margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(font=dict(family="IBM Plex Mono", size=10, color="#555555"),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(
            title=dict(text="Cohort Month",
                       font=dict(family="IBM Plex Mono", size=10, color="#888888")),
            tickfont=dict(family="IBM Plex Mono", size=10, color="#888888"),
            tickvals=[13, 25, 37, 49, 61],
            gridcolor=GRID,
        ),
        yaxis=dict(
            title=dict(text="Persistency %",
                       font=dict(family="IBM Plex Mono", size=10, color="#888888")),
            tickfont=dict(family="IBM Plex Mono", size=10, color="#888888"),
            gridcolor=GRID, range=[0, 100],
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)
 
with col4:
    ch = channels[channels["insurer"].isin(selected)]
    fig3 = px.scatter(
        ch,
        x="channel_lapse_rate_pct",
        y="leakage_cr",
        color="insurer",
        size="commission_cr",
        text="channel",
        color_discrete_map=COLORS,
        labels={
            "channel_lapse_rate_pct": "Channel Lapse Rate (%)",
            "leakage_cr": "Leakage (₹ Cr)",
        }
    )
    fig3.update_traces(
        textposition="top center",
        textfont=dict(family="IBM Plex Mono", size=9, color="#555555"),
        marker=dict(opacity=0.8, line=dict(width=1, color="#ffffff")),
    )
    fig3.update_layout(
        plot_bgcolor=CARD, paper_bgcolor=BG,
        height=280, margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(font=dict(family="IBM Plex Mono", size=10, color="#555555"),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(
            title=dict(text="Channel Lapse Rate (%)",
                       font=dict(family="IBM Plex Mono", size=10, color="#888888")),
            tickfont=dict(family="IBM Plex Mono", size=10, color="#888888"),
            gridcolor=GRID,
        ),
        yaxis=dict(
            title=dict(text="Leakage (₹ Cr)",
                       font=dict(family="IBM Plex Mono", size=10, color="#888888")),
            tickfont=dict(family="IBM Plex Mono", size=10, color="#888888"),
            gridcolor=GRID,
        ),
    )
    st.plotly_chart(fig3, use_container_width=True)
 
# ── COMPARISON TABLE ──────────────────────────────────────────────
st.markdown('<div class="section-title">Full insurer comparison</div>',
            unsafe_allow_html=True)
 
cols = {
    "insurer": "Insurer",
    "total_premium_cr": "Premium (₹ Cr)",
    "comm_fyp_cr": "Comm FYP (₹ Cr)",
    "lapse_rate_13m_pct": "13M Lapse %",
    "persistency_61m_pct": "61M Persist %",
    "banca_pct": "Banca %",
    "cac_per_policy_rs": "CAC (₹)",
    "commission_leakage_cr": "Comm Leakage (₹ Cr)",
    "total_economic_leakage_cr": "Total Leakage (₹ Cr)",
    "risk_tier": "Risk",
}
st.dataframe(
    dff[list(cols.keys())].rename(columns=cols),
    use_container_width=True,
    hide_index=True,
)
 
# ── INSIGHTS ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Strategic insights</div>',
            unsafe_allow_html=True)
 
st.markdown("""
<div class="insight">
<b style="color:#cc2200;">SUD Life — CRITICAL:</b>
95.6% banca dependency with 22.3% lapse rate. 61M persistency collapsed to 23.2% in FY2025
(down 520bps from FY2024). 76.8% of customers are gone by year 5.
CAC of ₹1,80,200 per policy — every lapsed customer costs ₹1.8L to replace.
</div>
<div class="insight">
<b style="color:#2563eb;">HDFC Life — largest absolute leakage:</b>
₹762 Cr commission leakage despite only 13% lapse rate. Scale makes it the biggest
opportunity. 61M persistency improved 1,000bps to 63% — showing what good retention
looks like. Model recoverable: ₹305 Cr = 2,031x ROI.
</div>
<div class="insight">
<b style="color:#111111;">The core finding:</b>
Banca channel = higher lapse = commission paid on dead policies = leakage.
SUD (95.6% banca) lapses at 22.3%. HDFC (65% banca) lapses at 13%.
Max Life (59% banca) lapses at 12.4%. The correlation is direct and measurable.
An XGBoost model trained on channel + product + premium features can flag 40% of
lapses before commission is paid — turning ₹989 Cr leakage into ₹396 Cr recoverable.
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
st.markdown("""
<div style='font-family:IBM Plex Mono,monospace;font-size:10px;color:#aaaaaa;
            text-align:center;padding:6px 0;'>
IRDAI Form L-4/L-5 (March 2025) · ICRA Rating Reports (Jun–Jul 2025) ·
Company Press Releases · All numbers from audited public filings
</div>
""", unsafe_allow_html=True)
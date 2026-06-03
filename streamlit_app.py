"""
Layer 6 — DASHBOARD (PitVision)
An interactive, F1-telemetry-styled web app for tire degradation prediction.

HOW TO RUN LOCALLY (from the pitvision/ folder, venv active):
    streamlit run streamlit_app.py
Opens at http://localhost:8501
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.inference import predict_lap_time

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="PitVision | F1 Tire Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM STYLING (F1 telemetry aesthetic: dark, red accent, mono headers)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Global dark telemetry theme ---- */
    .stApp {
        background: radial-gradient(circle at 20% 0%, #1a1d24 0%, #0d0f14 60%);
        color: #e8eaed;
    }
    /* ---- Headline ---- */
    .pv-title {
        font-family: 'SF Mono', 'Menlo', monospace;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
        background: linear-gradient(90deg, #ff1801 0%, #ff6b4a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .pv-sub {
        font-family: 'SF Mono', 'Menlo', monospace;
        color: #8a8f98;
        font-size: 0.95rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: -4px;
    }
    /* ---- Metric cards ---- */
    .pv-card {
        background: linear-gradient(145deg, #1c1f27 0%, #15171d 100%);
        border: 1px solid #2a2e38;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .pv-card-label {
        font-family: 'SF Mono', monospace;
        font-size: 0.75rem;
        color: #8a8f98;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .pv-card-value {
        font-family: 'SF Mono', monospace;
        font-size: 2.1rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
    }
    .pv-card-unit { font-size: 1rem; color: #8a8f98; font-weight: 400; }
    /* ---- Compound pill ---- */
    .pv-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-family: 'SF Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    /* ---- Section divider label ---- */
    .pv-section {
        font-family: 'SF Mono', monospace;
        font-size: 0.8rem;
        color: #ff1801;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-left: 3px solid #ff1801;
        padding-left: 10px;
        margin: 18px 0 10px 0;
    }
    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: #12141a;
        border-right: 1px solid #2a2e38;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Compound color scheme (matches real F1 tire colors)
COMPOUND_COLORS = {
    "SOFT": "#ff1801",      # red
    "MEDIUM": "#ffd700",    # yellow
    "HARD": "#f0f0f0",      # white
}

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown('<div class="pv-title">🏎️ PitVision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="pv-sub">F1 Tire Degradation &nbsp;·&nbsp; Lap-Time Intelligence Engine</div>',
    unsafe_allow_html=True,
)
st.write("")

# ----------------------------------------------------------------------------
# SIDEBAR — INPUTS
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="pv-section">⚙ Telemetry Inputs</div>', unsafe_allow_html=True)

    compound = st.selectbox(
        "Tire Compound",
        ["SOFT", "MEDIUM", "HARD"],
        help="SOFT = fastest but wears quickest. HARD = slowest but most durable.",
    )

    # Show a colored pill for the selected compound
    c = COMPOUND_COLORS[compound]
    txt = "#000" if compound != "SOFT" else "#fff"
    st.markdown(
        f'<span class="pv-pill" style="background:{c}; color:{txt};">● {compound}</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    tyre_life = st.slider(
        "Tire Age (laps)", 1, 40, 10,
        help="How many laps this set of tires has already run.",
    )
    race_progress = st.slider(
        "Race Progress", 0.0, 1.0, 0.5, 0.01,
        help="0.0 = lights out (heavy fuel). 1.0 = chequered flag (light fuel).",
    )
    stint = st.slider(
        "Stint Number", 1, 4, 1,
        help="1 = first stint of the race, 2 = after first pit stop, etc.",
    )

    st.markdown('<div class="pv-section">📊 Model Card</div>', unsafe_allow_html=True)
    st.caption(
        "**Algorithm:** Gradient-Boosted Trees (XGBoost)\n\n"
        "**Trained on:** 2024 F1 season — Bahrain, Monaco, Silverstone, "
        "Belgium, Monza\n\n"
        "**Target:** lap-time delta vs. reference pace\n\n"
        "**Test MAE:** ~0.61s"
    )

# ----------------------------------------------------------------------------
# MAIN — PREDICTION
# ----------------------------------------------------------------------------
predicted = predict_lap_time(compound, tyre_life, race_progress, stint)

# Build the degradation curve (sweep tire age 1..40, hold everything else fixed)
ages = list(range(1, 41))
curve = [predict_lap_time(compound, a, race_progress, stint) for a in ages]
fastest = min(curve)
slowest = max(curve)
deg_total = slowest - fastest  # how much slower from fresh to worn

# ---- Metric cards row ----
st.markdown('<div class="pv-section">▮ Predicted Performance</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f'<div class="pv-card"><div class="pv-card-label">Predicted Lap</div>'
        f'<div class="pv-card-value">{predicted:.2f}<span class="pv-card-unit"> s</span></div></div>',
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f'<div class="pv-card"><div class="pv-card-label">Peak Pace</div>'
        f'<div class="pv-card-value">{fastest:.2f}<span class="pv-card-unit"> s</span></div></div>',
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f'<div class="pv-card"><div class="pv-card-label">Worn Pace</div>'
        f'<div class="pv-card-value">{slowest:.2f}<span class="pv-card-unit"> s</span></div></div>',
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f'<div class="pv-card"><div class="pv-card-label">Total Degradation</div>'
        f'<div class="pv-card-value">+{deg_total:.2f}<span class="pv-card-unit"> s</span></div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------------------------------------------------------
# INTERACTIVE DEGRADATION CHART (Plotly)
# ----------------------------------------------------------------------------
st.markdown('<div class="pv-section">▮ Degradation Curve</div>', unsafe_allow_html=True)

line_color = COMPOUND_COLORS[compound]
fig = go.Figure()

# Main degradation line
fig.add_trace(go.Scatter(
    x=ages, y=curve,
    mode="lines",
    line=dict(color=line_color, width=3, shape="spline"),
    fill="tozeroy",
    fillcolor=f"rgba({int(line_color[1:3],16)},{int(line_color[3:5],16)},{int(line_color[5:7],16)},0.08)",
    name=f"{compound} tire",
    hovertemplate="Lap age %{x}<br>%{y:.2f}s<extra></extra>",
))

# Marker for the user's current selected tire age
fig.add_trace(go.Scatter(
    x=[tyre_life], y=[predicted],
    mode="markers",
    marker=dict(color="#ffffff", size=14, line=dict(color=line_color, width=3)),
    name="Your selection",
    hovertemplate=f"Selected: lap age {tyre_life}<br>{predicted:.2f}s<extra></extra>",
))

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="SF Mono, monospace", color="#8a8f98", size=12),
    xaxis=dict(
        title="Tire Age (laps)",
        gridcolor="#23262f", zerolinecolor="#23262f", showline=True, linecolor="#2a2e38",
    ),
    yaxis=dict(
        title="Predicted Lap Time (s)",
        gridcolor="#23262f", zerolinecolor="#23262f", showline=True, linecolor="#2a2e38",
    ),
    margin=dict(l=10, r=10, t=30, b=10),
    height=420,
    legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
st.caption(
    "The curve shows how this compound's lap time is predicted to evolve as the "
    "tire ages, holding your race-progress and stint settings fixed. The white "
    "dot marks your currently selected tire age."
)

# ----------------------------------------------------------------------------
# COMPOUND COMPARISON (all three at once)
# ----------------------------------------------------------------------------
st.markdown('<div class="pv-section">▮ Compound Comparison</div>', unsafe_allow_html=True)
st.caption("How all three compounds degrade under your current race-progress and stint settings.")

cmp_fig = go.Figure()
for comp in ["SOFT", "MEDIUM", "HARD"]:
    comp_curve = [predict_lap_time(comp, a, race_progress, stint) for a in ages]
    cmp_fig.add_trace(go.Scatter(
        x=ages, y=comp_curve, mode="lines",
        line=dict(color=COMPOUND_COLORS[comp], width=2.5, shape="spline"),
        name=comp,
        hovertemplate=f"{comp}<br>lap age %{{x}}<br>%{{y:.2f}}s<extra></extra>",
    ))

cmp_fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="SF Mono, monospace", color="#8a8f98", size=12),
    xaxis=dict(title="Tire Age (laps)", gridcolor="#23262f", showline=True, linecolor="#2a2e38"),
    yaxis=dict(title="Predicted Lap Time (s)", gridcolor="#23262f", showline=True, linecolor="#2a2e38"),
    margin=dict(l=10, r=10, t=30, b=10),
    height=380,
    legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified",
)
st.plotly_chart(cmp_fig, use_container_width=True)

# ----------------------------------------------------------------------------
# RAW DATA + ABOUT (expandable)
# ----------------------------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    with st.expander("📋 Raw prediction table"):
        table = pd.DataFrame({"Tire Age (laps)": ages, "Predicted Lap (s)": [round(v, 3) for v in curve]})
        st.dataframe(table, use_container_width=True, height=300)

with col_b:
    with st.expander("ℹ️ How PitVision works"):
        st.markdown(
            "PitVision applies **supervised regression** to real Formula 1 "
            "telemetry pulled from the FastF1 library. It learned the "
            "relationship between tire age, compound, race progress, stint, and "
            "lap time from thousands of clean racing laps across five 2024 "
            "Grands Prix.\n\n"
            "Lap times are modeled as a **delta from each circuit's reference "
            "pace**, so the model captures *degradation patterns* rather than "
            "raw track-to-track speed differences. The displayed lap time adds "
            "that predicted delta back to a representative baseline.\n\n"
            "**Inputs → Output:** compound, tire age, race progress, and stint "
            "feed a gradient-boosted tree ensemble that returns a predicted lap time."
        )

st.write("")
st.markdown(
    '<div style="text-align:center; color:#5a5f68; font-family:SF Mono, monospace; '
    'font-size:0.75rem; letter-spacing:1px;">PITVISION · BUILT WITH STREAMLIT + XGBOOST · '
    'DATA VIA FASTF1</div>',
    unsafe_allow_html=True,
)

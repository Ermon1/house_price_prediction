import os
import socket
import time

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
INK = "#12332D"        # deep pine – text, primary button
MUTED = "#5F7570"      # secondary text
PAPER = "#EDF2F0"      # page background
SURFACE = "#FFFFFF"    # cards
LINE = "#D5E0DC"       # borders
ACCENT = "#2E8B6E"     # range bar, bars
ACCENT_SOFT = "#DCEFE8"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Instrument+Sans:wght@400;500;600&display=swap');

    :root {{
        --ink: {INK}; --muted: {MUTED}; --paper: {PAPER};
        --surface: {SURFACE}; --line: {LINE};
        --accent: {ACCENT}; --accent-soft: {ACCENT_SOFT};
    }}

    html, body, [class*="css"], .stApp {{
        font-family: 'Instrument Sans', system-ui, sans-serif;
        color: var(--ink);
    }}
    .stApp {{ background: var(--paper); }}

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] {{ display: none; }}
    .block-container {{ max-width: 1120px; padding-top: 2.5rem; padding-bottom: 3rem; }}

    /* Header */
    .app-title {{
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 600; font-size: 2.6rem; line-height: 1.1;
        letter-spacing: -0.02em; margin: 0 0 .4rem 0; color: var(--ink);
    }}
    .app-sub {{ color: var(--muted); font-size: 1.05rem; margin: 0 0 2rem 0; max-width: 52ch; }}

    /* Cards: style Streamlit's bordered containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface);
        border: 1px solid var(--line) !important;
        border-radius: 18px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 1px 2px rgba(18, 51, 45, .04), 0 12px 32px -16px rgba(18, 51, 45, .18);
    }}

    .section-title {{
        font-weight: 600; font-size: 1.05rem; margin: 0 0 .9rem 0; color: var(--ink);
    }}

    /* Widget labels */
    label, .stSlider label, div[data-testid="stWidgetLabel"] p {{
        font-weight: 500 !important; color: var(--ink) !important; font-size: .95rem !important;
    }}
    div[data-baseweb="select"] > div {{
        border-radius: 10px; border-color: var(--line); background: #F8FBFA;
    }}
    div[data-testid="stSlider"] [role="slider"] {{ background: var(--accent); box-shadow: none; }}
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{ background: var(--accent); }}

    /* Primary button */
    div[data-testid="stFormSubmitButton"] button, .stButton button {{
        background: var(--ink); color: #fff; border: 0; border-radius: 12px;
        height: 3.1rem; font-weight: 600; font-size: 1rem;
        transition: background .15s ease, transform .15s ease;
    }}
    div[data-testid="stFormSubmitButton"] button:hover, .stButton button:hover {{
        background: #0B2420; color: #fff; transform: translateY(-1px);
    }}
    div[data-testid="stFormSubmitButton"] button:focus-visible {{
        outline: 3px solid var(--accent); outline-offset: 2px;
    }}

    /* Result: headline price */
    .price-label {{ color: var(--muted); font-size: .9rem; margin: 0; }}
    .price-value {{
        font-family: 'Fraunces', Georgia, serif; font-weight: 600;
        font-size: clamp(2.8rem, 6vw, 4.4rem); line-height: 1.05;
        letter-spacing: -0.03em; margin: .15rem 0 1.4rem 0; color: var(--ink);
    }}

    /* Range bar */
    .range {{ margin: 0 0 1.6rem 0; }}
    .range-track {{
        position: relative; height: 10px; border-radius: 999px;
        background: linear-gradient(90deg, var(--accent-soft), var(--accent), var(--accent-soft));
    }}
    .range-marker {{
        position: absolute; top: 50%; left: 50%; width: 22px; height: 22px;
        transform: translate(-50%, -50%); border-radius: 50%;
        background: var(--surface); border: 4px solid var(--ink);
    }}
    .range-ends {{
        display: flex; justify-content: space-between; margin-top: .65rem;
        font-size: .9rem; color: var(--muted);
    }}
    .range-ends strong {{ color: var(--ink); font-weight: 600; }}

    /* Stat tiles */
    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: 1.6rem; }}
    .stat {{ background: var(--paper); border-radius: 12px; padding: .8rem 1rem; }}
    .stat-label {{ color: var(--muted); font-size: .82rem; margin: 0; }}
    .stat-value {{ font-weight: 600; font-size: 1.15rem; margin: .1rem 0 0 0; }}

    /* Factor bars */
    .factor {{ margin-bottom: .75rem; }}
    .factor-head {{ display: flex; justify-content: space-between; font-size: .92rem; margin-bottom: .3rem; }}
    .factor-track {{ height: 8px; background: var(--paper); border-radius: 999px; overflow: hidden; }}
    .factor-fill {{ height: 100%; background: var(--accent); border-radius: 999px; }}

    /* Empty state */
    .empty {{
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 380px; text-align: center; color: var(--muted); gap: .4rem;
    }}
    .empty .big {{ font-size: 2.4rem; }}
    .empty p {{ margin: 0; max-width: 32ch; }}

    /* Footer */
    .app-footer {{
        margin-top: 2rem; text-align: center; color: var(--muted); font-size: .82rem;
    }}
    .app-footer span {{ margin: 0 .6rem; }}

    @media (prefers-reduced-motion: reduce) {{
        * {{ transition: none !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<h1 class="app-title">What is this house worth?</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-sub">Describe the property and get an instant price estimate '
    "from a machine-learning model.</p>",
    unsafe_allow_html=True,
)

LABELS = {
    "sqft": "Square footage",
    "location": "Location",
    "bathrooms": "Bathrooms",
    "bedrooms": "Bedrooms",
    "year_built": "Year built",
    "condition": "Condition",
}


def money(value: float) -> str:
    return "${:,.0f}".format(value)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
left, right = st.columns([5, 6], gap="large")

# ----- Input form ----------------------------------------------------------
with left:
    with st.container(border=True):
        st.markdown('<p class="section-title">Property details</p>', unsafe_allow_html=True)

        with st.form("predict_form", border=False):
            sqft = st.slider("Square footage (sq ft)", 500, 5000, 1500, 50)

            bedrooms = st.radio("Bedrooms", [1, 2, 3, 4, 5, 6], index=2, horizontal=True)

            bath_col, loc_col = st.columns(2)
            with bath_col:
                bathrooms = st.selectbox("Bathrooms", [1, 1.5, 2, 2.5, 3, 3.5, 4], index=2)
            with loc_col:
                location = st.selectbox(
                    "Location", ["Urban", "Suburban", "Rural", "Waterfront", "Mountain"], index=1
                )

            year_built = st.slider("Year built", 1900, 2025, 2000, 1)

            predict_button = st.form_submit_button("Estimate price", use_container_width=True)

# ----- Prediction call -----------------------------------------------------
if predict_button:
    api_data = {
        "sqft": sqft,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "location": location.lower(),
        "year_built": year_built,
        "condition": "Good",
    }
    api_endpoint = os.getenv("API_URL", "http://model:8000")
    predict_url = f"{api_endpoint.rstrip('/')}/predict"

    with left:
        with st.spinner("Calculating estimate..."):
            started = time.time()
            try:
                response = requests.post(predict_url, json=api_data, timeout=15)
                response.raise_for_status()
                st.session_state.prediction = response.json()
                st.session_state.is_demo = False
            except requests.exceptions.RequestException as e:
                st.error(f"Couldn't reach the prediction service at {predict_url}. {e}")
                st.session_state.prediction = {
                    "predicted_price": 467145,
                    "confidence_interval": [420430.5, 513859.5],
                    "features_importance": {"sqft": 0.43, "location": 0.27, "bathrooms": 0.15},
                    "prediction_time": "0.12 seconds",
                }
                st.session_state.is_demo = True
            st.session_state.round_trip = time.time() - started

# ----- Results -------------------------------------------------------------
with right:
    with st.container(border=True):
        st.markdown('<p class="section-title">Estimate</p>', unsafe_allow_html=True)

        pred = st.session_state.get("prediction")

        if not pred:
            st.markdown(
                """
                <div class="empty">
                    <div class="big">🏡</div>
                    <p><strong>No estimate yet</strong></p>
                    <p>Set the property details and select “Estimate price”.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            if st.session_state.get("is_demo"):
                st.warning("Showing sample data because the API is unavailable.")

            price = pred["predicted_price"]
            low, high = pred.get("confidence_interval", [price * 0.9, price * 1.1])

            st.markdown(
                f"""
                <p class="price-label">Estimated value</p>
                <p class="price-value">{money(price)}</p>

                <div class="range">
                    <div class="range-track"><div class="range-marker"></div></div>
                    <div class="range-ends">
                        <span>Low <strong>{money(low)}</strong></span>
                        <span>High <strong>{money(high)}</strong></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            model_name = pred.get("model", "XGBoost")
            pred_time = pred.get("prediction_time") or f"{st.session_state.get('round_trip', 0):.2f} seconds"
            confidence = pred.get("confidence_score")
            confidence_text = f"{confidence:.0%}" if isinstance(confidence, (int, float)) else "—"

            st.markdown(
                f"""
                <div class="stats">
                    <div class="stat"><p class="stat-label">Model</p><p class="stat-value">{model_name}</p></div>
                    <div class="stat"><p class="stat-label">Response time</p><p class="stat-value">{pred_time}</p></div>
                    <div class="stat"><p class="stat-label">Confidence</p><p class="stat-value">{confidence_text}</p></div>
                    <div class="stat"><p class="stat-label">Price spread</p><p class="stat-value">± {money((high - low) / 2)}</p></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            factors = pred.get("features_importance") or {}
            if factors:
                rows = ""
                for key, weight in sorted(factors.items(), key=lambda kv: kv[1], reverse=True):
                    rows += f"""
                    <div class="factor">
                        <div class="factor-head"><span>{LABELS.get(key, key.title())}</span><span>{weight:.0%}</span></div>
                        <div class="factor-track"><div class="factor-fill" style="width:{weight * 100:.0f}%"></div></div>
                    </div>
                    """
                st.markdown(
                    f'<p class="section-title" style="margin-top:.2rem">What drives this price</p>{rows}',
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
version = os.getenv("APP_VERSION", "1.0.0")
hostname = socket.gethostname()
try:
    ip_address = socket.gethostbyname(hostname)
except socket.gaierror:
    ip_address = "unavailable for now"

st.markdown(
    f"""
    <div class="app-footer">
        <span>Version {version}</span>
        <span>Host {hostname}</span>
        <span>IP {ip_address}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
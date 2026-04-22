import streamlit as st
import numpy as np
import xgboost as xgb

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------
MODEL_PATH = "xgb_model.json"

model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Cyber DDoS Attack Detector", layout="centered")

# ---------------------------------------------------
# DARK CYBERPUNK THEME CSS
# (Same style as your deep learning design)
# ---------------------------------------------------
cyber_css = """
<style>
body {
    background: linear-gradient(135deg, #020202 0%, #0b0b0b 100%) !important;
    font-family: 'Consolas', monospace;
    color: #00eaff;
    overflow-x: hidden;
}

/* Cyber moving grid background */
body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    background: repeating-linear-gradient(
        0deg,
        rgba(0,255,255,0.08) 0px,
        rgba(0,255,255,0.08) 1px,
        transparent 1px,
        transparent 40px
    ),
    repeating-linear-gradient(
        90deg,
        rgba(0,255,255,0.08) 0px,
        rgba(0,255,255,0.08) 1px,
        transparent 1px,
        transparent 40px
    );
    animation: gridMove 18s linear infinite;
}

@keyframes gridMove {
    from { transform: translateY(0); }
    to { transform: translateY(-40px); }
}

/* Title Glow */
.cyber-title {
    text-align: center;
    font-size: 50px;
    font-weight: 900;
    margin-top: 10px;
    color: #00eaff;
    text-shadow: 0 0 25px #00eaff, 0 0 60px #00eaff;
}

/* Description */
.cyber-desc {
    text-align: center;
    color: #8deaff;
    font-size: 20px;
    margin-bottom: 35px;
    letter-spacing: 1px;
}

/* Neon Inputs */
input, select {
    background: rgba(0,0,0,0.8) !important;
    color: #00eaff !important;
    border: 2px solid #00eaff !important;
    border-radius: 12px !important;
    padding: 10px !important;
    box-shadow: 0 0 22px #00eaff;
}

input:focus, select:focus {
    border-color: #00fff9 !important;
    box-shadow: 0 0 30px #00fff9;
    outline: none !important;
}

/* Neon Button */
.stButton>button {
    background: linear-gradient(90deg, #00eaff, #009dff);
    color: #000 !important;
    padding: 12px 22px;
    border-radius: 12px;
    font-weight: 900;
    font-size: 18px;
    border: none;
    box-shadow: 0 0 28px #00eaff;
    transition: 0.3s;
}

.stButton>button:hover {
    box-shadow: 0 0 38px #00eaff;
    transform: scale(1.07);
}

/* Attack Box */
.attack-box {
    background: rgba(255, 0, 50, 0.25);
    padding: 28px 30px;
    border: 3px solid #ff0047;
    border-radius: 20px;
    text-align: center;
    animation: attackPulse 1.2s infinite;
    box-shadow: 0 0 35px #ff0047;
}

.attack-text {
    font-size: 40px;
    color: #ff0047;
    font-weight: 900;
    text-shadow: 0 0 45px #ff0047;
}

@keyframes attackPulse {
    0%,100% { box-shadow: 0 0 20px #ff0047; }
    50% { box-shadow: 0 0 55px #ff0047; }
}

/* Normal Box */
.normal-box {
    background: rgba(0, 255, 120, 0.20);
    padding: 28px 30px;
    border: 3px solid #00ff99;
    border-radius: 20px;
    text-align: center;
    animation: safeGlow 2s infinite alternate;
    box-shadow: 0 0 30px #00ff99;
}

.normal-text {
    font-size: 36px;
    color: #00ff99;
    font-weight: 900;
    text-shadow: 0 0 45px #00ff99;
}

@keyframes safeGlow {
    0% { box-shadow: 0 0 18px #00ff99; }
    100% { box-shadow: 0 0 45px #00ff99; }
}
</style>
"""

st.markdown(cyber_css, unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown("<div class='cyber-title'>DDoS Attack Detector</div>", unsafe_allow_html=True)
st.markdown("<div class='cyber-desc'>Machine-Learning Based Real-Time Traffic Classification</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# INPUT FORM
# ---------------------------------------------------
with st.form("ddos_form"):
    col1, col2 = st.columns(2)

    with col1:
        flow_duration = st.number_input("Flow Duration")
        total_fwd = st.number_input("Total Fwd Packets")
        total_bwd = st.number_input("Total Backward Packets")
        total_len_fwd = st.number_input("Total Length of Fwd Packets")
        fwd_pkt_len_max = st.number_input("Fwd Packet Length Max")

    with col2:
        flow_bytes_s = st.number_input("Flow Bytes/s")
        flow_pkts_s = st.number_input("Flow Packets/s")
        idle_mean = st.number_input("Idle Mean")
        active_mean = st.number_input("Active Mean")
        protocol = st.selectbox("Protocol (1=ICMP, 6=TCP, 17=UDP)", (1, 6, 17))

    submit_btn = st.form_submit_button("🔍 Predict Traffic")

# ---------------------------------------------------
# PREDICTION
# ---------------------------------------------------
if submit_btn:
    features = [
        flow_duration, total_fwd, total_bwd, total_len_fwd,
        fwd_pkt_len_max, flow_bytes_s, flow_pkts_s,
        idle_mean, active_mean, protocol
    ]

    arr = np.array(features).reshape(1, -1)
    pred = model.predict(arr)[0]

    if pred == 1:
        st.markdown("""
        <div class="attack-box">
            <div class="attack-text">⚠ ATTACK DETECTED ⚠</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="normal-box">
            <div class="normal-text">✔ NORMAL TRAFFIC</div>
        </div>
        """, unsafe_allow_html=True)

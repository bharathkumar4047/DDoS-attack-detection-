import streamlit as st
import numpy as np
import xgboost as xgb
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import json

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="DDoS Detector", layout="wide")

st.title("DDoS Attack Detector")

# -------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------
tab1, tab2 = st.tabs(["🧠 Machine Learning", "🤖 Deep Learning"])


# ===================================================================
# TAB 1 → ML INTERFACE (ENHANCED STYLING)
# ===================================================================
with tab1:
    MODEL_PATH = "xgb_model.json"

    model_ml = xgb.XGBClassifier()
    model_ml.load_model(MODEL_PATH)

    # --------------------------------------------------------------
    # CYBERSECURITY BACKGROUND + NEON GLOW UI (MAINLY ML TAB)
    # --------------------------------------------------------------
    cyber_css = """
    <style>

    /* Dark cyber background for the app */
    .stApp {
        background: radial-gradient(circle at center,#001017,#000000 70%) !important;
        color: #00eaff !important;
        font-family: 'Consolas', monospace;
    }

    /* Cyber neon title */
    .cyber-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-top: 10px;
        color: #00eaff;
        text-shadow: 0 0 15px #00eaff, 0 0 30px #0095ff;
    }

    .cyber-desc {
        text-align: center;
        font-size: 18px;
        color: #67e8ff;
        margin-bottom: 30px;
        text-shadow: 0 0 8px #00eaff;
    }

    /* -------- RED ATTACK ALERT -------- */
    .attack-box {
        background: rgba(255, 0, 0, 0.15);
        border: 2px solid #ff0000;
        padding: 18px;
        text-align: center;
        border-radius: 12px;
        margin-top: 20px;
        animation: glow-red 1.5s infinite alternate;
    }
    .attack-text {
        font-size: 32px;
        font-weight: bold;
        color: #ff4d4d;
        text-shadow: 0 0 15px #ff1a1a, 0 0 30px #ff0000;
    }
    @keyframes glow-red {
        from { box-shadow: 0 0 10px #ff1a1a; }
        to   { box-shadow: 0 0 25px #ff0000; }
    }

    /* -------- GREEN NORMAL ALERT -------- */
    .normal-box {
        background: rgba(0, 255, 0, 0.10);
        border: 2px solid #00ff55;
        padding: 18px;
        text-align: center;
        border-radius: 12px;
        margin-top: 20px;
        animation: glow-green 1.5s infinite alternate;
    }
    .normal-text {
        font-size: 32px;
        font-weight: bold;
        color: #3cff76;
        text-shadow: 0 0 15px #00ff55, 0 0 30px #00cc44;
    }
    @keyframes glow-green {
        from { box-shadow: 0 0 10px #00ff55; }
        to   { box-shadow: 0 0 25px #00ff99; }
    }

    /* Input fields neon effect (may vary by Streamlit version) */
    .stNumberInput input {
        background-color: #000000 !important;
        color: #00eaff !important;
        border: 1px solid #00eaff !important;
        border-radius: 6px;
    }
    /* Make feature name labels white */
.stNumberInput label, .stSelectbox label {
    color: #ffffff !important;   /* PURE WHITE */
    font-weight: bold;
    text-shadow: 0 0 5px #ffffff;
}
/* STYLE FOR PREDICT BUTTON */
.stButton button {
    background-color: #00eaff !important;      /* Bright cyan */
    color: black !important;                   /* Text color */
    font-weight: bold;
    border-radius: 10px;
    padding: 12px 25px;
    border: none;
    font-size: 18px;
    cursor: pointer;
    box-shadow: 0 0 15px #00eaff;
    transition: 0.3s ease-in-out;
}

/* Hover effect */
.stButton button:hover {
    background-color: #0088aa !important;
    box-shadow: 0 0 25px #00eaff, 0 0 45px #00eaff;
    transform: scale(1.05);
}


    </style>
    """

    st.markdown(cyber_css, unsafe_allow_html=True)

    st.markdown("<div class='cyber-title'>🛡️ DDoS Attack Detector</div>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-desc'>Machine-Learning Based Real-Time Traffic Classification</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------
    # INPUT FORM
    # --------------------------------------------------------------
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
            protocol = st.selectbox(
                "Protocol (1=ICMP, 6=TCP, 17=UDP)",
                (1, 6, 17)
            )

        submit_btn = st.form_submit_button("🔍 Predict Traffic")

    # --------------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------------
    if submit_btn:
        features = [
            flow_duration, total_fwd, total_bwd, total_len_fwd,
            fwd_pkt_len_max, flow_bytes_s, flow_pkts_s,
            idle_mean, active_mean, protocol
        ]

        arr = np.array(features).reshape(1, -1)
        pred = model_ml.predict(arr)[0]

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


# ===================================================================
# TAB 2 → DL INTERFACE (LOAD CSV FROM SPECIFIED PATH)
# ===================================================================
with tab2:
    st.title("🛡️ Deep Learning DDoS Attack Detector")
    st.write("Dataset is automatically loaded from the given file path.")

    # ------------------------------------------------------
    # LOAD MODEL, SCALER, FEATURE ORDER
    # ------------------------------------------------------
    model_dl = load_model("ddos_model.h5")
    scaler = joblib.load("scaler.pkl")

    with open("feature_order.json") as f:
        feature_order = json.load(f)

    # ------------------------------------------------------
    # LOAD CSV FROM PATH (NO UPLOAD)
    # ------------------------------------------------------
    CSV_PATH = "test_updated_labels.csv"   # <<--- FIXED PATH HERE

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"❌ Cannot load CSV from path: {CSV_PATH}")
        st.error(f"Details: {e}")
        st.stop()

    st.subheader("📄 Loaded Dataset Preview")
    st.dataframe(df.head())

    # Remove label column if present
    if "Label" in df.columns:
        df = df.drop(columns=["Label"])

    # Check missing columns
    missing = [col for col in feature_order if col not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()

    # Match training feature order
    df = df[feature_order]

    # Scale
    X = scaler.transform(df)

    # Predict
    preds = model_dl.predict(X).flatten()

    df_result = pd.DataFrame({
        "Prediction": ["ATTACK" if p > 0.5 else "NORMAL" for p in preds],
        "Probability": preds
    })

    st.subheader("🔮 Prediction Results")
    st.dataframe(df_result)

    attack_count = sum(df_result["Prediction"] == "ATTACK")
    normal_count = sum(df_result["Prediction"] == "NORMAL")

    st.success(f"🛑 Attacks detected: {attack_count}")
    st.info(f"✅ Normal traffic: {normal_count}")

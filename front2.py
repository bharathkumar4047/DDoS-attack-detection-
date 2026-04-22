import streamlit as st

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="DDoS Detector", layout="wide")

st.title("🔥DDoS Attack Detector")


# -------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------
tab1, tab2 = st.tabs(["🧠 ML Model", "🤖 DL Model (Load CSV from Path)"])



# ===================================================================
# TAB 1 → ML INTERFACE (YOUR EXACT ORIGINAL CODE)
# ===================================================================

with tab1:
    import numpy as np
    import xgboost as xgb

    MODEL_PATH = "xgb_model.json"

    model_ml = xgb.XGBClassifier()
    model_ml.load_model(MODEL_PATH)

    cyber_css = """
    <style>
    body {
        background: linear-gradient(135deg, #020202 0%, #0b0b0b 100%) !important;
        font-family: 'Consolas', monospace;
        color: #00eaff;
        overflow-x: hidden;
    }
    </style>
    """
    st.markdown(cyber_css, unsafe_allow_html=True)

    st.markdown("<div class='cyber-title'>DDoS Attack Detector</div>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-desc'>Machine-Learning Based Real-Time Traffic Classification</div>", unsafe_allow_html=True)

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
# TAB 2 → FIXED DL INTERFACE (LOAD CSV FROM SPECIFIED PATH)
# ===================================================================

with tab2:
    import pandas as pd
    import numpy as np
    from tensorflow.keras.models import load_model
    import joblib
    import json

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
    except:
        st.error(f"❌ Cannot load CSV from path: {CSV_PATH}")
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

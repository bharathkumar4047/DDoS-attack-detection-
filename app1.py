import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="DDoS Attack Detector", layout="centered")

# ------------------------------
# CYBERSEC DARK THEME + ANIMATION CSS
# ------------------------------
cyber_css = """
<style>

body {
    background-color: #050505;
}

[data-testid="stAppViewContainer"] {
    background-color: #000000;
    color: #39ff14;
    font-family: 'Roboto', sans-serif;
}

/* MATRIX BACKGROUND ANIMATION */
@keyframes matrixRain {
  0% { background-position: 0 0; }
  100% { background-position: 0 1000px; }
}

[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  top:0;
  left:0;
  width:100%;
  height:100%;
  z-index:-1;
  background-image: url('https://i.imgur.com/7fYVdUO.png'); /* Green matrix style code */
  opacity:0.10;
  animation: matrixRain 15s linear infinite;
}

/* Neon Title */
h1, h2, h3 {
    color: #39ff14 !important;
    text-shadow: 0 0 10px #39ff14;
}

/* Neon boxes */
.block-container {
    padding: 2rem;
    border-radius: 12px;
}

/* Neon Button */
.stButton>button {
    background-color: black;
    color: #39ff14;
    border: 1px solid #39ff14;
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;

    box-shadow: 0px 0px 10px #39ff14;
    transition: 0.3s ease;
}

.stButton>button:hover {
    background-color: #39ff14;
    color: black;
    box-shadow: 0px 0px 20px #39ff14;
    transform: scale(1.05);
}

/* Data table text */
.dataframe {
    color: #00ffcc !important;
}

/* Progress bar neon */
.stProgress > div > div > div {
    background-color: #39ff14 !important;
}
</style>
"""
st.markdown(cyber_css, unsafe_allow_html=True)

# ------------------------------
# LOAD MODEL & CSV
# ------------------------------
MODEL_PATH = "ddos_model.h5"
CSV_PATH = "test_updated_labels.csv"

@st.cache_resource
def load_ddos_model():
    return load_model(MODEL_PATH)

@st.cache_data
def load_csv():
    return pd.read_csv(CSV_PATH)

model = load_ddos_model()
df = load_csv()

# ------------------------------
# UI TITLE
# ------------------------------
st.title("🛡️ DDoS Attack Detector")
st.markdown("<h3>Analyze any row from your CSV .</h3>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------
# ROW NUMBER INPUT
# ------------------------------
st.subheader("🔢 Select Row to Test")

max_row = len(df) - 1
row_num = st.number_input(
    "Enter a row number:",
    min_value=0,
    max_value=max_row,
    value=0,
    step=1
)

st.info(f"Total rows available: **{len(df)}**")

# ------------------------------
# BUTTON & PREDICTION FLOW
# ------------------------------
if st.button("🔍 Predict Row "):

    st.markdown("---")

    temp_df = df.copy()

    # Remove label if present
    label_col = "Label"
    if label_col in temp_df.columns:
        temp_df = temp_df.drop(columns=[label_col])

    # Extract row
    row = temp_df.iloc[row_num:row_num+1]

    st.subheader("📄 Selected Row Preview")
    st.dataframe(row, use_container_width=True)

    # Use only numeric features
    features = row.select_dtypes(include=['int64', 'float64'])
    X = features.to_numpy()

    # Prediction
    pred = model.predict(X)[0][0]
    label = "🛑 ATTACK" if pred > 0.5 else "✅ NORMAL"

    st.subheader("🔮 Prediction Result")

    # Cyber Glow Prediction Box
    # Cyber Glow Prediction Box
    if pred > 0.5:
        st.markdown(
        f"""
        <div style="
            background-color:#1a000f;
            padding:20px;
            border-radius:12px;
            border:2px solid #ff004f;
            box-shadow:0 0 15px #ff004f;
            text-align:center;">
            <h2 style='color:#ff004f; text-shadow:0 0 12px #ff004f;'>
                🛑 ATTACK
            </h2>
            <h3 style="color:white;">Probability: {pred:.4f}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    else:
        st.markdown(
        f"""
        <div style="
            background-color:#001a00;
            padding:20px;
            border-radius:12px;
            border:2px solid #39ff14;
            box-shadow:0 0 15px #39ff14;
            text-align:center;">
            <h2 style='color:#39ff14; text-shadow:0 0 12px #39ff14;'>
                ✅ NORMAL
            </h2>
            <h3 style="color:white;">Probability: {pred:.4f}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

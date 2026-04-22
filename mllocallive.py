import time
import threading
import numpy as np
from scapy.all import sniff, IP
import joblib
import pandas as pd

import xgboost as xgb
import joblib

model = xgb.XGBClassifier()
model.load_model("xgb_model.json")

scaler = joblib.load("scalerr.pkl")

print("[+] XGBoost model (JSON) and scaler loaded")

# =========================
# GLOBALS
# =========================
packet_buffer = []
lock = threading.Lock()
WINDOW_SECONDS = 2
DEBUG = True   # set False after testing

# =========================
# FEATURE ORDER (CRITICAL)
# =========================
FEATURE_ORDER = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Fwd Packet Length Max",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Idle Mean",
    "Active Mean",
    "Protocol"
]



# =========================
# PACKET HANDLER
# =========================
def packet_handler(pkt):
    if IP in pkt:
        with lock:
            packet_buffer.append((time.time(), pkt))

# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(packets):
    times = [t for t, _ in packets]
    flow_duration = max(times) - min(times)

    fwd_packets = len(packets)
    total_fwd_length = sum(len(pkt) for _, pkt in packets)
    max_fwd_length = max(len(pkt) for _, pkt in packets)

    # Approximate backward packets (important for model stability)
    bwd_packets = max(1, int(0.2 * fwd_packets))

    # Rates
    flow_packets_per_sec = fwd_packets / max(flow_duration, 1e-6)
    flow_bytes_per_sec = total_fwd_length / max(flow_duration, 1e-6)

    # Inter-arrival times
    iats = np.diff(sorted(times))
    idle_times = [iat for iat in iats if iat > 0.1]
    active_times = [iat for iat in iats if iat <= 0.1]

    idle_mean = np.mean(idle_times) if idle_times else 0
    active_mean = np.mean(active_times) if active_times else 0

    protocol = packets[0][1][IP].proto

    features = {
    "Flow Duration": flow_duration,
    "Total Fwd Packets": fwd_packets,
    "Total Backward Packets": bwd_packets,
    "Total Length of Fwd Packets": total_fwd_length,
    "Fwd Packet Length Max": max_fwd_length,
    "Flow Bytes/s": flow_bytes_per_sec,
    "Flow Packets/s": flow_packets_per_sec,
    "Idle Mean": idle_mean,
    "Active Mean": active_mean,
    "Protocol": protocol
}



    return features

# =========================
# PREDICTION THREAD
# =========================
def predictor():
    print("[*] Prediction thread running...")
    while True:
        time.sleep(WINDOW_SECONDS)

        with lock:
            if len(packet_buffer) < 5:
                packet_buffer.clear()
                continue

            packets = packet_buffer.copy()
            packet_buffer.clear()

        features = extract_features(packets)

        X_df = pd.DataFrame([features], columns=FEATURE_ORDER)
        X_scaled = scaler.transform(X_df)


        proba = model.predict_proba(X_scaled)[0][1]
        label = "ATTACK" if proba > 0.6 else "NORMAL"

        print(f"[{label}] confidence={proba:.2f}")

        if DEBUG:
            print({
    "pps": round(features["Flow Packets/s"], 2),
    "bps": round(features["Flow Bytes/s"], 2),
    "fwd": features["Total Fwd Packets"],
    "idle": round(features["Idle Mean"], 4),
    "active": round(features["Active Mean"], 4),
    "proto": features["Protocol"]
})


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("=== AVAILABLE NETWORK INTERFACES ===")
    from scapy.all import get_if_list

    interfaces = get_if_list()
    for i, iface in enumerate(interfaces):
        print(f"{i}: {iface}")

    idx = int(input("Select interface index: "))
    iface = interfaces[idx]

    print(f"[+] Sniffing on interface: {iface}")
    print("[!] IMPORTANT: Run as ADMINISTRATOR on Windows")

    t = threading.Thread(target=predictor, daemon=True)
    t.start()

    sniff(iface=iface, prn=packet_handler, store=False)

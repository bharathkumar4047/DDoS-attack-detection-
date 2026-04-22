import random
from scapy.layers.inet import IP, TCP
import threading
import time
import json
import joblib
import numpy as np
from scapy.all import *
from tensorflow.keras.models import load_model
import warnings

warnings.filterwarnings("ignore")

# -------------------------------------------------------------
# LOAD MODEL, SCALER, FEATURE ORDER
# -------------------------------------------------------------
scaler = joblib.load("scaler.pkl")
print("[OK] Scaler loaded")

model = load_model("ddos_model.h5")
print("[OK] DNN model loaded")

with open("feature_order.json", "r") as f:
    FEATURE_ORDER = json.load(f)

NUM_FEATURES = len(FEATURE_ORDER)
print(f"[OK] Feature count: {NUM_FEATURES}")

# -------------------------------------------------------------
# INTERFACE
# -------------------------------------------------------------
print("\n=== AVAILABLE NETWORK INTERFACES ===")
show_interfaces()
print("====================================\n")

INTERFACE = "Wi-Fi"   # adjust if needed

# -------------------------------------------------------------
# GLOBAL PACKET BUFFER
# -------------------------------------------------------------
packet_buffer = []

# -------------------------------------------------------------
# FEATURE EXTRACTION (PARTIAL REAL + SAFE ZERO FILL)
# -------------------------------------------------------------
def extract_features_from_flow(packets):

    if len(packets) == 0:
        return None

    features = dict.fromkeys(FEATURE_ORDER, 0)

    # ---------------- BASIC FLOW FEATURES ----------------
    start_time = packets[0].time
    end_time = packets[-1].time
    flow_duration = (end_time - start_time) * 1000  # ms

    pkt_lengths = [len(pkt) for pkt in packets]
    total_len = sum(pkt_lengths)

    duration_sec = max(flow_duration / 1000, 0.0001)

    # ---------------- POPULATE KNOWN FEATURES ----------------
    features["Flow Duration"] = flow_duration
    features["Total Fwd Packets"] = len(packets)
    features["Total Length of Fwd Packets"] = total_len
    features["Fwd Packet Length Max"] = max(pkt_lengths)
    features["Flow Bytes/s"] = total_len / duration_sec
    features["Flow Packets/s"] = len(packets) / duration_sec

    # Idle / Active
    gaps = [
        (packets[i].time - packets[i - 1].time) * 1000
        for i in range(1, len(packets))
    ]

    idle = [g for g in gaps if g > 100]
    active = [g for g in gaps if g <= 100]

    features["Idle Mean"] = np.mean(idle) if idle else 0
    features["Active Mean"] = np.mean(active) if active else 0

    # Protocol
    if hasattr(packets[0], "proto"):
        features["Protocol"] = packets[0].proto

    # ---------------- FINAL VECTOR (70 FEATURES) ----------------
    return [features[f] for f in FEATURE_ORDER]

# -------------------------------------------------------------
# PREDICTION THREAD
# -------------------------------------------------------------
def prediction_worker():
    global packet_buffer

    print("DNN live prediction thread started...")

    while True:
        time.sleep(1)

        if len(packet_buffer) < 10:
            continue

        packets = packet_buffer.copy()
        packet_buffer = []

        feature_vector = extract_features_from_flow(packets)
        if feature_vector is None:
            continue

        try:
            X = scaler.transform([feature_vector])
            prob = model.predict(X, verbose=0)[0][0]

            label = "🚨 DDoS ATTACK" if prob >= 0.5 else "✅ NORMAL"
            print(f"Prediction : {label} ")

        except Exception as e:
            print("Prediction error:", e)

# -------------------------------------------------------------
# PACKET HANDLER
# -------------------------------------------------------------
def packet_handler(pkt):
    global packet_buffer
    packet_buffer.append(pkt)

def mock_ddos_attack(rate=300, duration=10):
    """
    SAFE mock attack – feeds synthetic packets directly
    into the live pipeline.
    """
    print("\n[MOCK] Simulated DDoS attack started")

    end_time = time.time() + duration

    while time.time() < end_time:
        pkt = IP(
            src=f"10.0.0.{random.randint(1,254)}",
            dst="192.168.1.100"
        ) / TCP(
            sport=random.randint(1024, 65535),
            dport=80,
            flags="S"
        )

        packet_handler(pkt)
        time.sleep(1 / rate)

    print("[MOCK] Simulated DDoS attack ended\n")


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
if __name__ == "__main__":

    print("Starting LIVE DNN DDoS Detector (70-feature mode)")
    print("Run as ADMINISTRATOR")

    threading.Thread(
        target=prediction_worker,
        daemon=True
    ).start()
    

    conf.use_pcap = True

    print(f"\nSniffing on interface: {INTERFACE}\n")
    sniff(iface=INTERFACE, prn=packet_handler, store=False)

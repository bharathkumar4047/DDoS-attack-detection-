import time
import threading
import json
import joblib
import numpy as np
import pandas as pd
from scapy.all import sniff, IP, TCP
from tensorflow.keras.models import load_model

# =========================================
# LOAD MODEL, SCALER, FEATURE ORDER
# =========================================
model = load_model("ddos_model.h5")
scaler = joblib.load("scaler.pkl")

with open("feature_order.json", "r") as f:
    FEATURE_ORDER = json.load(f)

assert len(FEATURE_ORDER) == 70

print("[+] DNN model loaded")
print("[+] Scaler loaded (70 features)")
print("[+] Feature order verified")

# =========================================
# SETTINGS
# =========================================
WINDOW_SECONDS = 2
ATTACK_THRESHOLD = 0.30  # LOW prob => ATTACK

packet_buffer = []
lock = threading.Lock()

# =========================================
# PACKET HANDLER
# =========================================
def packet_handler(pkt):
    if IP in pkt:
        with lock:
            packet_buffer.append((time.time(), pkt))

# =========================================
# FEATURE EXTRACTION (LIVE-COMPATIBLE)
# =========================================
def extract_features(packets):
    times = np.array([t for t, _ in packets])
    pkts = [p for _, p in packets]

    duration = max(times[-1] - times[0], 1e-6)
    lengths = np.array([len(p) for p in pkts])
    iats = np.diff(times) if len(times) > 1 else np.array([0.0])

    fwd = len(pkts)
    bwd = max(1, int(0.15 * fwd))

    proto = pkts[0][IP].proto
    sport = pkts[0][IP].sport if hasattr(pkts[0][IP], "sport") else 0
    dport = pkts[0][IP].dport if hasattr(pkts[0][IP], "dport") else 0

    syn = ack = rst = urg = psh = 0
    for p in pkts:
        if TCP in p:
            flags = p[TCP].flags
            syn += int(flags & 0x02 != 0)
            ack += int(flags & 0x10 != 0)
            rst += int(flags & 0x04 != 0)
            urg += int(flags & 0x20 != 0)
            psh += int(flags & 0x08 != 0)

    feats = {
        "Source Port": sport,
        "Destination Port": dport,
        "Protocol": proto,
        "Timestamp": times[-1],

        "Flow Duration": duration,
        "Total Fwd Packets": fwd,
        "Total Backward Packets": bwd,
        "Total Length of Fwd Packets": lengths.sum(),
        "Total Length of Bwd Packets": int(lengths.sum() * 0.1),

        "Fwd Packet Length Max": lengths.max(),
        "Fwd Packet Length Min": lengths.min(),
        "Fwd Packet Length Mean": lengths.mean(),
        "Fwd Packet Length Std": lengths.std(),

        "Bwd Packet Length Max": lengths.max(),
        "Bwd Packet Length Min": lengths.min(),
        "Bwd Packet Length Mean": lengths.mean(),
        "Bwd Packet Length Std": lengths.std(),

        "Flow Bytes/s": lengths.sum() / duration,
        "Flow Packets/s": fwd / duration,

        "Flow IAT Mean": iats.mean(),
        "Flow IAT Std": iats.std(),
        "Flow IAT Max": iats.max(),
        "Flow IAT Min": iats.min(),

        "Fwd IAT Total": iats.sum(),
        "Fwd IAT Mean": iats.mean(),
        "Fwd IAT Std": iats.std(),
        "Fwd IAT Max": iats.max(),
        "Fwd IAT Min": iats.min(),

        "Bwd IAT Total": iats.sum() * 0.1,
        "Bwd IAT Mean": iats.mean(),
        "Bwd IAT Std": iats.std(),
        "Bwd IAT Max": iats.max(),
        "Bwd IAT Min": iats.min(),

        "Fwd PSH Flags": psh,
        "SYN Flag Count": syn,
        "ACK Flag Count": ack,
        "RST Flag Count": rst,
        "URG Flag Count": urg,
        "CWE Flag Count": 0,

        "Fwd Header Length": 20,
        "Bwd Header Length": 20,
        "Fwd Header Length.1": 20,

        "Fwd Packets/s": fwd / duration,
        "Bwd Packets/s": bwd / duration,

        "Min Packet Length": lengths.min(),
        "Max Packet Length": lengths.max(),
        "Packet Length Mean": lengths.mean(),
        "Packet Length Std": lengths.std(),
        "Packet Length Variance": lengths.var(),

        "Down/Up Ratio": bwd / max(fwd, 1),
        "Average Packet Size": lengths.mean(),
        "Avg Fwd Segment Size": lengths.mean(),
        "Avg Bwd Segment Size": lengths.mean(),

        "Subflow Fwd Packets": fwd,
        "Subflow Fwd Bytes": lengths.sum(),
        "Subflow Bwd Packets": bwd,
        "Subflow Bwd Bytes": int(lengths.sum() * 0.1),

        "Init_Win_bytes_forward": 1024,
        "Init_Win_bytes_backward": 1024,
        "act_data_pkt_fwd": fwd,
        "min_seg_size_forward": lengths.min(),

        "Active Mean": duration * 0.7,
        "Active Std": duration * 0.1,
        "Active Max": duration,
        "Active Min": duration * 0.5,

        "Idle Mean": duration * 0.3,
        "Idle Std": duration * 0.1,
        "Idle Max": duration * 0.4,
        "Idle Min": duration * 0.1,

        "Inbound": 1
    }

    return feats

# =========================================
# PREDICTION THREAD (FINAL LOGIC)
# =========================================
def predictor():
    print("[*] DNN live prediction started")

    while True:
        time.sleep(WINDOW_SECONDS)

        with lock:
            if not packet_buffer:
                continue
            packets = packet_buffer.copy()
            packet_buffer.clear()

        feats = extract_features(packets)
        row = {k: float(feats.get(k, 0.0)) for k in FEATURE_ORDER}

        X = pd.DataFrame([row])
        X_scaled = scaler.transform(X)

        prob = model.predict(X_scaled, verbose=0)[0][0]

        # 🔑 CORRECT DECISION
        label = "ATTACK" if prob <= ATTACK_THRESHOLD else "NORMAL"

        print(f"[{label}] P(NORMAL)={prob:.3f} | PPS={feats['Flow Packets/s']:.1f}")

# =========================================
# MAIN
# =========================================
if __name__ == "__main__":
    print("[!] Run as Administrator")
    threading.Thread(target=predictor, daemon=True).start()

    sniff(
        iface="\\Device\\NPF_Loopback",
        prn=packet_handler,
        store=False
    )

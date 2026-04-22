import threading
import time
import joblib
import xgboost as xgb
from scapy.all import *
import warnings

warnings.filterwarnings("ignore")

# -------------------------------------------------------------
# LOAD SCALER & MODEL
# -------------------------------------------------------------
try:
    scaler = joblib.load("scalerr.pkl")
    print("[OK] Scaler loaded")
except Exception as e:
    print("[ERROR] Failed to load scaler:", e)

try:
    model = xgb.XGBClassifier()
    model.load_model("xgb_model.json")
    print("[OK] XGBoost model loaded")
except Exception as e:
    print("[ERROR] Failed to load ML model:", e)

# -------------------------------------------------------------
# LIST INTERFACES
# -------------------------------------------------------------
print("\n=== AVAILABLE NETWORK INTERFACES ===")
show_interfaces()
print("====================================\n")

INTERFACE = "Wi-Fi"   # CHANGE if needed

# -------------------------------------------------------------
# GLOBAL FLOW BUFFER
# -------------------------------------------------------------
packet_buffer = []

# -------------------------------------------------------------
# FEATURE EXTRACTION (REAL LOGIC)
# -------------------------------------------------------------
def extract_features_from_flow(packets):

    if len(packets) == 0:
        return None

    # Time
    start_time = packets[0].time
    end_time = packets[-1].time
    flow_duration = (end_time - start_time) * 1000  # ms

    # Packet counts
    fwd_packets = len(packets)
    bwd_packets = 0  # simplified (can improve later)

    # Packet sizes
    total_fwd_length = sum(len(pkt) for pkt in packets)
    max_fwd_length = max(len(pkt) for pkt in packets)

    # Rates
    duration_sec = (flow_duration / 1000) + 0.0001
    flow_bytes_per_sec = total_fwd_length / duration_sec
    flow_packets_per_sec = fwd_packets / duration_sec

    # Idle & Active Times
    idle_times = []
    active_times = []

    for i in range(1, len(packets)):
        gap = (packets[i].time - packets[i - 1].time) * 1000
        if gap > 100:
            idle_times.append(gap)
        else:
            active_times.append(gap)

    idle_mean = sum(idle_times) / len(idle_times) if idle_times else 0
    active_mean = sum(active_times) / len(active_times) if active_times else 0

    # Protocol
    protocol = packets[0].proto if hasattr(packets[0], "proto") else 0

    # IMPORTANT: Feature order MUST match training
    return [
        flow_duration,
        fwd_packets,
        bwd_packets,
        total_fwd_length,
        max_fwd_length,
        flow_bytes_per_sec,
        flow_packets_per_sec,
        idle_mean,
        active_mean,
        protocol
    ]

# -------------------------------------------------------------
# PREDICTION THREAD
# -------------------------------------------------------------
def prediction_worker():
    global packet_buffer

    print("Prediction thread running...")

    while True:
        time.sleep(1)

        if len(packet_buffer) < 5:
            continue

        packets = packet_buffer.copy()
        packet_buffer = []

        features = extract_features_from_flow(packets)
        if features is None:
            continue

        try:
            X_scaled = scaler.transform([features])
            pred = model.predict(X_scaled)

            label = "🚨 DDoS ATTACK" if pred[0] == 1 else "✅ NORMAL"
            print("Prediction:", label)

        except Exception as e:
            print("Prediction error:", e)

# -------------------------------------------------------------
# PACKET HANDLER
# -------------------------------------------------------------
def packet_handler(pkt):
    global packet_buffer
    packet_buffer.append(pkt)

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
if __name__ == "__main__":
    print("Starting live flow predictor...")
    print("IMPORTANT: Run as ADMINISTRATOR on Windows")

    threading.Thread(target=prediction_worker, daemon=True).start()

    conf.use_pcap = True

    print(f"\nSniffing on interface: {INTERFACE}\n")
    sniff(iface=INTERFACE, prn=packet_handler, store=False)

import xgboost as xgb
import numpy as np

# --------------------------------------------
# LOAD XGBOOST MODEL
# --------------------------------------------
MODEL_PATH = "xgb_model.json"   # Change to your file name (.json/.pkl)
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

# --------------------------------------------
# THE 10 FEATURES LIST
# --------------------------------------------
selected_features = [
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

# --------------------------------------------
# TAKE USER INPUT FOR ALL 10 FEATURES
# --------------------------------------------
inputs = []

print("\nEnter values for the 10 features:\n")

for feature in selected_features:
    value = float(input(f"Enter {feature}: "))
    inputs.append(value)

# Convert to array for prediction
X = np.array(inputs).reshape(1, -1)

# --------------------------------------------
# PREDICT
# --------------------------------------------
prediction = model.predict(X)[0]

# Convert label (modify if your encoding is different)
label = "ATTACK" if prediction == 1 else "NORMAL"

print("\n----------------------------------")
print("Prediction Result:", label)
print("----------------------------------\n")

import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# Your selected 10 features
TEN_FEATURES = [
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

# Load your training dataset
df = pd.read_csv("combined_dataset.csv")   # change if needed

# Keep only your 10 features
df = df[TEN_FEATURES]

# Train the scaler
scalerr = StandardScaler()
scalerr.fit(df)

# Save the new scaler
joblib.dump(scalerr, "scalerr.pkl")
print("New scaler.pkl saved successfully. Now your live predictor will work.")

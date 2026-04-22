# import pandas as pd
# import numpy as np
# import json
# import joblib
# import matplotlib.pyplot as plt

# from sklearn.metrics import (
#     accuracy_score,
#     precision_score,
#     recall_score,
#     f1_score,
#     roc_auc_score,
#     confusion_matrix,
#     RocCurveDisplay
# )
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler

# from tensorflow.keras.models import load_model

# # ------------------------------------------------------
# # LOAD DATA
# # ------------------------------------------------------
# df = pd.read_csv("updated_labels.csv")
# label_col = "Label"

# X = df.drop(columns=[label_col])
# y = df[label_col]

# # ------------------------------------------------------
# # LOAD FEATURE ORDER
# # ------------------------------------------------------
# with open("feature_order.json", "r") as f:
#     FEATURE_ORDER = json.load(f)

# X = X[FEATURE_ORDER]

# # ------------------------------------------------------
# # TRAIN-TEST SPLIT (SAME FOR BOTH MODELS)
# # ------------------------------------------------------
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42, stratify=y
# )

# # ------------------------------------------------------
# # LOAD SCALER
# # ------------------------------------------------------
# scaler = joblib.load("scaler.pkl")
# X_test_scaled = scaler.transform(X_test)

# # ------------------------------------------------------
# # LOAD MODELS
# # ------------------------------------------------------
# ml_model = joblib.load("ml_model.pkl")          # ML model
# dl_model = load_model("ddos_model.h5")          # DNN model

# # ------------------------------------------------------
# # ML MODEL PREDICTIONS
# # ------------------------------------------------------
# ml_pred = ml_model.predict(X_test)
# ml_prob = ml_model.predict_proba(X_test)[:, 1]

# # ------------------------------------------------------
# # DL MODEL PREDICTIONS
# # ------------------------------------------------------
# dl_prob = dl_model.predict(X_test_scaled).ravel()
# dl_pred = (dl_prob >= 0.5).astype(int)

# # ------------------------------------------------------
# # METRICS FUNCTION
# # ------------------------------------------------------
# def evaluate_model(y_true, y_pred, y_prob):
#     return {
#         "Accuracy": accuracy_score(y_true, y_pred),
#         "Precision": precision_score(y_true, y_pred),
#         "Recall": recall_score(y_true, y_pred),
#         "F1-Score": f1_score(y_true, y_pred),
#         "ROC-AUC": roc_auc_score(y_true, y_prob)
#     }

# ml_metrics = evaluate_model(y_test, ml_pred, ml_prob)
# dl_metrics = evaluate_model(y_test, dl_pred, dl_prob)

# # ------------------------------------------------------
# # DISPLAY METRICS
# # ------------------------------------------------------
# results = pd.DataFrame([ml_metrics, dl_metrics], index=["ML Model", "DNN Model"])
# print("\nModel Comparison:\n")
# print(results)

# # ------------------------------------------------------
# # BAR GRAPH COMPARISON
# # ------------------------------------------------------
# results.plot(kind="bar", figsize=(10, 5))
# plt.title("ML vs DNN Performance Comparison")
# plt.ylabel("Score")
# plt.xticks(rotation=0)
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# # ------------------------------------------------------
# # ROC CURVES
# # ------------------------------------------------------
# plt.figure(figsize=(8, 6))
# RocCurveDisplay.from_predictions(y_test, ml_prob, name="ML Model")
# RocCurveDisplay.from_predictions(y_test, dl_prob, name="DNN Model")
# plt.title("ROC Curve Comparison")
# plt.grid(True)
# plt.show()

# # ------------------------------------------------------
# # CONFUSION MATRICES
# # ------------------------------------------------------
# ml_cm = confusion_matrix(y_test, ml_pred)
# dl_cm = confusion_matrix(y_test, dl_pred)

# print("\nML Confusion Matrix:\n", ml_cm)
# print("\nDNN Confusion Matrix:\n", dl_cm)

import pandas as pd
import numpy as np
import json
import joblib
import matplotlib.pyplot as plt
import xgboost as xgb

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, RocCurveDisplay
)
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = pd.read_csv("updated_labels.csv")
LABEL = "Label"

# -------------------------------------------------
# XGBOOST FEATURES (CRITICAL)
# -------------------------------------------------
XGB_FEATURES = [
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

# -------------------------------------------------
# DNN FEATURE ORDER
# -------------------------------------------------
with open("feature_order.json", "r") as f:
    DNN_FEATURES = json.load(f)

# -------------------------------------------------
# SPLIT DATA
# -------------------------------------------------
X = df.drop(columns=[LABEL])
y = df[LABEL]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------------------------------
# PREPARE XGBOOST DATA (ONLY 10 FEATURES)
# -------------------------------------------------
X_test_xgb = X_test[XGB_FEATURES]

# -------------------------------------------------
# PREPARE DNN DATA (FULL FEATURES + SCALER)
# -------------------------------------------------
scaler = joblib.load("scaler.pkl")
X_test_dnn = scaler.transform(X_test[DNN_FEATURES])

# -------------------------------------------------
# LOAD MODELS
# -------------------------------------------------
xgb_model = xgb.XGBClassifier()
xgb_model.load_model("xgb_model.json")

dnn_model = load_model("ddos_model.h5")

# -------------------------------------------------
# XGBOOST PREDICTION
# -------------------------------------------------
xgb_pred = xgb_model.predict(X_test_xgb)
xgb_prob = xgb_model.predict_proba(X_test_xgb)[:, 1]

# -------------------------------------------------
# DNN PREDICTION
# -------------------------------------------------
dnn_prob = dnn_model.predict(X_test_dnn).ravel()
dnn_pred = (dnn_prob >= 0.5).astype(int)

# -------------------------------------------------
# METRICS
# -------------------------------------------------
def metrics(y, y_hat, y_prob):
    return {
        "Accuracy": accuracy_score(y, y_hat),
        "Precision": precision_score(y, y_hat),
        "Recall": recall_score(y, y_hat),
        "F1": f1_score(y, y_hat),
        "ROC-AUC": roc_auc_score(y, y_prob)
    }

xgb_metrics = metrics(y_test, xgb_pred, xgb_prob)
dnn_metrics = metrics(y_test, dnn_pred, dnn_prob)

results = pd.DataFrame(
    [xgb_metrics, dnn_metrics],
    index=["XGBoost", "DNN"]
)

print("\nMODEL COMPARISON\n")
print(results)

# -------------------------------------------------
# BAR GRAPH
# -------------------------------------------------
results.plot(kind="bar", figsize=(10, 5))
plt.title("XGBoost vs DNN Performance Comparison")
plt.ylabel("Score")
plt.xticks(rotation=0)
plt.grid(True)
plt.tight_layout()
plt.show()

# -------------------------------------------------
# ROC CURVE
# -------------------------------------------------
plt.figure(figsize=(8, 6))
RocCurveDisplay.from_predictions(y_test, xgb_prob, name="XGBoost")
RocCurveDisplay.from_predictions(y_test, dnn_prob, name="DNN")
plt.title("ROC Curve Comparison")
plt.grid(True)
plt.show()

# -------------------------------------------------
# CONFUSION MATRICES
# -------------------------------------------------
print("\nXGBoost Confusion Matrix:\n", confusion_matrix(y_test, xgb_pred))
print("\nDNN Confusion Matrix:\n", confusion_matrix(y_test, dnn_pred))


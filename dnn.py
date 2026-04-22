import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import json

# ------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------
df = pd.read_csv("updated_labels.csv")     # <-- your training dataset

label_col = "Label"
X = df.drop(columns=[label_col])
y = df[label_col]

# ------------------------------------------------------
# SAVE COLUMN ORDER
# ------------------------------------------------------
feature_list = X.columns.tolist()

with open("feature_order.json", "w") as f:
    json.dump(feature_list, f)

# ------------------------------------------------------
# TRAIN-TEST SPLIT
# ------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------------------------------------------------------
# SCALING
# ------------------------------------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

joblib.dump(scaler, "scaler.pkl")
print("Scaler saved as scaler.pkl")

# ------------------------------------------------------
# FIX CLASS IMBALANCE
# ------------------------------------------------------
class_weights = compute_class_weight(
    "balanced",
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))
print("Class Weights:", class_weights)

# ------------------------------------------------------
# BUILD MODEL
# ------------------------------------------------------
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# ------------------------------------------------------
# TRAIN MODEL
# ------------------------------------------------------
es = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=50,
    batch_size=64,
    class_weight=class_weights,
    callbacks=[es],
    verbose=1
)

# ------------------------------------------------------
# SAVE MODEL
# ------------------------------------------------------
model.save("ddos_model.h5")
print("Model saved as ddos_model.h5")

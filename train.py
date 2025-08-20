import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

print("🔹 Loading dataset...")

# Load CSV (no headers)
df = pd.read_csv("data/KDDTrain+.csv", header=None)

# Features: columns 0 to 40
X = df.iloc[:, 0:41].copy()  # make a copy to avoid SettingWithCopyWarning

# Label: column 41
y = df.iloc[:, 41].apply(lambda x: 0 if x == "normal" else 1)

# Encode categorical columns: protocol_type (1), service (2), flag (3)
categorical_cols = [1, 2, 3]
encoders = {}  # save encoders in case you need for monitoring
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))  # ensure string type
    encoders[col] = le
    joblib.dump(le, f"encoder_col{col}.pkl")

# Convert all to numeric float
X = X.astype(float)

print("🔹 Training model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=50)
model.fit(X_train, y_train)

acc = model.score(X_test, y_test)
print(f"✅ Model trained with accuracy: {acc:.2f}")

# Save trained model
joblib.dump(model, "model.pkl")
print("💾 Model saved as model.pkl")

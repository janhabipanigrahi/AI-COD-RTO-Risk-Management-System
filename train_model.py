
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

# 1. Load dataset
df = pd.read_csv("orders_sample.csv")

# 2. Normalize status
df["final_status"] = (
    df["final_status"].astype(str).str.strip().str.upper()
)

# Keep completed orders only
df = df[df["final_status"].isin(["DELIVERED", "RTO"])].copy()

# 3. Create target variable
df["is_rto"] = (df["final_status"] == "RTO").astype(int)

# 4. Feature engineering
df["address_length"] = df["address"].fillna("").astype(str).str.len()

df["address_has_number"] = (
    df["address"].fillna("").astype(str).str.contains(r"\d").astype(int)
)

df["name_length"] = (
    df["customer_name"].fillna("").astype(str).str.len()
)

# 5. Select features available before shipping
numeric_features = [
    "order_value",
    "num_items",
    "customer_prior_orders",
    "customer_prior_rto",
    "address_length",
    "address_has_number",
    "name_length"
]

categorical_features = [
    "courier",
    "utm_source",
    "city",
    "state"
]

features = numeric_features + categorical_features

X = df[features].copy()
y = df["is_rto"]

# Handle missing values
for col in numeric_features:
    X[col] = pd.to_numeric(X[col], errors="coerce")
    X[col] = X[col].fillna(X[col].median())

for col in categorical_features:
    X[col] = X[col].fillna("Unknown").astype(str)

# 6. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 7. Preprocessing
preprocessor = ColumnTransformer([
    ("numeric", StandardScaler(), numeric_features),
    ("categorical", OneHotEncoder(handle_unknown="ignore"),
     categorical_features)
])

# 8. Build model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42
    ))
])

# 9. Train
print("Training RTO prediction model...")
model.fit(X_train, y_train)

# 10. Evaluate
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("\nMODEL EVALUATION")
print("-------------------------")
print("Accuracy:", round(accuracy_score(y_test, predictions) * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    target_names=["Delivered", "RTO"],
    zero_division=0
))

print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))

print(
    "ROC-AUC:",
    round(roc_auc_score(y_test, probabilities), 3)
)

# 11. Save model and feature configuration
joblib.dump(
    {
        "model": model,
        "features": features,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features
    },
    "rto_model.pkl"
)

print("\nModel saved successfully as rto_model.pkl")

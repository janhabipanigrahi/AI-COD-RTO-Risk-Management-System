import pandas as pd
# Load historical COD orders
df = pd.read_csv("orders_sample.csv")

print("=" * 55)
print("AI COD RISK MANAGEMENT - DATA ANALYSIS")
print("=" * 55)

# Clean column values
df.columns = df.columns.str.strip()
df["final_status"] = (
    df["final_status"].astype(str).str.strip().str.upper()
)

# Keep completed orders only
completed = df[df["final_status"].isin(["DELIVERED", "RTO"])].copy()

completed["is_rto"] = (
    completed["final_status"] == "RTO"
).astype(int)

total = len(completed)
delivered = (completed["final_status"] == "DELIVERED").sum()
rto = completed["is_rto"].sum()

print(f"\nTotal dataset records: {len(df)}")
print(f"Completed orders: {total}")
print(f"Delivered orders: {delivered}")
print(f"RTO orders: {rto}")
print(f"Overall RTO rate: {rto / total * 100:.2f}%")

# Customer history analysis
print("\n--- RTO RATE BY PREVIOUS RTO COUNT ---")

history = completed.groupby("customer_prior_rto").agg(
    total_orders=("order_id", "count"),
    rto_orders=("is_rto", "sum")
)

history["rto_rate"] = (
    history["rto_orders"] / history["total_orders"] * 100
).round(2)

print(history.to_string())

# Courier analysis
print("\n--- COURIER PERFORMANCE ---")

courier = completed.groupby("courier").agg(
    total_orders=("order_id", "count"),
    rto_orders=("is_rto", "sum")
)

courier["rto_rate"] = (
    courier["rto_orders"] / courier["total_orders"] * 100
).round(2)

print(courier.sort_values("rto_rate", ascending=False).to_string())

# Order value analysis
print("\n--- ORDER VALUE ANALYSIS ---")

completed["order_value_group"] = pd.cut(
    completed["order_value"],
    bins=[0, 400, 700, 1000, float("inf")],
    labels=["Below 400", "400-700", "700-1000", "Above 1000"]
)

value_analysis = completed.groupby(
    "order_value_group", observed=True
).agg(
    total_orders=("order_id", "count"),
    rto_orders=("is_rto", "sum")
)

value_analysis["rto_rate"] = (
    value_analysis["rto_orders"] /
    value_analysis["total_orders"] * 100
).round(2)

print(value_analysis.to_string())

# Financial analysis
rto_cost = 65 + 65 + 25 + (0.08 * 180)

print("\n--- FINANCIAL IMPACT ---")
print(f"Estimated direct cost per RTO: Rs. {rto_cost:.2f}")
print(f"Estimated historical RTO cost: Rs. {rto * rto_cost:.2f}")

print("\nAnalysis completed successfully!")

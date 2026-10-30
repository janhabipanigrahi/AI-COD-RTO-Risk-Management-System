import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime, date, timedelta

from decision_engine import predict_risk
from whatsapp_simulator import generate_message, process_reply

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI COD Risk Management",
    page_icon="📦",
    layout="wide"
)

st.title("📦 AI-Powered COD Risk Management System")
st.caption("Intelligent Order Verification and RTO Prevention")

# --------------------------------------------------
# LOAD CONFIGURATION
# --------------------------------------------------

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("orders_sample.csv")
    data["final_status"] = (
        data["final_status"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return data


df = load_data()

# --------------------------------------------------
# LOAD TRAINED ML MODEL
# --------------------------------------------------

model_data = None

if Path("rto_model.pkl").exists():
    model_data = joblib.load("rto_model.pkl")


# --------------------------------------------------
# FINANCIAL ASSUMPTIONS
# --------------------------------------------------

RTO_COST = 65 + 65 + 25 + (0.08 * 180)
GROSS_MARGIN_RATE = 0.62

LOG_FILE = Path("decision_log.csv")


# --------------------------------------------------
# DECISION LOGGING FUNCTIONS
# --------------------------------------------------

def load_decision_log():

    if LOG_FILE.exists():

        try:
            return pd.read_csv(
                LOG_FILE,
                parse_dates=["created_at"]
            )

        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def save_decision(order, result, probability):

    record = {
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "customer_name": order["customer_name"],
        "order_value": float(order["order_value"]),
        "rto_probability": float(probability),
        "action": result["action"],
        "risk_level": result["risk_level"],
        "risk_score": float(result["risk_score"])
    }

    new_row = pd.DataFrame([record])

    if LOG_FILE.exists():

        old = load_decision_log()

        new_row = pd.concat(
            [old, new_row],
            ignore_index=True
        )

    new_row.to_csv(LOG_FILE, index=False)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Select Section",
    [
        "Dashboard",
        "Order Risk Analyzer",
        "WhatsApp Simulator",
        "Business Insights"
    ]
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.header("Business Dashboard")

    completed = df[
        df["final_status"].isin(
            ["DELIVERED", "RTO"]
        )
    ]

    total = len(completed)

    rto_count = int(
        (completed["final_status"] == "RTO").sum()
    )

    delivered_count = int(
        (completed["final_status"] == "DELIVERED").sum()
    )

    rto_rate = (
        rto_count / total * 100
        if total else 0
    )

    # Main metrics

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Completed Orders",
        f"{total:,}"
    )

    col2.metric(
        "Delivered Orders",
        f"{delivered_count:,}"
    )

    col3.metric(
        "RTO Orders",
        f"{rto_count:,}"
    )

    col4.metric(
        "Historical RTO Rate",
        f"{rto_rate:.2f}%"
    )

    st.divider()

    # Historical delivery chart

    st.subheader("Historical Delivery Performance")

    chart = pd.DataFrame(
        {
            "Orders": [
                delivered_count,
                rto_count
            ]
        },
        index=["Delivered", "RTO"]
    )

    st.bar_chart(chart)

    st.divider()

    # Yesterday's decisions

    st.subheader("Yesterday's Decision Breakdown")

    log = load_decision_log()

    if not log.empty and "created_at" in log.columns:

        log["created_at"] = pd.to_datetime(
            log["created_at"],
            errors="coerce"
        )

        yesterday = date.today() - timedelta(days=1)

        yesterday_log = log[
            log["created_at"].dt.date == yesterday
        ]

        if not yesterday_log.empty:

            buckets = [
                "Ship as-is",
                "Ship after confirmation",
                "Nudge to prepaid",
                "Hold / cancel"
            ]

            counts = (
                yesterday_log["action"]
                .value_counts()
                .reindex(buckets, fill_value=0)
            )

            st.bar_chart(counts)

            cols = st.columns(4)

            for col, bucket in zip(cols, buckets):

                col.metric(
                    bucket,
                    int(counts[bucket])
                )

        else:

            st.info(
                "No decisions were logged yesterday. "
                "Run orders through the Order Risk Analyzer "
                "to create decision-log entries. "
                "The dashboard will display actual logged "
                "decisions here."
            )

    else:

        st.info(
            "No decision log exists yet. "
            "Decisions made in the Order Risk Analyzer "
            "will be recorded automatically."
        )

    # Decision log overview

    st.subheader("Decision Log Overview")

    if not log.empty:

        log["created_at"] = pd.to_datetime(
            log["created_at"],
            errors="coerce"
        )

        counts = log["action"].value_counts()

        st.dataframe(
            counts.rename_axis(
                "Recommended Action"
            ).reset_index(
                name="Orders"
            ),
            use_container_width=True
        )

        st.caption(
            f"Total analyzed orders logged: {len(log)}"
        )

    else:

        st.write(
            "No analyzed orders have been logged yet."
        )

    # Business overview

    st.subheader("Business Overview")

    st.write(
        f"Total rows in source dataset: {len(df):,}"
    )

    st.write(
        f"Completed historical orders: {total:,}"
    )

    st.write(
        f"Other statuses excluded from delivery metrics: "
        f"{len(df) - total:,}"
    )

    st.caption(
        "Historical delivery metrics come from the supplied "
        "dataset. Decision buckets come only from orders "
        "analyzed in this app; they are not presented as "
        "historical decisions."
    )


# ==================================================
# ORDER RISK ANALYZER
# ==================================================

elif page == "Order Risk Analyzer":

    st.header("AI COD Order Risk Analyzer")

    if model_data is None:

        st.error(
            "Trained ML model not found. "
            "Run py train_model.py first."
        )

        st.stop()

    with st.form("order_form"):

        st.subheader("Customer Information")

        name = st.text_input(
            "Customer Name",
            value="Rahul Sharma"
        )

        phone = st.text_input(
            "Phone Number",
            value="9876543210"
        )

        address = st.text_area(
            "Delivery Address",
            value="Near SBI Bank, Main Road, Bhubaneswar"
        )

        pincode = st.text_input(
            "Pincode",
            value="751001"
        )

        st.subheader("Order Information")

        order_value = st.number_input(
            "Order Value (₹)",
            min_value=1,
            value=649
        )

        num_items = st.number_input(
            "Number of Items",
            min_value=1,
            value=1
        )

        previous_orders = st.number_input(
            "Previous Orders",
            min_value=0,
            value=3
        )

        previous_rto = st.number_input(
            "Previous RTOs",
            min_value=0,
            value=0
        )

        courier = st.text_input(
            "Courier",
            value="Delhivery"
        )

        city = st.text_input(
            "City",
            value="Bhubaneswar"
        )

        state = st.text_input(
            "State",
            value="Odisha"
        )

        utm_source = st.selectbox(
            "Marketing Source",
            [
                "meta_ads",
                "google_ads",
                "organic",
                "Unknown"
            ]
        )

        submitted = st.form_submit_button(
            "Analyse Order",
            use_container_width=True
        )

    if submitted:

        order = {
            "customer_name": name,
            "phone": phone,
            "address": address,
            "pincode": pincode,
            "order_value": order_value,
            "customer_prior_orders": previous_orders,
            "customer_prior_rto": previous_rto,
            "num_items": num_items,
            "courier": courier,
            "city": city,
            "state": state,
            "utm_source": utm_source
        }

        if not name.strip() or not address.strip():

            st.error(
                "Please enter customer name and address."
            )

        else:

            # Prepare model features

            features = model_data["features"]

            model_order = order.copy()

            model_order["address_length"] = len(
                address.strip()
            )

            model_order["address_has_number"] = int(
                any(ch.isdigit() for ch in address)
            )

            model_order["name_length"] = len(
                name.strip()
            )

            model_input = pd.DataFrame([
                {
                    feature: model_order.get(feature, 0)
                    for feature in features
                }
            ])

            # ML prediction

            model = model_data["model"]

            ml_probability = float(
                model.predict_proba(model_input)[0][1]
            )

            # Decision engine

            result = predict_risk(
                order,
                ml_probability
            )

            # Save decision automatically

            save_decision(
                order,
                result,
                ml_probability
            )

            st.divider()

            st.subheader("ML Prediction")

            col1, col2 = st.columns(2)

            col1.metric(
                "Predicted RTO Probability",
                f"{ml_probability * 100:.2f}%"
            )

            col2.metric(
                "Risk Score",
                f"{result['risk_score']}/100"
            )

            st.subheader("Decision Engine Result")

            st.write(
                f"**Risk Level:** {result['risk_level']}"
            )

            st.success(
                f"Recommended Action: {result['action']}"
            )

            st.write(
                f"**Reason:** {result['reason']}"
            )

            st.caption(
                "This analysis has been added to "
                "decision_log.csv for dashboard reporting."
            )

            # WhatsApp message preview

            if result["action"] in [
                "Ship after confirmation",
                "Nudge to prepaid"
            ]:

                st.divider()

                st.subheader(
                    "WhatsApp Message Preview"
                )

                message = generate_message(
                    name,
                    result["action"],
                    config["prepaid_discount"]
                )

                st.chat_message(
                    "assistant"
                ).write(message)

            elif result["action"] == "Hold / cancel":

                st.warning(
                    "Order requires manual review "
                    "before cancellation."
                )


# ==================================================
# WHATSAPP SIMULATOR
# ==================================================

elif page == "WhatsApp Simulator":

    st.header(
        "WhatsApp Customer Confirmation Simulator"
    )

    customer = st.text_input(
        "Customer Name",
        value="Rahul"
    )

    action = st.selectbox(
        "Select Workflow",
        [
            "Ship after confirmation",
            "Nudge to prepaid"
        ]
    )

    message = generate_message(
        customer,
        action,
        config["prepaid_discount"]
    )

    st.subheader("Message Preview")

    st.chat_message(
        "assistant"
    ).write(message)

    reply = st.text_input(
        "Customer Reply",
        placeholder="Type YES, NO or another response"
    )

    hours = st.number_input(
        "Hours Since Message",
        min_value=0,
        max_value=48,
        value=0
    )

    if st.button("Process Customer Reply"):

        result = process_reply(
            action,
            reply,
            hours_elapsed=hours
        )

        st.subheader("Customer Response")

        st.write(
            "**Status:**",
            result["status"]
        )

        st.write(
            "**Next Action:**",
            result["next_action"]
        )

        st.info(result["message"])


# ==================================================
# BUSINESS INSIGHTS
# ==================================================

elif page == "Business Insights":

    st.header(
        "Business Insights & Financial Analysis"
    )

    completed = df[
        df["final_status"].isin(
            ["DELIVERED", "RTO"]
        )
    ]

    rto_count = int(
        (completed["final_status"] == "RTO").sum()
    )

    delivered_count = int(
        (completed["final_status"] == "DELIVERED").sum()
    )

    historical_loss = rto_count * RTO_COST

    # Historical financial impact

    st.subheader("Historical Financial Impact")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Estimated Direct Cost per RTO",
        f"₹{RTO_COST:.2f}"
    )

    col2.metric(
        "Historical RTO Orders",
        f"{rto_count:,}"
    )

    col3.metric(
        "Estimated Historical RTO Cost",
        f"₹{historical_loss:,.2f}"
    )

    st.caption(
        "RTO cost = ₹65 forward shipping + "
        "₹65 return shipping + ₹25 packaging/handling "
        "+ expected ₹14.40 damage cost."
    )

    st.divider()

    # COD vs prepaid comparison

    st.subheader("COD vs Prepaid Comparison")

    cod_rto = 0.28
    prepaid_rto = 0.04

    discount = float(
        config["prepaid_discount"]
    )

    avoided_cost_per_conversion = (
        (cod_rto - prepaid_rto) * RTO_COST
    )

    net_saving_per_conversion = (
        avoided_cost_per_conversion - discount
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "COD RTO Assumption",
        "28%"
    )

    col2.metric(
        "Prepaid RTO Assumption",
        "4%"
    )

    col3.metric(
        "Net Expected Saving / Conversion",
        f"₹{net_saving_per_conversion:.2f}"
    )

    st.write(
        f"Expected reduction in RTO cost before discount: "
        f"**₹{avoided_cost_per_conversion:.2f}** "
        f"per prepaid conversion."
    )

    st.write(
        f"Prepaid discount: **₹{discount:.2f}**."
    )

    st.caption(
        "Estimate based on the assignment's COD/prepaid "
        "RTO assumptions. It is not a measured result "
        "or guaranteed saving."
    )

    st.divider()

    # Decision log financial impact

    st.subheader(
        "Decision Log: Estimated Impact"
    )

    log = load_decision_log()

    if not log.empty:

        log["rto_probability"] = (
            pd.to_numeric(
                log["rto_probability"],
                errors="coerce"
            )
            .fillna(0)
            .clip(0, 1)
        )

        log["order_value"] = (
            pd.to_numeric(
                log["order_value"],
                errors="coerce"
            )
            .fillna(0)
        )

        held = log[
            log["action"]
            .astype(str)
            .str.lower()
            .isin(
                ["hold / cancel", "hold/cancel"]
            )
        ]

        expected_rto_cost_avoided = (
            held["rto_probability"] * RTO_COST
        ).sum()

        estimated_genuine_margin_lost = (
            (1 - held["rto_probability"])
            * held["order_value"]
            * GROSS_MARGIN_RATE
        ).sum()

        estimated_net_impact = (
            expected_rto_cost_avoided
            - estimated_genuine_margin_lost
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Estimated RTO Cost Exposure Avoided",
            f"₹{expected_rto_cost_avoided:,.2f}"
        )

        col2.metric(
            "Estimated Genuine-Order Margin at Risk",
            f"₹{estimated_genuine_margin_lost:,.2f}"
        )

        col3.metric(
            "Estimated Net Impact",
            f"₹{estimated_net_impact:,.2f}"
        )

        st.caption(
            "Scenario estimates for logged Hold/Cancel "
            "recommendations: expected RTO exposure = "
            "probability × ₹169.40; potential genuine-order "
            "margin = (1 − probability) × order value × 62%. "
            "These are estimates, not realized savings or "
            "confirmed cancellations."
        )

        st.dataframe(
            log.tail(20),
            use_container_width=True
        )

    else:

        st.info(
            "Analyze orders first. The app will log each "
            "prediction and estimate the potential financial "
            "impact of Hold/Cancel recommendations."
        )
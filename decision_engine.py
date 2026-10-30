
import json
import re
from pathlib import Path

DEFAULT_CONFIG = {
    "ship_threshold": 25,
    "confirm_threshold": 45,
    "prepaid_threshold": 65,
    "prepaid_discount": 20
}


def predict_risk(order, ml_probability=None):

    config_path = Path("config.json")

    if config_path.exists():
        with open(config_path, "r") as file:
            config = {**DEFAULT_CONFIG, **json.load(file)}
    else:
        config = DEFAULT_CONFIG

    reasons = []

    name = str(order.get("customer_name", "")).strip()
    address = str(order.get("address", "")).strip()
    phone = re.sub(r"\D", "", str(order.get("phone", "")))
    pincode = re.sub(r"\D", "", str(order.get("pincode", "")))

    previous_rto = int(order.get("customer_prior_rto", 0) or 0)

    # Identify additional verification concerns
    if previous_rto >= 2:
        reasons.append("Customer has multiple previous RTOs")
    elif previous_rto == 1:
        reasons.append("Customer has a previous RTO")

    if len(name) < 3 or name.lower() in [
        "test", "asdf", "dummy", "unknown"
    ]:
        reasons.append("Customer name requires verification")

    if len(address) < 12:
        reasons.append("Delivery address appears incomplete")

    if len(phone) < 10:
        reasons.append("Phone number requires verification")

    if len(pincode) != 6:
        reasons.append("Pincode requires verification")

    # Use trained ML probability as the primary risk score
    if ml_probability is None:
        raise ValueError(
            "ML probability is required for the final decision."
        )

    risk = round(float(ml_probability) * 100, 2)

    # Configurable decision thresholds
    if risk < config["ship_threshold"]:
        action = "Ship as-is"

    elif risk < config["confirm_threshold"]:
        action = "Ship after confirmation"

    elif risk < config["prepaid_threshold"]:
        action = "Nudge to prepaid"

    else:
        action = "Hold / cancel"

    if not reasons:
        reasons.append(
            "Customer and address checks show no obvious verification issues"
        )

    reasons.append(
        f"ML model estimates {risk:.2f}% probability of RTO"
    )

    return {
        "risk_score": risk,
        "risk_level": (
            "Low" if risk < 35 else
            "Medium" if risk < 65 else
            "High"
        ),
        "action": action,
        "reason": "; ".join(reasons)
    }



from datetime import datetime, timedelta


def generate_message(customer_name, action, discount=20):
    if action == "Ship after confirmation":
        return (
            f"Hello {customer_name}! Thank you for your order. "
            "Please confirm your COD order by replying YES. "
            "Reply NO if you wish to cancel."
        )

    if action == "Nudge to prepaid":
        return (
            f"Hello {customer_name}! Complete your payment online "
            f"and receive Rs. {discount} OFF. "
            "Reply YES to accept the prepaid offer or NO to continue with COD."
        )

    return "No WhatsApp message required."


def process_reply(action, reply, hours_elapsed=0):
    reply = str(reply).strip().lower()

    if hours_elapsed >= 24:
        return {
            "status": "Timeout",
            "next_action": "Hold / cancel",
            "message": "No response received within 24 hours."
        }

    if action == "Ship after confirmation":
        if reply in ["yes", "y"]:
            return {
                "status": "Confirmed",
                "next_action": "Ship as-is",
                "message": "Customer confirmed. Order can be shipped."
            }

        if reply in ["no", "n"]:
            return {
                "status": "Rejected",
                "next_action": "Cancel",
                "message": "Customer rejected the order."
            }

        return {
            "status": "Waiting",
            "next_action": "Await clear confirmation",
            "message": "Please reply YES or NO."
        }

    if action == "Nudge to prepaid":
        if reply in ["yes", "y"]:
            return {
                "status": "Offer accepted",
                "next_action": "Send payment link",
                "message": "Prepaid offer accepted. Complete online payment."
            }

        if reply in ["no", "n"]:
            return {
                "status": "Offer declined",
                "next_action": "Continue COD with confirmation",
                "message": "Prepaid offer declined. Confirm the COD order."
            }

        return {
            "status": "Waiting",
            "next_action": "Await clear response",
            "message": "Please reply YES or NO."
        }

    return {
        "status": "Not applicable",
        "next_action": "Review order",
        "message": "No confirmation workflow is required."
    }


if __name__ == "__main__":
    action = "Ship after confirmation"
    name = "Rahul"

    print("WHATSAPP SIMULATOR")
    print("-" * 40)

    print("\nMessage sent:")
    print(generate_message(name, action))

    reply = input("\nEnter customer reply (yes/no/random): ")
    result = process_reply(action, reply)

    print("\nCustomer response:")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n24-hour timeout test:")
    print(process_reply(action, "", hours_elapsed=24))

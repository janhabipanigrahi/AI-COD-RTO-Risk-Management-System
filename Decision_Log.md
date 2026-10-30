# Decision Log
## AI-Powered COD Risk Management System

I maintained this log to explain the main decisions I made while developing this project.

### 1. Choosing the machine learning model
I chose Random Forest to predict the possibility of an order becoming RTO. I considered using simple fixed rules, but I wanted the system to learn patterns from the historical order data. Random Forest was a practical choice for this dataset and was easy to integrate with Python.

### 2. Selecting the input features
I used available details such as order value, number of items, previous orders, previous RTOs, address length, courier, city, state and marketing source. I selected these fields because delivery outcomes may depend on several factors rather than just the order amount.

### 3. Keeping thresholds editable
I stored the risk thresholds in config.json so they can be changed without modifying the main application code.

The current thresholds are:
- Below 25%: Ship as-is
- 25% to below 45%: Ship after confirmation
- 45% to below 65%: Nudge to prepaid
- 65% and above: Hold / cancel

I selected these as starting values for this assignment. They should be reviewed using real order results before business use.

### 4. Selecting the prepaid discount
I selected a ₹20 discount for prepaid orders.

According to the assignment, COD RTO is 28% and prepaid RTO is 4%. The difference is 24%.

Expected RTO cost reduction:
24% × ₹169.40 = ₹40.66

After the ₹20 discount:
₹40.66 - ₹20 = ₹20.66 estimated net benefit per conversion.

This is an estimate based on the assignment figures, not actual savings.

### 5. WhatsApp simulation
I created a simple WhatsApp response simulator to demonstrate YES, NO, unclear replies and no response within 24 hours.

I did not connect a real WhatsApp account because the assignment allows a mock API or chat simulator.

### 6. Calculating RTO cost
I used the cost figures provided in the assignment:

- Forward shipping: ₹65
- Return shipping: ₹65
- Packaging and handling: ₹25
- Expected product damage: ₹14.40

Total estimated RTO cost = ₹169.40.

I have shown these values as estimates because the application is not connected to a live business.

### 7. Testing the decisions
I tested the application using sample customer details. Four orders received Ship after confirmation and four received Nudge to prepaid.

None of my tested orders received Ship as-is or Hold / cancel. I kept the actual results instead of changing thresholds just to show all four categories.

### 8. Current limitations
The current version does not have an actual LLM integration for checking incomplete addresses, fake names or Hinglish addresses. The prediction is made using the Scikit-learn Random Forest model.

If I continue this project, I would like to add an LLM-assisted validation feature while keeping the numerical calculations in Python.

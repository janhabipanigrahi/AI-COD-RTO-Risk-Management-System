# AI-Powered COD Risk Management System

## About the Project

This project helps an online business identify COD orders that may have
a higher chance of becoming Return to Origin (RTO). It uses a machine
learning model to estimate the risk and suggests what action the
business can take before shipping the order.

## Main Features

-   Analyzes order and customer details.
-   Predicts the probability of an order becoming RTO.
-   Recommends one of four actions: Ship as-is, Ship after confirmation,
    Nudge to prepaid, or Hold / cancel.
-   Simulates WhatsApp confirmation replies such as YES, NO, unclear
    replies, and no response after 24 hours.
-   Displays order statistics, risk decisions, and estimated business
    impact in a Streamlit dashboard.
-   Saves analyzed orders in a decision log.

## Technologies Used

-   Python
-   Pandas
-   Scikit-learn
-   Streamlit
-   Joblib
-   CSV and JSON

## Project Files

-   `app.py` -- Runs the Streamlit application.
-   `data_analysis.py` -- Reads the order data and calculates basic
    business statistics.
-   `train_model.py` -- Trains and saves the machine learning model.
-   `decision_engine.py` -- Selects an action based on the predicted
    risk and configured thresholds.
-   `whatsapp_simulator.py` -- Simulates customer confirmation replies.
-   `config.json` -- Stores editable risk thresholds and settings.
-   `orders_sample.csv` -- Sample order data supplied for the
    assignment.
-   `rto_model.pkl` -- Saved trained model.
-   `decision_log.csv` -- Stores order analyses made through the
    application.

## How to Run the Project

### 1. Install the required packages

Open a terminal in the project folder and run:

``` bash
py -m pip install pandas scikit-learn streamlit joblib
```

### 2. Train the model

Run this command if you need to train the model again:

``` bash
py train_model.py
```

This creates or updates `rto_model.pkl`.

### 3. Start the application

Run:

``` bash
py -m streamlit run app.py
```

The application will open in your web browser.

## How the Decision Process Works

The model predicts an RTO probability for an order. The decision engine
compares that probability with the thresholds in `config.json` and
recommends an action. The thresholds can be changed without editing the
main decision-engine code.

The WhatsApp section is a simulation for demonstration. It does not send
real WhatsApp messages.

## Business Assumptions

The project uses the cost and RTO assumptions given in the assignment:

-   Forward shipping: ₹65
-   Return shipping: ₹65
-   Packaging and handling: ₹25
-   Expected product damage cost: ₹14.40
-   Estimated direct cost per RTO: ₹169.40

Any savings or business impact shown by the application are estimates
based on these assumptions. They are not confirmed business results.

## Notes and Limitations

-   The model is trained on the sample dataset provided for the
    assignment.
-   The test orders are examples used to check the application flow.
    They do not prove production accuracy or actual cost savings.
-   The WhatsApp feature is simulated; no live WhatsApp service is
    connected.
-   High-risk orders should be reviewed by a person before cancellation.
-   The application should be tested with more real order outcomes
    before being used for business decisions.

## Author

Developed as an Associate Software Engineer assignment.

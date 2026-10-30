# AI Usage Log
## AI-Powered COD Risk Management System

I used AI assistance during this assignment to understand requirements, plan the project, solve coding doubts and prepare documentation. I reviewed the suggestions and tested the application rather than accepting every suggestion without checking.

## Tools used

- ChatGPT: Helped me  troubleshoot coding questions and improve documentation.
- Python and Scikit-learn: Used to prepare the data and train the Random Forest model.
- Streamlit: Used to build the dashboard and application interface.

## Examples of suggestions I checked and improved

### 1. README file format
Initially, I had a Word document version of the README. I clarified that GitHub requires a separate README.md file for the repository's main documentation.

I created a separate Markdown README and kept the Word document only as an optional supporting document.

### 2. Document formatting
An earlier document version did not have the layout I wanted. I reviewed the formatting and requested improvements to the margins, headings and spacing.

### 3. Dashboard showing zero impact
During testing, the Hold / cancel impact was showing zero. I checked the decision log and found that none of my tested orders had received that recommendation.

I kept the value at zero rather than changing the model results just to display savings.

## What I verified myself

- I ran the application locally.
- I entered sample orders and checked the predicted risk scores and recommended actions.
- I reviewed the completed-order count and historical RTO rate.
- I checked the financial calculations against the assignment assumptions.

## Current limitations

The application does not currently use ChatGPT or another LLM at runtime for address validation, fake-name detection or Hinglish interpretation.

The WhatsApp feature is also a simulator and does not send real messages.

I have included these limitations so the documentation accurately describes what I have implemented. If I get more time, I would like to add LLM-based address validation and test it separately from the numerical prediction model.

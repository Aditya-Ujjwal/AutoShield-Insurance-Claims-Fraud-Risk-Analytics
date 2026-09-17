import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import joblib
import json


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AutoShield | Fraud Risk Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIR / "fraud_detection_pipeline.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
SCHEMA_PATH = MODEL_DIR / "feature_schema.json"


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metadata():

    if METADATA_PATH.exists():

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    return {
        "model_name": "Random Forest",
        "classification_threshold": 0.20
    }


try:
    model = load_model()
    metadata = load_metadata()

except FileNotFoundError:

    st.error(
        "Model files could not be found. "
        "Make sure the models folder contains "
        "`fraud_detection_pipeline.joblib`."
    )

    st.stop()

except Exception as error:

    st.error(
        f"Unable to load the fraud detection model: {error}"
    )

    st.stop()


THRESHOLD = float(
    metadata.get(
        "classification_threshold",
        0.20
    )
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {
    background:
        linear-gradient(
            135deg,
            #07111f 0%,
            #0b1728 45%,
            #101d31 100%
        );
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    padding: 2.2rem 2.4rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.38),
            rgba(14, 165, 233, 0.13)
        );
    border: 1px solid rgba(148, 163, 184, 0.18);
    margin-bottom: 1.8rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}

.shield {
    font-size: 3rem;
    margin-bottom: 0.4rem;
}

.hero-title {
    font-size: 2.75rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f8fafc;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    line-height: 1.65;
    max-width: 850px;
}


/* ============================================================
   SECTION HEADERS
   ============================================================ */

.section-title {
    font-size: 1.4rem;
    font-weight: 750;
    color: #f8fafc;
    margin-top: 1.1rem;
    margin-bottom: 0.25rem;
}

.section-description {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 1.15rem;
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    padding: 1rem;
    text-align: center;
    min-height: 105px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.metric-label {
    color: #94a3b8;
    font-size: 0.82rem;
    margin-bottom: 0.45rem;
}

.metric-value {
    color: #f8fafc;
    font-size: 1.4rem;
    font-weight: 750;
}


/* ============================================================
   RESULT CARD
   ============================================================ */

.result-card {
    border-radius: 24px;
    padding: 2rem;
    margin-top: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
    text-align: center;
}

.result-title {
    font-size: 0.95rem;
    letter-spacing: 1.2px;
    color: #cbd5e1;
    margin-bottom: 0.7rem;
}

.result-probability {
    font-size: 4rem;
    font-weight: 850;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.85rem;
}

.result-status {
    display: inline-block;
    padding: 0.5rem 1.15rem;
    border-radius: 999px;
    font-size: 0.92rem;
    font-weight: 750;
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
}


/* ============================================================
   INFO BOX
   ============================================================ */

.info-box {
    background: rgba(30, 41, 59, 0.68);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    color: #cbd5e1;
    font-size: 0.88rem;
    line-height: 1.65;
    margin-top: 1rem;
}


/* ============================================================
   BUTTON
   ============================================================ */

div.stButton > button {
    width: 100%;
    height: 3.3rem;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.13);
    font-size: 1rem;
    font-weight: 750;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #08111f 0%,
            #0c1727 100%
        );
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

.sidebar-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-text {
    color: #94a3b8;
    font-size: 0.86rem;
    line-height: 1.6;
}


/* ============================================================
   STREAMLIT TEXT
   ============================================================ */

.stMarkdown {
    color: #e2e8f0;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🛡️ AutoShield</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="sidebar-text">
Insurance Claims & Fraud Risk Analytics
</div>
""",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Model Information")

    st.write(
        f"**Model:** "
        f"{metadata.get('model_name', 'Random Forest')}"
    )

    st.write(
        f"**Decision Threshold:** "
        f"{THRESHOLD:.2f}"
    )

    st.write(
        "**Task:** Binary Classification"
    )

    st.write(
        "**Target:** Synthetic Fraud Risk"
    )

    st.divider()

    st.markdown("### How It Works")

    st.markdown(
        """
<div class="sidebar-text">
Enter customer, vehicle, policy and claim information.
AutoShield calculates the required derived features and sends
them through the trained machine-learning pipeline.
</div>
""",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        """
<div class="sidebar-text">
<b>Important:</b> This application uses a synthetic insurance
dataset and a synthetic fraud-risk target for demonstration.
Predictions should not be interpreted as real-world fraud
determinations.
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
<div class="hero">
<div class="shield">🛡️</div>
<div class="hero-title">AutoShield Fraud Risk Detector</div>
<div class="hero-subtitle">
Evaluate insurance claims using customer, vehicle, policy
and accident characteristics with a machine-learning
fraud-risk model.
</div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CUSTOMER INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">👤 Customer Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Enter the policyholder information associated with the claim.'
    '</div>',
    unsafe_allow_html=True
)

customer_col1, customer_col2, customer_col3 = st.columns(3)

with customer_col1:

    gender = st.selectbox(
        "Gender",
        ["Female", "Male"]
    )

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=35,
        step=1
    )

with customer_col2:

    marital_status = st.selectbox(
        "Marital Status",
        ["Single", "Married"]
    )

    occupation = st.selectbox(
        "Occupation",
        [
            "Teacher",
            "Business",
            "Engineer",
            "Doctor",
            "Govt",
            "Student"
        ]
    )

with customer_col3:

    annual_income = st.number_input(
        "Annual Income (₹)",
        min_value=0.0,
        value=2500000.0,
        step=50000.0,
        format="%.2f"
    )

    driving_experience = st.number_input(
        "Driving Experience (Years)",
        min_value=0,
        max_value=70,
        value=10,
        step=1
    )


# ============================================================
# VEHICLE INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">🚗 Vehicle Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Provide the vehicle characteristics covered by the insurance policy.'
    '</div>',
    unsafe_allow_html=True
)

vehicle_col1, vehicle_col2, vehicle_col3 = st.columns(3)

with vehicle_col1:

    vehicle_type = st.selectbox(
        "Vehicle Type",
        [
            "Sedan",
            "Motorcycle",
            "SUV",
            "Hatchback"
        ]
    )

    brand = st.selectbox(
        "Brand",
        [
            "Kia",
            "Hyundai",
            "Mahindra",
            "Maruti",
            "BMW",
            "Tata",
            "Toyota",
            "Honda"
        ]
    )

with vehicle_col2:

    manufacture_year = st.number_input(
        "Manufacture Year",
        min_value=2000,
        max_value=2026,
        value=2020,
        step=1
    )

    fuel_type = st.selectbox(
        "Fuel Type",
        [
            "Diesel",
            "Electric",
            "CNG",
            "Petrol",
            "Hybrid"
        ]
    )

with vehicle_col3:

    engine_cc = st.number_input(
        "Engine Capacity (CC)",
        min_value=100.0,
        value=1200.0,
        step=50.0
    )

    vehicle_value = st.number_input(
        "Vehicle Value (₹)",
        min_value=1.0,
        value=4000000.0,
        step=50000.0,
        format="%.2f"
    )


# ============================================================
# POLICY INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">📄 Policy Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Enter the insurance policy details associated with this claim.'
    '</div>',
    unsafe_allow_html=True
)

policy_col1, policy_col2, policy_col3 = st.columns(3)

with policy_col1:

    policy_type = st.selectbox(
        "Policy Type",
        [
            "Comprehensive",
            "Zero Depreciation",
            "Third Party"
        ]
    )

with policy_col2:

    coverage_amount = st.number_input(
        "Coverage Amount (₹)",
        min_value=1.0,
        value=5000000.0,
        step=50000.0,
        format="%.2f"
    )

with policy_col3:

    premium_amount = st.number_input(
        "Premium Amount (₹)",
        min_value=1.0,
        value=40000.0,
        step=1000.0,
        format="%.2f"
    )

    no_claim_bonus = st.number_input(
        "No-Claim Bonus (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=1.0
    )


# ============================================================
# CLAIM INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">🚨 Claim Information</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Enter the details of the insurance claim and accident.'
    '</div>',
    unsafe_allow_html=True
)

claim_col1, claim_col2, claim_col3 = st.columns(3)

with claim_col1:

    claim_date = st.date_input(
        "Claim Date",
        value=date(2025, 6, 15)
    )

    accident_city = st.text_input(
        "Accident City",
        value="Delhi"
    )

    accident_type = st.selectbox(
        "Accident Type",
        [
            "Flood",
            "Theft",
            "Major Accident",
            "Collision",
            "Fire",
            "Minor Accident"
        ]
    )

with claim_col2:

    weather_condition = st.selectbox(
        "Weather Condition",
        [
            "Sunny",
            "Rainy",
            "Cloudy",
            "Storm",
            "Fog"
        ]
    )

    police_report = st.selectbox(
        "Police Report Filed?",
        [
            "Yes",
            "No"
        ]
    )

    injuries = st.selectbox(
        "Injuries",
        [
            "Minor",
            "Serious",
            "Unknown"
        ]
    )

with claim_col3:

    estimated_damage = st.number_input(
        "Estimated Damage Cost (₹)",
        min_value=1.0,
        value=1000000.0,
        step=25000.0,
        format="%.2f"
    )

    claim_amount = st.number_input(
        "Claim Amount (₹)",
        min_value=1.0,
        value=900000.0,
        step=25000.0,
        format="%.2f"
    )


# ============================================================
# POLICY TIMELINE
# ============================================================

st.markdown(
    '<div class="section-title">📅 Policy Timeline</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'These dates are used to calculate policy timing features.'
    '</div>',
    unsafe_allow_html=True
)

date_col1, date_col2 = st.columns(2)

with date_col1:

    policy_start = st.date_input(
        "Policy Start Date",
        value=date(2024, 1, 1)
    )

with date_col2:

    policy_end = st.date_input(
        "Policy End Date",
        value=date(2025, 12, 31)
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

validation_errors = []

if driving_experience > max(age - 18, 0):

    validation_errors.append(
        "Driving experience is greater than the maximum "
        "implied by the customer's age."
    )

if manufacture_year > claim_date.year:

    validation_errors.append(
        "Vehicle manufacture year cannot be later than "
        "the claim year."
    )

if policy_end <= policy_start:

    validation_errors.append(
        "Policy end date must be after the policy start date."
    )

if claim_date < policy_start:

    validation_errors.append(
        "Claim date cannot occur before the policy start date."
    )

if claim_date > policy_end:

    validation_errors.append(
        "Claim date cannot occur after the policy end date."
    )

if claim_amount > estimated_damage:

    validation_errors.append(
        "Claim amount cannot exceed estimated damage cost."
    )


if validation_errors:

    for error in validation_errors:
        st.warning(error)


# ============================================================
# DERIVED FEATURE PREVIEW
# ============================================================

with st.expander(
    "🔎 Preview calculated claim-risk features"
):

    vehicle_age_preview = (
        claim_date.year - manufacture_year
    )

    premium_coverage_preview = (
        premium_amount / coverage_amount
    )

    claim_damage_preview = (
        claim_amount / estimated_damage
    )

    claim_vehicle_preview = (
        claim_amount / vehicle_value
    )

    claim_coverage_preview = (
        claim_amount / coverage_amount
    )

    damage_vehicle_preview = (
        estimated_damage / vehicle_value
    )

    claim_income_preview = (
        claim_amount / annual_income
        if annual_income > 0
        else 0
    )

    policy_age_preview = (
        claim_date - policy_start
    ).days

    days_to_end_preview = (
        policy_end - claim_date
    ).days

    preview_cols = st.columns(4)

    preview_data = [
        (
            "Vehicle Age",
            f"{vehicle_age_preview} years"
        ),
        (
            "Claim / Damage",
            f"{claim_damage_preview:.2f}"
        ),
        (
            "Claim / Coverage",
            f"{claim_coverage_preview:.2f}"
        ),
        (
            "Claim / Vehicle Value",
            f"{claim_vehicle_preview:.2f}"
        ),
        (
            "Premium / Coverage",
            f"{premium_coverage_preview:.3f}"
        ),
        (
            "Damage / Vehicle Value",
            f"{damage_vehicle_preview:.2f}"
        ),
        (
            "Claim / Income",
            f"{claim_income_preview:.2f}"
        ),
        (
            "Policy Age",
            f"{policy_age_preview} days"
        )
    ]

    for index, (label, value) in enumerate(
        preview_data
    ):

        col = preview_cols[index % 4]

        with col:

            st.markdown(
                f"""
<div class="metric-card">
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# PREDICTION BUTTON
# ============================================================

st.markdown("---")

predict_col1, predict_col2, predict_col3 = st.columns(
    [1, 2, 1]
)

with predict_col2:

    predict_button = st.button(
        "🛡️ ANALYZE CLAIM FOR FRAUD RISK",
        type="primary",
        use_container_width=True
    )


# ============================================================
# PREDICTION
# ============================================================

if predict_button:

    if validation_errors:

        st.error(
            "Please correct the highlighted input issues "
            "before running the prediction."
        )

        st.stop()


    # ========================================================
    # DERIVED FEATURES
    # ========================================================

    vehicle_age = (
        claim_date.year - manufacture_year
    )

    premium_coverage_ratio = (
        premium_amount / coverage_amount
    )

    claim_damage_ratio = (
        claim_amount / estimated_damage
    )

    claim_vehicle_value_ratio = (
        claim_amount / vehicle_value
    )

    claim_coverage_ratio = (
        claim_amount / coverage_amount
    )

    damage_vehicle_value_ratio = (
        estimated_damage / vehicle_value
    )

    claim_income_ratio = (
        claim_amount / annual_income
        if annual_income > 0
        else 0
    )

    policy_age_at_claim = (
        claim_date - policy_start
    ).days

    days_to_policy_end = (
        policy_end - claim_date
    ).days

    claim_year = claim_date.year

    claim_month = claim_date.month

    claim_day_of_week = (
        claim_date.weekday()
    )

    claim_weekend = int(
        claim_day_of_week >= 5
    )


    # ========================================================
    # MODEL INPUT
    # ========================================================

    input_data = pd.DataFrame([
        {
            # Customer
            "Gender": gender,
            "Age": age,
            "Marital_Status": marital_status,
            "Occupation": occupation,
            "Annual_Income": annual_income,
            "Driving_Experience_Years": driving_experience,

            # Vehicle
            "Vehicle_Type": vehicle_type,
            "Brand": brand,
            "Manufacture_Year": manufacture_year,
            "Fuel_Type": fuel_type,
            "Engine_CC": engine_cc,
            "Vehicle_Value": vehicle_value,

            # Policy
            "Policy_Type": policy_type,
            "Coverage_Amount": coverage_amount,
            "Premium_Amount": premium_amount,
            "No_Claim_Bonus": no_claim_bonus,

            # Claim
            "Accident_City": accident_city,
            "Accident_Type": accident_type,
            "Weather_Condition": weather_condition,
            "Police_Report_Filed": police_report,
            "Injuries": injuries,
            "Estimated_Damage_Cost": estimated_damage,
            "Claim_Amount": claim_amount,

            # Engineered
            "Vehicle_Age": vehicle_age,
            "Premium_Coverage_Ratio": premium_coverage_ratio,
            "Claim_Damage_Ratio": claim_damage_ratio,
            "Claim_Vehicle_Value_Ratio": claim_vehicle_value_ratio,
            "Claim_Coverage_Ratio": claim_coverage_ratio,
            "Damage_Vehicle_Value_Ratio": damage_vehicle_value_ratio,
            "Claim_Income_Ratio": claim_income_ratio,

            # Temporal
            "Claim_Year": claim_year,
            "Claim_Month": claim_month,
            "Claim_DayOfWeek": claim_day_of_week,
            "Claim_Weekend": claim_weekend,

            # Policy timing
            "Policy_Age_At_Claim": policy_age_at_claim,
            "Days_To_Policy_End": days_to_policy_end
        }
    ])


    # ========================================================
    # PREDICTION
    # ========================================================

    fraud_probability = model.predict_proba(
        input_data
    )[0, 1]

    fraud_prediction = int(
        fraud_probability >= THRESHOLD
    )

    probability_percentage = (
        fraud_probability * 100
    )


    # ========================================================
    # RESULT STYLE
    # ========================================================

    if fraud_prediction == 1:

        result_title = "HIGHER FRAUD RISK"

        result_background = (
            "linear-gradient("
            "135deg,"
            "rgba(127, 29, 29, 0.90),"
            "rgba(153, 27, 27, 0.65)"
            ")"
        )

    else:

        result_title = "LOWER FRAUD RISK"

        result_background = (
            "linear-gradient("
            "135deg,"
            "rgba(6, 78, 59, 0.90),"
            "rgba(4, 120, 87, 0.65)"
            ")"
        )


    # ========================================================
    # RESULT CARD
    # ========================================================

    st.markdown(
        f"""
<div class="result-card" style="background:{result_background};">
<div class="result-title">MODEL FRAUD PROBABILITY</div>
<div class="result-probability">
{probability_percentage:.1f}%
</div>
<div class="result-status">
{result_title}
</div>
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # RISK LEVEL
    # ========================================================

    st.markdown("### Risk Level")

    st.progress(
        min(
            max(
                fraud_probability,
                0.0
            ),
            1.0
        )
    )

    st.markdown(
        f"""
<div class="info-box">
The model uses a classification threshold of
<b>{THRESHOLD:.0%}</b>.
Claims with a predicted probability at or above this
threshold are classified as higher fraud risk.
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # ASSESSMENT SUMMARY
    # ========================================================

    st.markdown(
        "### Claim Assessment Summary"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Fraud Probability</div>
<div class="metric-value">
{probability_percentage:.1f}%
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with metric2:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Claim Amount</div>
<div class="metric-value">
₹{claim_amount:,.0f}
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with metric3:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Claim / Damage</div>
<div class="metric-value">
{claim_damage_ratio:.2f}
</div>
</div>
""",
            unsafe_allow_html=True
        )


    with metric4:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Policy Age</div>
<div class="metric-value">
{policy_age_at_claim:,} days
</div>
</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # MODEL INPUT DETAILS
    # ========================================================

    with st.expander(
        "📊 View model input features"
    ):

        st.dataframe(
            input_data.T.rename(
                columns={0: "Value"}
            ),
            use_container_width=True
        )


    # ========================================================
    # INTERPRETATION
    # ========================================================

    st.markdown("### 🧠 Prediction Interpretation")

    if fraud_prediction == 1:

        st.warning(
            "The model's predicted probability is above the configured "
            "classification threshold. The claim has been classified "
            "as higher fraud risk by the synthetic fraud-risk model."
        )

    else:

        st.success(
            "The model's predicted probability is below the configured "
            "classification threshold. The claim has been classified "
            "as lower fraud risk by the synthetic fraud-risk model."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div style="
text-align:center;
color:#64748b;
font-size:0.78rem;
padding-top:2.5rem;
line-height:1.6;
">
AutoShield Insurance Analytics • Machine Learning Demonstration
<br>
Synthetic dataset — predictions are for analytical demonstration only.
</div>
""",
    unsafe_allow_html=True
)
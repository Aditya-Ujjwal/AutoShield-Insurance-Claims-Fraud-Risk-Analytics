import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AutoShield | Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS & ENVIRONMENT
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

required_vars = {
    "DB_HOST": DB_HOST,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME
}

missing_vars = [
    key
    for key, value in required_vars.items()
    if not value
]

if missing_vars:

    st.error(
        "Missing database environment variables: "
        + ", ".join(missing_vars)
    )

    st.stop()


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=600)
def load_data():

    customers = pd.read_sql(
        "SELECT * FROM customers",
        engine
    )

    vehicles = pd.read_sql(
        "SELECT * FROM vehicles",
        engine
    )

    policies = pd.read_sql(
        "SELECT * FROM policies",
        engine
    )

    claims = pd.read_sql(
        "SELECT * FROM claims",
        engine
    )

    payments = pd.read_sql(
        "SELECT * FROM payments",
        engine
    )

    return (
        customers,
        vehicles,
        policies,
        claims,
        payments
    )


try:

    (
        customers,
        vehicles,
        policies,
        claims,
        payments
    ) = load_data()

except Exception as error:

    st.error(
        f"Unable to load data from MySQL: {error}"
    )

    st.stop()


# ============================================================
# DATA PREPARATION
# ============================================================

# Dates
policies["Start_Date"] = pd.to_datetime(
    policies["Start_Date"]
)

policies["End_Date"] = pd.to_datetime(
    policies["End_Date"]
)

vehicles["Purchase_Date"] = pd.to_datetime(
    vehicles["Purchase_Date"]
)

claims["Claim_Date"] = pd.to_datetime(
    claims["Claim_Date"]
)

payments["Payment_Date"] = pd.to_datetime(
    payments["Payment_Date"]
)


# ------------------------------------------------------------
# Correct vehicle dates for dashboard analytics
# ------------------------------------------------------------

earliest_policy = (
    policies
    .groupby("Vehicle_ID")["Start_Date"]
    .min()
    .reset_index()
    .rename(
        columns={
            "Start_Date": "Earliest_Policy_Start"
        }
    )
)

vehicles = vehicles.merge(
    earliest_policy,
    on="Vehicle_ID",
    how="left"
)

needs_correction = (
    vehicles["Purchase_Date"]
    > vehicles["Earliest_Policy_Start"]
)

proposed_purchase = (
    vehicles["Earliest_Policy_Start"]
    - pd.Timedelta(days=30)
)

proposed_manufacture = vehicles[
    "Manufacture_Year"
].copy()

manufacture_conflict = (
    proposed_purchase.dt.year
    < proposed_manufacture
)

proposed_manufacture.loc[
    manufacture_conflict
] = proposed_purchase[
    manufacture_conflict
].dt.year

vehicles.loc[
    needs_correction,
    "Purchase_Date"
] = proposed_purchase[
    needs_correction
]

vehicles.loc[
    needs_correction,
    "Manufacture_Year"
] = proposed_manufacture[
    needs_correction
]

vehicles.drop(
    columns=["Earliest_Policy_Start"],
    inplace=True
)


# ------------------------------------------------------------
# Claims missing injuries
# ------------------------------------------------------------

claims["Injuries"] = claims[
    "Injuries"
].fillna("Unknown")


# ------------------------------------------------------------
# Payment aggregation
# ------------------------------------------------------------

payment_summary = (
    payments
    .groupby("Claim_ID")
    .agg(
        Total_Paid=("Amount_Paid", "sum"),
        Payment_Count=("Payment_ID", "count"),
        Last_Payment_Date=("Payment_Date", "max")
    )
    .reset_index()
)


# ============================================================
# BUILD ANALYTICS DATASET
# ============================================================

analytics = claims.merge(
    policies[
        [
            "Policy_ID",
            "Policy_Type",
            "Coverage_Amount",
            "Premium_Amount",
            "Start_Date",
            "End_Date",
            "No_Claim_Bonus",
            "Policy_Status"
        ]
    ],
    on="Policy_ID",
    how="left"
)

analytics = analytics.merge(
    customers[
        [
            "Customer_ID",
            "Gender",
            "Age",
            "Marital_Status",
            "Occupation",
            "Annual_Income",
            "State",
            "City",
            "Driving_Experience_Years"
        ]
    ],
    on="Customer_ID",
    how="left"
)

analytics = analytics.merge(
    vehicles[
        [
            "Vehicle_ID",
            "Vehicle_Type",
            "Brand",
            "Manufacture_Year",
            "Registration_State",
            "Fuel_Type",
            "Engine_CC",
            "Vehicle_Value",
            "Purchase_Date"
        ]
    ],
    on="Vehicle_ID",
    how="left"
)

analytics = analytics.merge(
    payment_summary,
    on="Claim_ID",
    how="left"
)


# ============================================================
# DERIVED ANALYTICS FEATURES
# ============================================================

analytics["Total_Paid"] = (
    analytics["Total_Paid"]
    .fillna(0)
)

analytics["Payment_Count"] = (
    analytics["Payment_Count"]
    .fillna(0)
)

analytics["Outstanding_Amount"] = (
    analytics["Claim_Amount"]
    - analytics["Total_Paid"]
)

analytics["Payment_Coverage_Ratio"] = np.where(
    analytics["Claim_Amount"] > 0,
    analytics["Total_Paid"] /
    analytics["Claim_Amount"],
    0
)

analytics["Vehicle_Age"] = (
    analytics["Claim_Date"].dt.year
    - analytics["Manufacture_Year"]
)

analytics["Policy_Age_At_Claim"] = (
    analytics["Claim_Date"]
    - analytics["Start_Date"]
).dt.days

analytics["Claim_Damage_Ratio"] = (
    analytics["Claim_Amount"]
    / analytics["Estimated_Damage_Cost"]
)

analytics["Claim_Coverage_Ratio"] = (
    analytics["Claim_Amount"]
    / analytics["Coverage_Amount"]
)

analytics["Claim_Vehicle_Value_Ratio"] = (
    analytics["Claim_Amount"]
    / analytics["Vehicle_Value"]
)

analytics["Year"] = (
    analytics["Claim_Date"].dt.year
)

analytics["Month"] = (
    analytics["Claim_Date"].dt.month
)

analytics["Month_Name"] = (
    analytics["Claim_Date"].dt.strftime("%b")
)

analytics["Year_Month"] = (
    analytics["Claim_Date"]
    .dt.to_period("M")
    .astype(str)
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background:
        linear-gradient(
            135deg,
            #07111f 0%,
            #0b1728 50%,
            #101d31 100%
        );
}

.main .block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 2.2rem 2.5rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.40),
            rgba(14, 165, 233, 0.12)
        );
    border: 1px solid rgba(148,163,184,0.18);
    margin-bottom: 1.5rem;
    box-shadow:
        0 20px 50px rgba(0,0,0,0.25);
}

.hero-icon {
    font-size: 2.8rem;
}

.hero-title {
    color: #f8fafc;
    font-size: 2.55rem;
    font-weight: 850;
    letter-spacing: -1px;
    margin-top: 0.4rem;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 0.98rem;
    line-height: 1.6;
    max-width: 900px;
}

.section-title {
    color: #f8fafc;
    font-size: 1.35rem;
    font-weight: 750;
    margin-top: 1rem;
}

.kpi-card {
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 18px;
    padding: 1.1rem;
    min-height: 125px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.13);
}

.kpi-label {
    color: #94a3b8;
    font-size: 0.82rem;
}

.kpi-value {
    color: #f8fafc;
    font-size: 1.65rem;
    font-weight: 800;
    margin-top: 0.35rem;
}

.kpi-subtitle {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 0.35rem;
}

.info-box {
    background: rgba(30,41,59,0.65);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    color: #cbd5e1;
    line-height: 1.6;
}

.sidebar-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-text {
    color: #94a3b8;
    font-size: 0.84rem;
    line-height: 1.55;
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
        '<div class="sidebar-title">📊 AutoShield Analytics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="sidebar-text">
Interactive insurance claims, policy, customer,
vehicle and payment analytics.
</div>
""",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Global Filters")

    min_date = analytics["Claim_Date"].min().date()
    max_date = analytics["Claim_Date"].max().date()

    date_range = st.date_input(
        "Claim Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    selected_states = st.multiselect(
        "Customer State",
        sorted(
            analytics["State"].dropna().unique()
        )
    )

    selected_policy_types = st.multiselect(
        "Policy Type",
        sorted(
            analytics["Policy_Type"]
            .dropna()
            .unique()
        )
    )

    selected_claim_status = st.multiselect(
        "Claim Status",
        sorted(
            analytics["Claim_Status"]
            .dropna()
            .unique()
        )
    )

    selected_accident_types = st.multiselect(
        "Accident Type",
        sorted(
            analytics["Accident_Type"]
            .dropna()
            .unique()
        )
    )

    selected_vehicle_types = st.multiselect(
        "Vehicle Type",
        sorted(
            analytics["Vehicle_Type"]
            .dropna()
            .unique()
        )
    )

    fraud_filter = st.selectbox(
        "Fraud Suspected",
        [
            "All",
            "Yes",
            "No"
        ]
    )

    st.divider()

    st.markdown("### Dashboard Scope")

    st.markdown(
        """
<div class="sidebar-text">
• Claims & fraud trends<br>
• Policy performance<br>
• Customer & vehicle profile<br>
• Payment & settlement analysis
</div>
""",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        """
<div class="sidebar-text">
<b>Data Note:</b> Dashboard metrics use the original
insurance dataset. Fraud labels are synthetic and are
presented for analytical demonstration.
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = analytics.copy()


# Date range
if len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    ) + pd.Timedelta(days=1)

    filtered = filtered[
        (
            filtered["Claim_Date"] >= start_date
        )
        &
        (
            filtered["Claim_Date"] < end_date
        )
    ]


if selected_states:

    filtered = filtered[
        filtered["State"].isin(
            selected_states
        )
    ]


if selected_policy_types:

    filtered = filtered[
        filtered["Policy_Type"].isin(
            selected_policy_types
        )
    ]


if selected_claim_status:

    filtered = filtered[
        filtered["Claim_Status"].isin(
            selected_claim_status
        )
    ]


if selected_accident_types:

    filtered = filtered[
        filtered["Accident_Type"].isin(
            selected_accident_types
        )
    ]


if selected_vehicle_types:

    filtered = filtered[
        filtered["Vehicle_Type"].isin(
            selected_vehicle_types
        )
    ]


if fraud_filter != "All":

    filtered = filtered[
        filtered["Fraud_Suspected"]
        == fraud_filter
    ]


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">
<div class="hero-icon">📊</div>
<div class="hero-title">AutoShield Insurance Analytics</div>
<div class="hero-subtitle">
Interactive analytics for insurance claims, fraud indicators,
policies, customers, vehicles, settlements and payments.
Use the filters in the sidebar to explore the portfolio dynamically.
</div>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# DATASET STATUS
# ============================================================

st.markdown(
    f"""
<div class="info-box">
Showing <b>{len(filtered):,}</b> claims out of
<b>{len(analytics):,}</b> total claims based on the current filters.
</div>
""",
    unsafe_allow_html=True
)

st.write("")


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_customers = (
    filtered["Customer_ID"].nunique()
)

total_claims = len(filtered)

total_claim_amount = (
    filtered["Claim_Amount"].sum()
)

total_paid = (
    filtered["Total_Paid"].sum()
)

avg_claim = (
    filtered["Claim_Amount"].mean()
    if total_claims > 0
    else 0
)

avg_settlement = (
    filtered["Settlement_Days"].mean()
    if total_claims > 0
    else 0
)

fraud_claims = (
    filtered["Fraud_Suspected"]
    .eq("Yes")
    .sum()
)

fraud_rate = (
    fraud_claims / total_claims * 100
    if total_claims > 0
    else 0
)

unpaid_claims = (
    filtered["Payment_Count"] == 0
).sum()

active_policies = (
    filtered["Policy_Status"]
    .eq("Active")
    .sum()
)


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)

kpi_data_1 = [
    (
        "Total Claims",
        f"{total_claims:,}",
        "Filtered claim records"
    ),
    (
        "Total Claim Value",
        f"₹{total_claim_amount / 1e7:.2f} Cr",
        "Claimed amount"
    ),
    (
        "Total Paid",
        f"₹{total_paid / 1e7:.2f} Cr",
        "Payment records"
    ),
    (
        "Average Claim",
        f"₹{avg_claim:,.0f}",
        "Average claim amount"
    )
]

for col, (label, value, subtitle) in zip(
    [k1, k2, k3, k4],
    kpi_data_1
):

    with col:

        st.markdown(
            f"""
<div class="kpi-card">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-subtitle">{subtitle}</div>
</div>
""",
            unsafe_allow_html=True
        )


st.write("")

k5, k6, k7, k8 = st.columns(4)

kpi_data_2 = [
    (
        "Fraud Suspected",
        f"{fraud_rate:.1f}%",
        f"{fraud_claims:,} claims"
    ),
    (
        "Avg Settlement",
        f"{avg_settlement:.0f} days",
        "Average settlement time"
    ),
    (
        "Unpaid Claims",
        f"{unpaid_claims:,}",
        "Claims without payment"
    ),
    (
        "Active Policies",
        f"{active_policies:,}",
        "Within filtered claims"
    )
]

for col, (label, value, subtitle) in zip(
    [k5, k6, k7, k8],
    kpi_data_2
):

    with col:

        st.markdown(
            f"""
<div class="kpi-card">
<div class="kpi-label">{label}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-subtitle">{subtitle}</div>
</div>
""",
            unsafe_allow_html=True
        )


st.write("")


# ============================================================
# DASHBOARD TABS
# ============================================================

tab_overview, tab_claims, tab_policy, tab_customer, tab_payment = (
    st.tabs(
        [
            "📈 Overview",
            "🚨 Claims & Fraud",
            "📄 Policies",
            "👥 Customers & Vehicles",
            "💳 Payments"
        ]
    )
)


# ============================================================
# OVERVIEW TAB
# ============================================================

with tab_overview:

    st.markdown(
        '<div class="section-title">Claim Trend</div>',
        unsafe_allow_html=True
    )

    monthly_claims = (
        filtered
        .groupby("Year_Month")
        .agg(
            Claims=("Claim_ID", "count"),
            Claim_Amount=("Claim_Amount", "sum")
        )
        .reset_index()
    )

    fig = px.line(
        monthly_claims,
        x="Year_Month",
        y="Claims",
        markers=True,
        title="Monthly Claim Volume"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title="Month",
        yaxis_title="Claims"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    col1, col2 = st.columns(2)

    with col1:

        accident_summary = (
            filtered
            .groupby("Accident_Type")
            .agg(
                Claims=("Claim_ID", "count"),
                Claim_Value=("Claim_Amount", "sum")
            )
            .reset_index()
            .sort_values(
                "Claim_Value",
                ascending=False
            )
        )

        fig = px.bar(
            accident_summary,
            x="Accident_Type",
            y="Claim_Value",
            title="Claim Value by Accident Type",
            text_auto=".2s"
        )

        fig.update_layout(
            template="plotly_dark",
            height=400,
            yaxis_title="Claim Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        policy_summary = (
            filtered
            .groupby("Policy_Type")
            .agg(
                Claims=("Claim_ID", "count"),
                Avg_Claim=("Claim_Amount", "mean"),
                Coverage=("Coverage_Amount", "mean")
            )
            .reset_index()
        )

        fig = px.bar(
            policy_summary,
            x="Policy_Type",
            y="Avg_Claim",
            title="Average Claim by Policy Type",
            text_auto=".2s"
        )

        fig.update_layout(
            template="plotly_dark",
            height=400,
            yaxis_title="Average Claim Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# CLAIMS & FRAUD TAB
# ============================================================

with tab_claims:

    st.markdown(
        '<div class="section-title">Claims & Fraud Analysis</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        fraud_by_type = (
            filtered
            .groupby("Accident_Type")[
                "Fraud_Suspected"
            ]
            .apply(
                lambda x:
                (x == "Yes").mean() * 100
            )
            .reset_index(
                name="Fraud_Rate"
            )
            .sort_values(
                "Fraud_Rate",
                ascending=False
            )
        )

        fig = px.bar(
            fraud_by_type,
            x="Accident_Type",
            y="Fraud_Rate",
            title="Suspected Fraud Rate by Accident Type",
            text_auto=".1f"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            yaxis_title="Fraud Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fraud_weather = (
            filtered
            .groupby("Weather_Condition")[
                "Fraud_Suspected"
            ]
            .apply(
                lambda x:
                (x == "Yes").mean() * 100
            )
            .reset_index(
                name="Fraud_Rate"
            )
            .sort_values(
                "Fraud_Rate",
                ascending=False
            )
        )

        fig = px.bar(
            fraud_weather,
            x="Weather_Condition",
            y="Fraud_Rate",
            title="Suspected Fraud Rate by Weather",
            text_auto=".1f"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            yaxis_title="Fraud Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    col3, col4 = st.columns(2)

    with col3:

        status_summary = (
            filtered
            .groupby("Claim_Status")
            .agg(
                Claims=("Claim_ID", "count"),
                Claim_Value=("Claim_Amount", "sum")
            )
            .reset_index()
        )

        fig = px.pie(
            status_summary,
            names="Claim_Status",
            values="Claims",
            title="Claim Status Distribution",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col4:

        injuries_summary = (
            filtered
            .groupby("Injuries")
            .size()
            .reset_index(
                name="Claims"
            )
        )

        fig = px.pie(
            injuries_summary,
            names="Injuries",
            values="Claims",
            title="Injury Severity Distribution",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.markdown(
        '<div class="section-title">Claim Amount Distribution</div>',
        unsafe_allow_html=True
    )

    fig = px.histogram(
        filtered,
        x="Claim_Amount",
        color="Fraud_Suspected",
        nbins=30,
        title="Claim Amount Distribution by Suspected Fraud"
    )

    fig.update_layout(
        template="plotly_dark",
        height=430,
        xaxis_title="Claim Amount",
        yaxis_title="Number of Claims"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# POLICY TAB
# ============================================================

with tab_policy:

    st.markdown(
        '<div class="section-title">Policy Analytics</div>',
        unsafe_allow_html=True
    )

    policy_summary = (
        policies
        .groupby("Policy_Type")
        .agg(
            Policies=("Policy_ID", "count"),
            Avg_Premium=("Premium_Amount", "mean"),
            Avg_Coverage=("Coverage_Amount", "mean"),
            Avg_NCB=("No_Claim_Bonus", "mean")
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            policy_summary,
            x="Policy_Type",
            y=[
                "Avg_Premium",
                "Avg_Coverage"
            ],
            barmode="group",
            title="Average Premium vs Coverage"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            yaxis_title="Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        policy_status = (
            policies[
                "Policy_Status"
            ]
            .value_counts()
            .reset_index()
        )

        policy_status.columns = [
            "Policy_Status",
            "Policies"
        ]

        fig = px.pie(
            policy_status,
            names="Policy_Status",
            values="Policies",
            title="Policy Status Distribution",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.dataframe(
        policy_summary.style.format(
            {
                "Avg_Premium": "₹{:,.0f}",
                "Avg_Coverage": "₹{:,.0f}",
                "Avg_NCB": "{:.1f}%"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CUSTOMER & VEHICLE TAB
# ============================================================

with tab_customer:

    st.markdown(
        '<div class="section-title">Customer & Vehicle Profile</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        occupation_summary = (
            filtered
            .groupby("Occupation")
            .agg(
                Customers=(
                    "Customer_ID",
                    "nunique"
                ),
                Claims=(
                    "Claim_ID",
                    "count"
                ),
                Claim_Value=(
                    "Claim_Amount",
                    "sum"
                )
            )
            .reset_index()
        )

        fig = px.bar(
            occupation_summary,
            x="Occupation",
            y="Claims",
            title="Claims by Customer Occupation",
            text_auto=True
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        vehicle_summary = (
            filtered
            .groupby("Vehicle_Type")
            .agg(
                Claims=("Claim_ID", "count"),
                Claim_Value=("Claim_Amount", "sum"),
                Avg_Claim=("Claim_Amount", "mean")
            )
            .reset_index()
        )

        fig = px.bar(
            vehicle_summary,
            x="Vehicle_Type",
            y="Claim_Value",
            title="Claim Value by Vehicle Type",
            text_auto=".2s"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    col3, col4 = st.columns(2)

    with col3:

        state_summary = (
            filtered
            .groupby("State")
            .agg(
                Claims=("Claim_ID", "count"),
                Claim_Value=("Claim_Amount", "sum")
            )
            .reset_index()
            .sort_values(
                "Claim_Value",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            state_summary,
            x="Claim_Value",
            y="State",
            orientation="h",
            title="Top States by Claim Value"
        )

        fig.update_layout(
            template="plotly_dark",
            height=450,
            xaxis_title="Claim Amount"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col4:

        fuel_summary = (
            filtered
            .groupby("Fuel_Type")
            .size()
            .reset_index(
                name="Claims"
            )
        )

        fig = px.pie(
            fuel_summary,
            names="Fuel_Type",
            values="Claims",
            title="Claims by Fuel Type",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAYMENTS TAB
# ============================================================

with tab_payment:

    st.markdown(
        '<div class="section-title">Payment & Settlement Analytics</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        payment_status = (
            payments
            .groupby("Payment_Status")
            .agg(
                Payments=("Payment_ID", "count"),
                Amount=("Amount_Paid", "sum")
            )
            .reset_index()
        )

        fig = px.pie(
            payment_status,
            names="Payment_Status",
            values="Amount",
            title="Payment Amount by Status",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        payment_mode = (
            payments
            .groupby("Payment_Mode")
            .agg(
                Payments=("Payment_ID", "count"),
                Amount=("Amount_Paid", "sum")
            )
            .reset_index()
        )

        fig = px.bar(
            payment_mode,
            x="Payment_Mode",
            y="Amount",
            title="Payments by Payment Mode",
            text_auto=".2s"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    payment_monthly = (
        payments.assign(
            Year_Month=payments["Payment_Date"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("Year_Month")
        .agg(
            Payments=("Payment_ID", "count"),
            Amount=("Amount_Paid", "sum")
        )
        .reset_index()
    )

    fig = px.line(
        payment_monthly,
        x="Year_Month",
        y="Amount",
        markers=True,
        title="Monthly Payment Amount"
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        yaxis_title="Amount Paid"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    settlement = filtered[
        [
            "Claim_ID",
            "Claim_Amount",
            "Total_Paid",
            "Outstanding_Amount",
            "Payment_Coverage_Ratio"
        ]
    ].copy()

    settlement = settlement.sort_values(
        "Outstanding_Amount",
        ascending=False
    )

    st.markdown(
        '<div class="section-title">Outstanding Claim Amount</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        settlement.head(20).style.format(
            {
                "Claim_Amount": "₹{:,.0f}",
                "Total_Paid": "₹{:,.0f}",
                "Outstanding_Amount": "₹{:,.0f}",
                "Payment_Coverage_Ratio": "{:.1%}"
            }
        ),
        use_container_width=True,
        hide_index=True
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
AutoShield Insurance Analytics
<br>
MySQL • Python • Streamlit • Plotly
<br>
Synthetic insurance dataset — analytical demonstration only.
</div>
""",
    unsafe_allow_html=True
)
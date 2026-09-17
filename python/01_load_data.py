import pandas as pd
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Project directories
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

required_env_vars = [
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME"
]

missing_vars = [
    var for var in required_env_vars
    if not os.getenv(var)
]

if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}\n"
        f"Please check your .env file."
    )

# ============================================================
# 2. MYSQL CONNECTION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


# ============================================================
# 3. SOURCE FILES
# ============================================================

FILES = {
    "customers": "Customers.xlsx",
    "vehicles": "Vehicles.xlsx",
    "policies": "Policies.xlsx",
    "claims": "Claims.xlsx",
    "payments": "Payments.xlsx"
}


# ============================================================
# 4. LOAD EXCEL FILES
# ============================================================

def load_excel_files():

    dataframes = {}

    for table_name, filename in FILES.items():

        file_path = DATA_DIR / filename

        print(f"Reading {filename}...")

        df = pd.read_excel(file_path)

        dataframes[table_name] = df

        print(f"  → {len(df):,} rows loaded")

    return dataframes


# ============================================================
# 5. CONNECT TO MYSQL
# ============================================================

def create_connection():

    connection = mysql.connector.connect(**DB_CONFIG)

    print("\nConnected to MySQL successfully.")

    return connection


# ============================================================
# 6. INSERT DATA INTO MYSQL
# ============================================================

def insert_data(connection, dataframes):

    cursor = connection.cursor()

    insert_queries = {

        "customers": """
            INSERT INTO customers (
                Customer_ID,
                Customer_Name,
                Gender,
                Age,
                Marital_Status,
                Occupation,
                Annual_Income,
                City,
                State,
                Address,
                Contact_Number,
                Email,
                Driving_Experience_Years
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,

        "vehicles": """
            INSERT INTO vehicles (
                Vehicle_ID,
                Customer_ID,
                Vehicle_Type,
                Brand,
                Model,
                Manufacture_Year,
                Registration_State,
                Fuel_Type,
                Engine_CC,
                Vehicle_Value,
                Purchase_Date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,

        "policies": """
            INSERT INTO policies (
                Policy_ID,
                Customer_ID,
                Vehicle_ID,
                Policy_Type,
                Coverage_Amount,
                Premium_Amount,
                Start_Date,
                End_Date,
                No_Claim_Bonus,
                Policy_Status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,

        "claims": """
            INSERT INTO claims (
                Claim_ID,
                Policy_ID,
                Vehicle_ID,
                Customer_ID,
                Claim_Date,
                Accident_City,
                Accident_Type,
                Weather_Condition,
                Police_Report_Filed,
                Injuries,
                Estimated_Damage_Cost,
                Claim_Amount,
                Fraud_Suspected,
                Claim_Status,
                Settlement_Days
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,

        "payments": """
            INSERT INTO payments (
                Payment_ID,
                Claim_ID,
                Payment_Date,
                Payment_Mode,
                Amount_Paid,
                Payment_Status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
    }

    # Order matters because of foreign keys.
    load_order = [
        "customers",
        "vehicles",
        "policies",
        "claims",
        "payments"
    ]

    for table_name in load_order:

        df = dataframes[table_name]

        print(f"\nLoading {table_name}...")

        query = insert_queries[table_name]

        # Convert DataFrame rows into tuples.
        rows = [
            tuple(row)
            for row in df.itertuples(index=False, name=None)
        ]

        cursor.executemany(query, rows)

        print(f"  → {cursor.rowcount:,} rows inserted")

    connection.commit()

    cursor.close()

    print("\nAll data committed successfully.")


# ============================================================
# 7. MAIN
# ============================================================

def main():

    print("=" * 60)
    print("AUTOSHIELD INSURANCE ANALYTICS")
    print("RAW DATA LOADER")
    print("=" * 60)

    dataframes = load_excel_files()

    connection = create_connection()

    try:

        insert_data(connection, dataframes)

    except Exception as error:

        connection.rollback()

        print("\nERROR:")
        print(error)

        print("\nTransaction rolled back.")

        raise

    finally:

        connection.close()

        print("\nMySQL connection closed.")


if __name__ == "__main__":
    main()
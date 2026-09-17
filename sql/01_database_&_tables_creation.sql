/* ============================================================================
   AUTOSHIELD INSURANCE ANALYTICS
   ----------------------------------------------------------------------------
   File        : 02_create_tables.sql
   Project     : AutoShield — Insurance Claims & Fraud Risk Analytics
   Database    : autoshield_insurance

   Purpose:
   This script creates the relational database structure used by the
   AutoShield Insurance Analytics project.

   The database consists of five core entities:

       1. customers  → Policyholders
       2. vehicles   → Insured vehicles
       3. policies   → Insurance policies
       4. claims     → Insurance claims
       5. payments   → Claim payment transactions

   Database Design:
       Customer
          │
          ├── Vehicles
          │
          └── Policies
                 │
                 └── Claims
                        │
                        └── Payments

   Design Features:
       - Primary keys for unique record identification
       - Foreign keys for referential integrity
       - NOT NULL constraints for mandatory attributes
       - CHECK constraints for basic data validation
       - Indexes on frequently joined and filtered columns
       - UTF-8 support using utf8mb4

   Important:
       - This script recreates the database from scratch.
       - Running it will DROP the existing autoshield_insurance database.
       - Run only when a fresh database structure is required.

   Author      : Aditya Ujjwal
   Project     : AutoShield Insurance Analytics
   ============================================================================ */


/* ============================================================================
   SECTION 01 — DATABASE INITIALIZATION
   ----------------------------------------------------------------------------
   Objective:
   Remove any existing AutoShield database and create a fresh database
   using UTF-8 compatible character encoding.
   ============================================================================ */

-- Remove the existing database if it already exists.
-- WARNING: This permanently removes all tables and data inside it.
DROP DATABASE IF EXISTS autoshield_insurance;


-- Create a new database using utf8mb4 for broad Unicode support.
CREATE DATABASE autoshield_insurance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;


-- Select the newly created database for subsequent table creation.
USE autoshield_insurance;


/* ============================================================================
   SECTION 02 — CUSTOMERS TABLE
   ----------------------------------------------------------------------------
   Purpose:
   Stores the master information for each insurance customer.

   Primary Key:
       Customer_ID

   Key attributes:
       - Personal information
       - Demographic information
       - Financial information
       - Contact information
       - Driving experience

   Relationship:
       One customer can own multiple vehicles and hold multiple policies.
   ============================================================================ */

CREATE TABLE customers (

    -- Unique identifier for each customer.
    Customer_ID VARCHAR(20) PRIMARY KEY,

    -- Customer's full name.
    Customer_Name VARCHAR(100) NOT NULL,

    -- Customer gender.
    Gender VARCHAR(20) NOT NULL,

    -- Customer age in years.
    Age TINYINT UNSIGNED NOT NULL,

    -- Marital status of the customer.
    Marital_Status VARCHAR(20) NOT NULL,

    -- Customer occupation.
    Occupation VARCHAR(50) NOT NULL,

    -- Annual income of the customer.
    Annual_Income DECIMAL(15,2) NOT NULL,

    -- City where the customer resides.
    City VARCHAR(50) NOT NULL,

    -- State where the customer resides.
    State VARCHAR(50) NOT NULL,

    -- Residential address.
    Address VARCHAR(255) NOT NULL,

    -- Contact phone number.
    Contact_Number VARCHAR(20) NOT NULL,

    -- Customer email address.
    Email VARCHAR(150) NOT NULL,

    -- Number of years of driving experience.
    Driving_Experience_Years TINYINT UNSIGNED NOT NULL,


    /* ------------------------------------------------------------------------
       Customer Validation Constraints
       ------------------------------------------------------------------------ */

    -- Customers must be between 18 and 100 years old.
    CONSTRAINT chk_customer_age
        CHECK (Age BETWEEN 18 AND 100),

    -- Annual income cannot be negative.
    CONSTRAINT chk_customer_income
        CHECK (Annual_Income >= 0),

    -- Driving experience cannot be negative.
    CONSTRAINT chk_driving_experience
        CHECK (Driving_Experience_Years >= 0)
);


/* ============================================================================
   SECTION 03 — VEHICLES TABLE
   ----------------------------------------------------------------------------
   Purpose:
   Stores vehicle information associated with customers.

   Primary Key:
       Vehicle_ID

   Foreign Key:
       Customer_ID → customers.Customer_ID

   Relationship:
       One customer can own multiple vehicles.
   ============================================================================ */

CREATE TABLE vehicles (

    -- Unique identifier for each vehicle.
    Vehicle_ID VARCHAR(20) PRIMARY KEY,

    -- Customer who owns the vehicle.
    Customer_ID VARCHAR(20) NOT NULL,

    -- General vehicle classification.
    Vehicle_Type VARCHAR(30) NOT NULL,

    -- Vehicle manufacturer/brand.
    Brand VARCHAR(50) NOT NULL,

    -- Vehicle model.
    Model VARCHAR(50) NOT NULL,

    -- Year in which the vehicle was manufactured.
    Manufacture_Year SMALLINT UNSIGNED NOT NULL,

    -- State in which the vehicle is registered.
    Registration_State VARCHAR(50) NOT NULL,

    -- Fuel type used by the vehicle.
    Fuel_Type VARCHAR(30) NOT NULL,

    -- Engine displacement in cubic centimeters.
    Engine_CC SMALLINT UNSIGNED NOT NULL,

    -- Estimated monetary value of the vehicle.
    Vehicle_Value DECIMAL(15,2) NOT NULL,

    -- Date on which the vehicle was purchased.
    Purchase_Date DATE NOT NULL,


    /* ------------------------------------------------------------------------
       Relationship Constraints
       ------------------------------------------------------------------------ */

    -- Connect each vehicle to its owner in the customers table.
    CONSTRAINT fk_vehicle_customer
        FOREIGN KEY (Customer_ID)
        REFERENCES customers(Customer_ID),


    /* ------------------------------------------------------------------------
       Vehicle Validation Constraints
       ------------------------------------------------------------------------ */

    -- Prevent unrealistic historical manufacture years.
    CONSTRAINT chk_vehicle_year
        CHECK (Manufacture_Year >= 1900),

    -- Engine capacity must be greater than zero.
    CONSTRAINT chk_engine_cc
        CHECK (Engine_CC > 0),

    -- Vehicle value cannot be negative.
    CONSTRAINT chk_vehicle_value
        CHECK (Vehicle_Value >= 0),


    /* ------------------------------------------------------------------------
       Vehicle Indexes
       ------------------------------------------------------------------------ */

    -- Speeds up customer → vehicle joins and lookups.
    INDEX idx_vehicles_customer (Customer_ID),

    -- Speeds up filtering and grouping by vehicle brand.
    INDEX idx_vehicles_brand (Brand)
);


/* ============================================================================
   SECTION 04 — POLICIES TABLE
   ----------------------------------------------------------------------------
   Purpose:
   Stores insurance policy information linking customers and vehicles.

   Primary Key:
       Policy_ID

   Foreign Keys:
       Customer_ID → customers.Customer_ID
       Vehicle_ID  → vehicles.Vehicle_ID

   Relationship:
       A policy belongs to a customer and covers a vehicle.
   ============================================================================ */

CREATE TABLE policies (

    -- Unique identifier for each insurance policy.
    Policy_ID VARCHAR(20) PRIMARY KEY,

    -- Customer who owns the policy.
    Customer_ID VARCHAR(20) NOT NULL,

    -- Vehicle covered by the policy.
    Vehicle_ID VARCHAR(20) NOT NULL,

    -- Type of insurance policy.
    Policy_Type VARCHAR(40) NOT NULL,

    -- Maximum insured coverage amount.
    Coverage_Amount DECIMAL(15,2) NOT NULL,

    -- Premium charged for the policy.
    Premium_Amount DECIMAL(15,2) NOT NULL,

    -- Date on which the policy becomes active.
    Start_Date DATE NOT NULL,

    -- Date on which the policy expires.
    End_Date DATE NOT NULL,

    -- No-Claim Bonus percentage.
    No_Claim_Bonus TINYINT UNSIGNED NOT NULL,

    -- Current policy status.
    Policy_Status VARCHAR(30) NOT NULL,


    /* ------------------------------------------------------------------------
       Relationship Constraints
       ------------------------------------------------------------------------ */

    -- Connect the policy to its customer.
    CONSTRAINT fk_policy_customer
        FOREIGN KEY (Customer_ID)
        REFERENCES customers(Customer_ID),

    -- Connect the policy to the insured vehicle.
    CONSTRAINT fk_policy_vehicle
        FOREIGN KEY (Vehicle_ID)
        REFERENCES vehicles(Vehicle_ID),


    /* ------------------------------------------------------------------------
       Policy Validation Constraints
       ------------------------------------------------------------------------ */

    -- Policy expiration cannot occur before policy start.
    CONSTRAINT chk_policy_dates
        CHECK (End_Date >= Start_Date),

    -- Coverage amount cannot be negative.
    CONSTRAINT chk_coverage
        CHECK (Coverage_Amount >= 0),

    -- Premium cannot be negative.
    CONSTRAINT chk_premium
        CHECK (Premium_Amount >= 0),

    -- No-Claim Bonus must be between 0% and 100%.
    CONSTRAINT chk_ncb
        CHECK (No_Claim_Bonus BETWEEN 0 AND 100),


    /* ------------------------------------------------------------------------
       Policy Indexes
       ------------------------------------------------------------------------ */

    -- Speeds up customer → policy queries.
    INDEX idx_policies_customer (Customer_ID),

    -- Speeds up vehicle → policy queries.
    INDEX idx_policies_vehicle (Vehicle_ID),

    -- Speeds up filtering by policy status.
    INDEX idx_policies_status (Policy_Status)
);


/* ============================================================================
   SECTION 05 — CLAIMS TABLE
   ----------------------------------------------------------------------------
   Purpose:
   Stores insurance claim records associated with policies, vehicles,
   and customers.

   Primary Key:
       Claim_ID

   Foreign Keys:
       Policy_ID  → policies.Policy_ID
       Vehicle_ID → vehicles.Vehicle_ID
       Customer_ID → customers.Customer_ID

   This is the central transactional table for the project's claims
   and fraud analytics.
   ============================================================================ */

CREATE TABLE claims (

    -- Unique identifier for each claim.
    Claim_ID VARCHAR(20) PRIMARY KEY,

    -- Policy under which the claim was submitted.
    Policy_ID VARCHAR(20) NOT NULL,

    -- Vehicle involved in the claim.
    Vehicle_ID VARCHAR(20) NOT NULL,

    -- Customer associated with the claim.
    Customer_ID VARCHAR(20) NOT NULL,

    -- Date on which the claim occurred or was submitted.
    Claim_Date DATE NOT NULL,

    -- City where the accident occurred.
    Accident_City VARCHAR(50) NOT NULL,

    -- Type/category of accident.
    Accident_Type VARCHAR(50) NOT NULL,

    -- Weather conditions during the incident.
    Weather_Condition VARCHAR(30) NOT NULL,

    -- Indicates whether a police report was filed.
    Police_Report_Filed VARCHAR(10) NOT NULL,

    -- Injury severity information.
    -- NULL is permitted because injury information may not be recorded.
    Injuries VARCHAR(30) NULL,

    -- Estimated repair/damage cost.
    Estimated_Damage_Cost DECIMAL(15,2) NOT NULL,

    -- Amount claimed by the customer.
    Claim_Amount DECIMAL(15,2) NOT NULL,

    -- Original fraud-suspicion indicator from the dataset.
    Fraud_Suspected VARCHAR(10) NOT NULL,

    -- Current processing status of the claim.
    Claim_Status VARCHAR(40) NOT NULL,

    -- Number of days associated with claim settlement.
    Settlement_Days SMALLINT UNSIGNED NOT NULL,


    /* ------------------------------------------------------------------------
       Relationship Constraints
       ------------------------------------------------------------------------ */

    -- Link the claim to its insurance policy.
    CONSTRAINT fk_claim_policy
        FOREIGN KEY (Policy_ID)
        REFERENCES policies(Policy_ID),

    -- Link the claim to its vehicle.
    CONSTRAINT fk_claim_vehicle
        FOREIGN KEY (Vehicle_ID)
        REFERENCES vehicles(Vehicle_ID),

    -- Link the claim to its customer.
    CONSTRAINT fk_claim_customer
        FOREIGN KEY (Customer_ID)
        REFERENCES customers(Customer_ID),


    /* ------------------------------------------------------------------------
       Claim Validation Constraints
       ------------------------------------------------------------------------ */

    -- Estimated damage cannot be negative.
    CONSTRAINT chk_damage
        CHECK (Estimated_Damage_Cost >= 0),

    -- Claim amount cannot be negative.
    CONSTRAINT chk_claim_amount
        CHECK (Claim_Amount >= 0),

    -- Settlement duration cannot be negative.
    CONSTRAINT chk_settlement_days
        CHECK (Settlement_Days >= 0),


    /* ------------------------------------------------------------------------
       Claim Indexes
       ------------------------------------------------------------------------ */

    -- Speeds up policy → claim queries.
    INDEX idx_claims_policy (Policy_ID),

    -- Speeds up vehicle → claim queries.
    INDEX idx_claims_vehicle (Vehicle_ID),

    -- Speeds up customer → claim queries.
    INDEX idx_claims_customer (Customer_ID),

    -- Speeds up date-based claim analysis.
    INDEX idx_claims_date (Claim_Date),

    -- Speeds up claim-status filtering.
    INDEX idx_claims_status (Claim_Status),

    -- Speeds up fraud-related filtering and analysis.
    INDEX idx_claims_fraud (Fraud_Suspected)
);


/* ============================================================================
   SECTION 06 — PAYMENTS TABLE
   ----------------------------------------------------------------------------
   Purpose:
   Stores payment transactions associated with insurance claims.

   Primary Key:
       Payment_ID

   Foreign Key:
       Claim_ID → claims.Claim_ID

   Relationship:
       A claim can have one or multiple associated payment records.
   ============================================================================ */

CREATE TABLE payments (

    -- Unique identifier for each payment transaction.
    Payment_ID VARCHAR(20) PRIMARY KEY,

    -- Claim associated with the payment.
    Claim_ID VARCHAR(20) NOT NULL,

    -- Date on which the payment was made.
    Payment_Date DATE NOT NULL,

    -- Method used to make the payment.
    Payment_Mode VARCHAR(40) NOT NULL,

    -- Amount paid toward the claim.
    Amount_Paid DECIMAL(15,2) NOT NULL,

    -- Current payment status.
    Payment_Status VARCHAR(30) NOT NULL,


    /* ------------------------------------------------------------------------
       Relationship Constraints
       ------------------------------------------------------------------------ */

    -- Link each payment to its associated claim.
    CONSTRAINT fk_payment_claim
        FOREIGN KEY (Claim_ID)
        REFERENCES claims(Claim_ID),


    /* ------------------------------------------------------------------------
       Payment Validation Constraints
       ------------------------------------------------------------------------ */

    -- Payment amount cannot be negative.
    CONSTRAINT chk_payment_amount
        CHECK (Amount_Paid >= 0),


    /* ------------------------------------------------------------------------
       Payment Indexes
       ------------------------------------------------------------------------ */

    -- Speeds up claim → payment lookups.
    INDEX idx_payments_claim (Claim_ID),

    -- Speeds up time-based payment analysis.
    INDEX idx_payments_date (Payment_Date),

    -- Speeds up filtering by payment status.
    INDEX idx_payments_status (Payment_Status)
);


/* ============================================================================
   SECTION 07 — BASIC POST-CREATION CHECK
   ----------------------------------------------------------------------------
   Objective:
   Confirm that the claims table was created successfully and can be
   queried after the database structure has been initialized.
   ============================================================================ */

SELECT *
FROM claims;
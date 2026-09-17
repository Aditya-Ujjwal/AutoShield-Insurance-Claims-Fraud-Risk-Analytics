/* ============================================================================
   AUTOShield INSURANCE ANALYTICS
   ----------------------------------------------------------------------------
   File        : 02_data_audit.sql
   Project     : AutoShield — Insurance Claims & Fraud Risk Analytics
   Database    : autoshield_insurance

   Purpose:
   This script performs a comprehensive read-only audit of the AutoShield
   insurance database.

   Audit areas covered:
       1. Database and table structure
       2. Row counts and sample records
       3. NULL / missing-value analysis
       4. Duplicate primary-key checks
       5. Categorical-value profiling
       6. Numerical range and validity checks
       7. Date consistency checks
       8. Referential-integrity validation
       9. Cross-table business-rule validation
      10. Claim and payment analysis
      11. Fraud and policy summaries
      12. Final database-quality summary

   Important:
   - This script is READ-ONLY.
   - No INSERT, UPDATE, DELETE, ALTER, or DROP statements are performed.
   - The audit is conducted against the raw data loaded into MySQL.
   - Data cleaning and transformations are handled separately in Python.

   Author      : Aditya Ujjwal
   Project     : AutoShield Insurance Analytics
   ============================================================================ */


/* ============================================================================
   SECTION 01 — SELECT PROJECT DATABASE
   ============================================================================ */

USE autoshield_insurance;


/* ============================================================================
   SECTION 02 — DATABASE & TABLE OVERVIEW
   ----------------------------------------------------------------------------
   Objective:
   Confirm that the expected database and tables are available and inspect
   approximate table sizes.
   ============================================================================ */

-- Display the number of rows reported by INFORMATION_SCHEMA for each table.
-- Note: TABLE_ROWS may be an estimate for some MySQL storage engines.
SELECT
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'autoshield_insurance'
ORDER BY TABLE_NAME;


/* ============================================================================
   SECTION 03 — TABLE STRUCTURE
   ----------------------------------------------------------------------------
   Objective:
   Inspect the columns, data types, NULL constraints, keys, and defaults
   of all core project tables.
   ============================================================================ */

-- Customer table structure.
DESCRIBE customers;

-- Vehicle table structure.
DESCRIBE vehicles;

-- Policy table structure.
DESCRIBE policies;

-- Claims table structure.
DESCRIBE claims;

-- Payments table structure.
DESCRIBE payments;


/* ============================================================================
   SECTION 04 — RAW DATA SAMPLE
   ----------------------------------------------------------------------------
   Objective:
   Review a small sample of records from each table before performing
   detailed quality checks.
   ============================================================================ */

-- Sample customer records.
SELECT * FROM customers LIMIT 10;

-- Sample vehicle records.
SELECT * FROM vehicles LIMIT 10;

-- Sample policy records.
SELECT * FROM policies LIMIT 10;

-- Sample claim records.
SELECT * FROM claims LIMIT 10;

-- Sample payment records.
SELECT * FROM payments LIMIT 10;


/* ============================================================================
   SECTION 05 — NULL / MISSING-VALUE AUDIT
   ----------------------------------------------------------------------------
   Objective:
   Count NULL values across all important columns.

   This identifies fields requiring investigation during the Python
   cleaning stage.
   ============================================================================ */

-- -------------------------
-- Customer NULL audit
-- -------------------------

SELECT
    SUM(Customer_ID IS NULL) AS Customer_ID_nulls,
    SUM(Customer_Name IS NULL) AS Customer_Name_nulls,
    SUM(Gender IS NULL) AS Gender_nulls,
    SUM(Age IS NULL) AS Age_nulls,
    SUM(Marital_Status IS NULL) AS Marital_Status_nulls,
    SUM(Occupation IS NULL) AS Occupation_nulls,
    SUM(Annual_Income IS NULL) AS Annual_Income_nulls,
    SUM(City IS NULL) AS City_nulls,
    SUM(State IS NULL) AS State_nulls,
    SUM(Address IS NULL) AS Address_nulls,
    SUM(Contact_Number IS NULL) AS Contact_Number_nulls,
    SUM(Email IS NULL) AS Email_nulls,
    SUM(Driving_Experience_Years IS NULL) AS Driving_Experience_nulls
FROM customers;


-- -------------------------
-- Vehicle NULL audit
-- -------------------------

SELECT
    SUM(Vehicle_ID IS NULL) AS Vehicle_ID_nulls,
    SUM(Customer_ID IS NULL) AS Customer_ID_nulls,
    SUM(Vehicle_Type IS NULL) AS Vehicle_Type_nulls,
    SUM(Brand IS NULL) AS Brand_nulls,
    SUM(Model IS NULL) AS Model_nulls,
    SUM(Manufacture_Year IS NULL) AS Manufacture_Year_nulls,
    SUM(Registration_State IS NULL) AS Registration_State_nulls,
    SUM(Fuel_Type IS NULL) AS Fuel_Type_nulls,
    SUM(Engine_CC IS NULL) AS Engine_CC_nulls,
    SUM(Vehicle_Value IS NULL) AS Vehicle_Value_nulls,
    SUM(Purchase_Date IS NULL) AS Purchase_Date_nulls
FROM vehicles;


-- -------------------------
-- Policy NULL audit
-- -------------------------

SELECT
    SUM(Policy_ID IS NULL) AS Policy_ID_nulls,
    SUM(Customer_ID IS NULL) AS Customer_ID_nulls,
    SUM(Vehicle_ID IS NULL) AS Vehicle_ID_nulls,
    SUM(Policy_Type IS NULL) AS Policy_Type_nulls,
    SUM(Coverage_Amount IS NULL) AS Coverage_Amount_nulls,
    SUM(Premium_Amount IS NULL) AS Premium_Amount_nulls,
    SUM(Start_Date IS NULL) AS Start_Date_nulls,
    SUM(End_Date IS NULL) AS End_Date_nulls,
    SUM(No_Claim_Bonus IS NULL) AS No_Claim_Bonus_nulls,
    SUM(Policy_Status IS NULL) AS Policy_Status_nulls
FROM policies;


-- -------------------------
-- Claims NULL audit
-- -------------------------

SELECT
    SUM(Claim_ID IS NULL) AS Claim_ID_nulls,
    SUM(Policy_ID IS NULL) AS Policy_ID_nulls,
    SUM(Vehicle_ID IS NULL) AS Vehicle_ID_nulls,
    SUM(Customer_ID IS NULL) AS Customer_ID_nulls,
    SUM(Claim_Date IS NULL) AS Claim_Date_nulls,
    SUM(Accident_City IS NULL) AS Accident_City_nulls,
    SUM(Accident_Type IS NULL) AS Accident_Type_nulls,
    SUM(Weather_Condition IS NULL) AS Weather_Condition_nulls,
    SUM(Police_Report_Filed IS NULL) AS Police_Report_nulls,
    SUM(Injuries IS NULL) AS Injuries_nulls,
    SUM(Estimated_Damage_Cost IS NULL) AS Damage_Cost_nulls,
    SUM(Claim_Amount IS NULL) AS Claim_Amount_nulls,
    SUM(Fraud_Suspected IS NULL) AS Fraud_nulls,
    SUM(Claim_Status IS NULL) AS Claim_Status_nulls,
    SUM(Settlement_Days IS NULL) AS Settlement_Days_nulls
FROM claims;


-- -------------------------
-- Payments NULL audit
-- -------------------------

SELECT
    SUM(Payment_ID IS NULL) AS Payment_ID_nulls,
    SUM(Claim_ID IS NULL) AS Claim_ID_nulls,
    SUM(Payment_Date IS NULL) AS Payment_Date_nulls,
    SUM(Payment_Mode IS NULL) AS Payment_Mode_nulls,
    SUM(Amount_Paid IS NULL) AS Amount_Paid_nulls,
    SUM(Payment_Status IS NULL) AS Payment_Status_nulls
FROM payments;


/* ============================================================================
   SECTION 06 — PRIMARY KEY DUPLICATE AUDIT
   ----------------------------------------------------------------------------
   Objective:
   Verify that each table's primary/business identifier remains unique.
   A result with zero rows means no duplicate keys were found.
   ============================================================================ */

-- Duplicate customer identifiers.
SELECT
    Customer_ID,
    COUNT(*) AS duplicate_count
FROM customers
GROUP BY Customer_ID
HAVING COUNT(*) > 1;


-- Duplicate policy identifiers.
SELECT
    Policy_ID,
    COUNT(*) AS duplicate_count
FROM policies
GROUP BY Policy_ID
HAVING COUNT(*) > 1;


-- Duplicate vehicle identifiers.
SELECT
    Vehicle_ID,
    COUNT(*) AS duplicate_count
FROM vehicles
GROUP BY Vehicle_ID
HAVING COUNT(*) > 1;


-- Duplicate claim identifiers.
SELECT
    Claim_ID,
    COUNT(*) AS duplicate_count
FROM claims
GROUP BY Claim_ID
HAVING COUNT(*) > 1;


-- Duplicate payment identifiers.
SELECT
    Payment_ID,
    COUNT(*) AS duplicate_count
FROM payments
GROUP BY Payment_ID
HAVING COUNT(*) > 1;


/* ============================================================================
   SECTION 07 — CATEGORICAL DATA PROFILING
   ----------------------------------------------------------------------------
   Objective:
   Inspect the distinct values and their frequencies for important
   categorical fields.

   This helps identify:
       - Unexpected categories
       - Spelling inconsistencies
       - Different capitalization
       - Placeholder values
       - Rare categories requiring investigation
   ============================================================================ */

-- -------------------------
-- Customer categories
-- -------------------------

-- Gender distribution.
SELECT Gender, COUNT(*) AS count
FROM customers
GROUP BY Gender
ORDER BY count DESC;

-- Marital status distribution.
SELECT Marital_Status, COUNT(*) AS count
FROM customers
GROUP BY Marital_Status
ORDER BY count DESC;

-- Occupation distribution.
SELECT Occupation, COUNT(*) AS count
FROM customers
GROUP BY Occupation
ORDER BY count DESC;

-- Customer state distribution.
SELECT State, COUNT(*) AS count
FROM customers
GROUP BY State
ORDER BY count DESC;


-- -------------------------
-- Vehicle categories
-- -------------------------

-- Vehicle type distribution.
SELECT Vehicle_Type, COUNT(*) AS count
FROM vehicles
GROUP BY Vehicle_Type
ORDER BY count DESC;

-- Vehicle brand distribution.
SELECT Brand, COUNT(*) AS count
FROM vehicles
GROUP BY Brand
ORDER BY count DESC;

-- Fuel type distribution.
SELECT Fuel_Type, COUNT(*) AS count
FROM vehicles
GROUP BY Fuel_Type
ORDER BY count DESC;

-- Vehicle registration state distribution.
SELECT Registration_State, COUNT(*) AS count
FROM vehicles
GROUP BY Registration_State
ORDER BY count DESC;


-- -------------------------
-- Policy categories
-- -------------------------

-- Policy type distribution.
SELECT Policy_Type, COUNT(*) AS count
FROM policies
GROUP BY Policy_Type
ORDER BY count DESC;

-- Policy status distribution.
SELECT Policy_Status, COUNT(*) AS count
FROM policies
GROUP BY Policy_Status
ORDER BY count DESC;


-- -------------------------
-- Claims categories
-- -------------------------

-- Accident type distribution.
SELECT Accident_Type, COUNT(*) AS count
FROM claims
GROUP BY Accident_Type
ORDER BY count DESC;

-- Weather condition distribution.
SELECT Weather_Condition, COUNT(*) AS count
FROM claims
GROUP BY Weather_Condition
ORDER BY count DESC;

-- Police report distribution.
SELECT Police_Report_Filed, COUNT(*) AS count
FROM claims
GROUP BY Police_Report_Filed
ORDER BY count DESC;

-- Injury severity distribution.
SELECT Injuries, COUNT(*) AS count
FROM claims
GROUP BY Injuries
ORDER BY count DESC;

-- Original fraud-suspected distribution.
SELECT Fraud_Suspected, COUNT(*) AS count
FROM claims
GROUP BY Fraud_Suspected
ORDER BY count DESC;

-- Claim status distribution.
SELECT Claim_Status, COUNT(*) AS count
FROM claims
GROUP BY Claim_Status
ORDER BY count DESC;


-- -------------------------
-- Payment categories
-- -------------------------

-- Payment mode distribution.
SELECT Payment_Mode, COUNT(*) AS count
FROM payments
GROUP BY Payment_Mode
ORDER BY count DESC;

-- Payment status distribution.
SELECT Payment_Status, COUNT(*) AS count
FROM payments
GROUP BY Payment_Status
ORDER BY count DESC;


/* ============================================================================
   SECTION 08 — NUMERICAL DATA PROFILING
   ----------------------------------------------------------------------------
   Objective:
   Inspect the minimum, maximum, and average values of important numerical
   variables to identify potentially unrealistic values.
   ============================================================================ */

-- Customer numerical summary.
SELECT
    MIN(Age) AS min_age,
    MAX(Age) AS max_age,
    AVG(Age) AS avg_age,
    MIN(Annual_Income) AS min_income,
    MAX(Annual_Income) AS max_income,
    AVG(Annual_Income) AS avg_income,
    MIN(Driving_Experience_Years) AS min_driving_experience,
    MAX(Driving_Experience_Years) AS max_driving_experience
FROM customers;


-- Existing duplicate customer numerical summary from the original audit.
-- Retained intentionally for completeness of the original audit workflow.
SELECT
    MIN(Age) AS min_age,
    MAX(Age) AS max_age,
    AVG(Age) AS avg_age,
    MIN(Annual_Income) AS min_income,
    MAX(Annual_Income) AS max_income,
    AVG(Annual_Income) AS avg_income,
    MIN(Driving_Experience_Years) AS min_driving_experience,
    MAX(Driving_Experience_Years) AS max_driving_experience
FROM customers;


-- Policy financial and NCB summary.
SELECT
    MIN(Coverage_Amount) AS min_coverage,
    MAX(Coverage_Amount) AS max_coverage,
    MIN(Premium_Amount) AS min_premium,
    MAX(Premium_Amount) AS max_premium,
    MIN(No_Claim_Bonus) AS min_ncb,
    MAX(No_Claim_Bonus) AS max_ncb
FROM policies;


-- Claims monetary and settlement summary.
SELECT
    MIN(Estimated_Damage_Cost) AS min_damage,
    MAX(Estimated_Damage_Cost) AS max_damage,
    MIN(Claim_Amount) AS min_claim,
    MAX(Claim_Amount) AS max_claim,
    MIN(Settlement_Days) AS min_settlement_days,
    MAX(Settlement_Days) AS max_settlement_days
FROM claims;


-- Payment amount range.
SELECT
    MIN(Amount_Paid) AS min_payment,
    MAX(Amount_Paid) AS max_payment
FROM payments;


/* ============================================================================
   SECTION 09 — NUMERICAL VALIDATION
   ----------------------------------------------------------------------------
   Objective:
   Identify physically or logically invalid numerical values.
   ============================================================================ */

-- Check for impossible customer ages.
SELECT *
FROM customers
WHERE Age < 18
   OR Age > 100;


-- Check for impossible driving experience.
SELECT *
FROM customers
WHERE Driving_Experience_Years < 0
   OR Driving_Experience_Years > Age;


-- Check for negative annual income.
SELECT *
FROM customers
WHERE Annual_Income < 0;


-- Check for unrealistic vehicle manufacture years.
SELECT *
FROM vehicles
WHERE Manufacture_Year < 1900
   OR Manufacture_Year > YEAR(CURDATE());


-- Check for zero or negative engine capacities.
SELECT *
FROM vehicles
WHERE Engine_CC <= 0;


-- Check for zero or negative vehicle values.
SELECT *
FROM vehicles
WHERE Vehicle_Value <= 0;


-- Check for invalid policy financial values.
SELECT *
FROM policies
WHERE Coverage_Amount <= 0
   OR Premium_Amount <= 0;


-- Check for invalid No-Claim Bonus percentages.
SELECT *
FROM policies
WHERE No_Claim_Bonus < 0
   OR No_Claim_Bonus > 100;


-- Check for invalid claim amounts, damage costs, or settlement durations.
SELECT *
FROM claims
WHERE Estimated_Damage_Cost < 0
   OR Claim_Amount < 0
   OR Settlement_Days < 0;


-- Check for negative payment amounts.
SELECT *
FROM payments
WHERE Amount_Paid < 0;


/* ============================================================================
   SECTION 10 — POLICY DATE VALIDATION
   ----------------------------------------------------------------------------
   Objective:
   Verify that policy end dates do not precede their start dates and
   calculate the overall policy duration range.
   ============================================================================ */

-- Identify policies with an invalid date range.
SELECT *
FROM policies
WHERE End_Date < Start_Date;


-- Calculate policy duration statistics in days.
SELECT
    MIN(DATEDIFF(End_Date, Start_Date)) AS shortest_policy_days,
    MAX(DATEDIFF(End_Date, Start_Date)) AS longest_policy_days,
    AVG(DATEDIFF(End_Date, Start_Date)) AS average_policy_days
FROM policies;


/* ============================================================================
   SECTION 11 — DATE RANGE PROFILING
   ----------------------------------------------------------------------------
   Objective:
   Understand the overall temporal coverage of vehicles, claims, and
   payments.
   ============================================================================ */

-- Vehicle purchase date range.
SELECT
    MIN(Purchase_Date) AS earliest_purchase,
    MAX(Purchase_Date) AS latest_purchase
FROM vehicles;


-- Claim date range.
SELECT
    MIN(Claim_Date) AS earliest_claim,
    MAX(Claim_Date) AS latest_claim
FROM claims;


-- Payment date range.
SELECT
    MIN(Payment_Date) AS earliest_payment,
    MAX(Payment_Date) AS latest_payment
FROM payments;


/* ============================================================================
   SECTION 12 — REFERENTIAL INTEGRITY AUDIT
   ----------------------------------------------------------------------------
   Objective:
   Verify that all foreign-key relationships point to existing parent
   records.

   Expected result:
   All queries should return zero rows.
   ============================================================================ */

-- Vehicles without a valid customer.
SELECT v.*
FROM vehicles v
LEFT JOIN customers c
    ON v.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL;


-- Policies without a valid customer.
SELECT p.*
FROM policies p
LEFT JOIN customers c
    ON p.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL;


-- Policies without a valid vehicle.
SELECT p.*
FROM policies p
LEFT JOIN vehicles v
    ON p.Vehicle_ID = v.Vehicle_ID
WHERE v.Vehicle_ID IS NULL;


-- Claims without a valid policy.
SELECT c.*
FROM claims c
LEFT JOIN policies p
    ON c.Policy_ID = p.Policy_ID
WHERE p.Policy_ID IS NULL;


-- Claims without a valid customer.
SELECT c.*
FROM claims c
LEFT JOIN customers cu
    ON c.Customer_ID = cu.Customer_ID
WHERE cu.Customer_ID IS NULL;


-- Payments without a valid claim.
SELECT p.*
FROM payments p
LEFT JOIN claims c
    ON p.Claim_ID = c.Claim_ID
WHERE c.Claim_ID IS NULL;


/* ============================================================================
   SECTION 13 — CROSS-TABLE BUSINESS CONSISTENCY
   ----------------------------------------------------------------------------
   Objective:
   Foreign keys may be valid while the relationships are still logically
   inconsistent. These queries check whether linked records refer to the
   same underlying customer or vehicle.
   ============================================================================ */

-- Check whether the customer attached to a policy matches
-- the customer who owns its associated vehicle.
SELECT
    p.Policy_ID,
    p.Customer_ID AS Policy_Customer,
    v.Customer_ID AS Vehicle_Customer
FROM policies p
JOIN vehicles v
    ON p.Vehicle_ID = v.Vehicle_ID
WHERE p.Customer_ID <> v.Customer_ID;


-- Check whether the customer attached to a claim matches
-- the customer attached to its policy.
SELECT
    c.Claim_ID,
    c.Customer_ID AS Claim_Customer,
    p.Customer_ID AS Policy_Customer
FROM claims c
JOIN policies p
    ON c.Policy_ID = p.Policy_ID
WHERE c.Customer_ID <> p.Customer_ID;


-- Check whether the vehicle attached to a claim matches
-- the vehicle covered by the associated policy.
SELECT
    c.Claim_ID,
    c.Vehicle_ID AS Claim_Vehicle,
    p.Vehicle_ID AS Policy_Vehicle
FROM claims c
JOIN policies p
    ON c.Policy_ID = p.Policy_ID
WHERE c.Vehicle_ID <> p.Vehicle_ID;


/* ============================================================================
   SECTION 14 — CLAIM AMOUNT VALIDATION
   ----------------------------------------------------------------------------
   Objective:
   Ensure that a claim does not exceed its estimated damage cost and
   calculate the claim-to-damage ratio.
   ============================================================================ */

-- Identify claims exceeding the estimated damage cost.
SELECT *
FROM claims
WHERE Claim_Amount > Estimated_Damage_Cost;


-- Calculate claim-to-damage ratio statistics.
SELECT
    MIN(
        Claim_Amount /
        NULLIF(Estimated_Damage_Cost, 0)
    ) AS min_claim_ratio,

    MAX(
        Claim_Amount /
        NULLIF(Estimated_Damage_Cost, 0)
    ) AS max_claim_ratio,

    AVG(
        Claim_Amount /
        NULLIF(Estimated_Damage_Cost, 0)
    ) AS avg_claim_ratio
FROM claims;


/* ============================================================================
   SECTION 15 — CLAIM DATE VS POLICY PERIOD
   ----------------------------------------------------------------------------
   Objective:
   Verify that each claim occurs within the active period of its
   associated policy.
   ============================================================================ */

SELECT
    c.Claim_ID,
    c.Claim_Date,
    p.Start_Date,
    p.End_Date
FROM claims c
JOIN policies p
    ON c.Policy_ID = p.Policy_ID
WHERE c.Claim_Date < p.Start_Date
   OR c.Claim_Date > p.End_Date;


/* ============================================================================
   SECTION 16 — PAYMENT DATE VALIDATION
   ----------------------------------------------------------------------------
   Objective:
   Verify that payments do not occur before the associated claim.
   ============================================================================ */

-- Identify payments occurring before the corresponding claim date.
SELECT
    pay.Payment_ID,
    pay.Payment_Date,
    c.Claim_Date
FROM payments pay
JOIN claims c
    ON pay.Claim_ID = c.Claim_ID
WHERE pay.Payment_Date < c.Claim_Date;


-- Calculate payment delay statistics from claim to payment.
SELECT
    MIN(
        DATEDIFF(
            pay.Payment_Date,
            c.Claim_Date
        )
    ) AS min_payment_delay,

    MAX(
        DATEDIFF(
            pay.Payment_Date,
            c.Claim_Date
        )
    ) AS max_payment_delay,

    AVG(
        DATEDIFF(
            pay.Payment_Date,
            c.Claim_Date
        )
    ) AS avg_payment_delay
FROM payments pay
JOIN claims c
    ON pay.Claim_ID = c.Claim_ID;


/* ============================================================================
   SECTION 17 — CLAIMS WITHOUT PAYMENT
   ----------------------------------------------------------------------------
   Objective:
   Identify claims for which no payment record exists.

   These records are not automatically data errors. They may represent
   rejected, pending, or otherwise unpaid claims and are useful for later
   business analysis.
   ============================================================================ */

-- Detailed list of claims without payment records.
SELECT
    c.Claim_ID,
    c.Claim_Status,
    c.Claim_Amount,
    c.Fraud_Suspected
FROM claims c
LEFT JOIN payments p
    ON c.Claim_ID = p.Claim_ID
WHERE p.Claim_ID IS NULL;


-- Count claims without payment records.
SELECT COUNT(*) AS claims_without_payment
FROM claims c
LEFT JOIN payments p
    ON c.Claim_ID = p.Claim_ID
WHERE p.Claim_ID IS NULL;


/* ============================================================================
   SECTION 18 — PAYMENT VS CLAIM AMOUNT
   ----------------------------------------------------------------------------
   Objective:
   Compare total payments associated with each claim against the original
   claim amount.

   This identifies:
       - Claims paid above the requested amount
       - Partially settled claims
   ============================================================================ */

-- Identify claims where total payments exceed the claim amount.
SELECT
    c.Claim_ID,
    c.Claim_Amount,
    SUM(p.Amount_Paid) AS total_paid
FROM claims c
JOIN payments p
    ON c.Claim_ID = p.Claim_ID
GROUP BY c.Claim_ID, c.Claim_Amount
HAVING SUM(p.Amount_Paid) > c.Claim_Amount;


-- Identify claims where total payments are below the claim amount.
SELECT
    c.Claim_ID,
    c.Claim_Amount,
    SUM(p.Amount_Paid) AS total_paid,
    c.Claim_Amount - SUM(p.Amount_Paid) AS outstanding_amount
FROM claims c
JOIN payments p
    ON c.Claim_ID = p.Claim_ID
GROUP BY c.Claim_ID, c.Claim_Amount
HAVING SUM(p.Amount_Paid) < c.Claim_Amount;


/* ============================================================================
   SECTION 19 — MULTIPLE PAYMENTS PER CLAIM
   ----------------------------------------------------------------------------
   Objective:
   Identify claims associated with multiple payment records.
   This helps establish whether the payment process behaves as a
   one-to-one or one-to-many relationship.
   ============================================================================ */

SELECT
    Claim_ID,
    COUNT(*) AS payment_count,
    SUM(Amount_Paid) AS total_paid
FROM payments
GROUP BY Claim_ID
HAVING COUNT(*) > 1
ORDER BY payment_count DESC;


/* ============================================================================
   SECTION 20 — CLAIM TREND BY YEAR
   ----------------------------------------------------------------------------
   Objective:
   Summarize annual claim volume and claim amounts for exploratory
   analysis and temporal validation.
   ============================================================================ */

SELECT
    YEAR(Claim_Date) AS claim_year,
    COUNT(*) AS claim_count,
    SUM(Claim_Amount) AS total_claim_amount,
    AVG(Claim_Amount) AS average_claim_amount
FROM claims
GROUP BY YEAR(Claim_Date)
ORDER BY claim_year;


/* ============================================================================
   SECTION 21 — PAYMENT TREND BY YEAR
   ----------------------------------------------------------------------------
   Objective:
   Summarize annual payment activity.
   ============================================================================ */

SELECT
    YEAR(Payment_Date) AS payment_year,
    COUNT(*) AS payment_count,
    SUM(Amount_Paid) AS total_paid
FROM payments
GROUP BY YEAR(Payment_Date)
ORDER BY payment_year;


/* ============================================================================
   SECTION 22 — SPECIFIC 2027 PAYMENT INVESTIGATION
   ----------------------------------------------------------------------------
   Objective:
   Inspect payments occurring in 2027 because the dataset contains
   payment dates extending beyond the main claim/policy periods.
   ============================================================================ */

SELECT *
FROM payments
WHERE YEAR(payment_date) = 2027;


/* ============================================================================
   SECTION 23 — FRAUD ANALYSIS
   ----------------------------------------------------------------------------
   Objective:
   Profile the original Fraud_Suspected field by claim volume and
   financial impact.
   ============================================================================ */

-- Overall fraud-suspected distribution with claim amounts.
SELECT
    Fraud_Suspected,
    COUNT(*) AS claim_count,
    SUM(Claim_Amount) AS total_claim_amount,
    AVG(Claim_Amount) AS average_claim_amount
FROM claims
GROUP BY Fraud_Suspected;


-- Fraud status cross-tabulated with claim status.
SELECT
    Fraud_Suspected,
    Claim_Status,
    COUNT(*) AS claim_count
FROM claims
GROUP BY Fraud_Suspected, Claim_Status
ORDER BY Fraud_Suspected, claim_count DESC;


/* ============================================================================
   SECTION 24 — CLAIM STATUS ANALYSIS
   ----------------------------------------------------------------------------
   Objective:
   Examine claim volumes, financial exposure, and settlement duration
   across claim statuses.
   ============================================================================ */

SELECT
    Claim_Status,
    COUNT(*) AS claim_count,
    SUM(Claim_Amount) AS total_claim_amount,
    AVG(Settlement_Days) AS avg_settlement_days
FROM claims
GROUP BY Claim_Status
ORDER BY claim_count DESC;


/* ============================================================================
   SECTION 25 — POLICY STATUS ANALYSIS
   ----------------------------------------------------------------------------
   Objective:
   Analyze premium activity across policy statuses.
   ============================================================================ */

SELECT
    Policy_Status,
    COUNT(*) AS policy_count,
    SUM(Premium_Amount) AS total_premium,
    AVG(Premium_Amount) AS avg_premium
FROM policies
GROUP BY Policy_Status;


/* ============================================================================
   SECTION 26 — POLICY TYPE ANALYSIS
   ----------------------------------------------------------------------------
   Objective:
   Compare policy volumes, premiums, and coverage amounts across
   policy types.
   ============================================================================ */

SELECT
    Policy_Type,
    COUNT(*) AS policy_count,
    AVG(Premium_Amount) AS avg_premium,
    AVG(Coverage_Amount) AS avg_coverage
FROM policies
GROUP BY Policy_Type
ORDER BY policy_count DESC;


/* ============================================================================
   SECTION 27 — CUSTOMER / VEHICLE / POLICY COVERAGE
   ----------------------------------------------------------------------------
   Objective:
   Identify customers or vehicles that currently have no associated
   records in downstream tables.

   These are not automatically errors; they may be legitimate business
   cases and should be interpreted during analysis.
   ============================================================================ */

-- Customers without vehicles.
SELECT
    c.Customer_ID,
    c.Customer_Name
FROM customers c
LEFT JOIN vehicles v
    ON c.Customer_ID = v.Customer_ID
WHERE v.Vehicle_ID IS NULL;


-- Customers without policies.
SELECT
    c.Customer_ID,
    c.Customer_Name
FROM customers c
LEFT JOIN policies p
    ON c.Customer_ID = p.Customer_ID
WHERE p.Policy_ID IS NULL;


-- Vehicles without policies.
SELECT
    v.Vehicle_ID,
    v.Customer_ID,
    v.Brand,
    v.Model
FROM vehicles v
LEFT JOIN policies p
    ON v.Vehicle_ID = p.Vehicle_ID
WHERE p.Policy_ID IS NULL;


/* ============================================================================
   SECTION 28 — FINAL DATABASE AUDIT SUMMARY
   ----------------------------------------------------------------------------
   Objective:
   Produce a compact final health snapshot containing:

       - Row counts for all major tables
       - Missing injury records
       - Claims without payment
       - Claims outside policy period
       - Claims above estimated damage
       - Payments occurring before claim date

   This query can be used as the final high-level data-quality checkpoint.
   ============================================================================ */

SELECT
    (SELECT COUNT(*) FROM customers) AS customers,
    (SELECT COUNT(*) FROM vehicles) AS vehicles,
    (SELECT COUNT(*) FROM policies) AS policies,
    (SELECT COUNT(*) FROM claims) AS claims,
    (SELECT COUNT(*) FROM payments) AS payments,

    -- Missing injury information in claims.
    (
        SELECT COUNT(*)
        FROM claims
        WHERE Injuries IS NULL
    ) AS claims_missing_injuries,

    -- Claims that do not currently have a payment record.
    (
        SELECT COUNT(*)
        FROM claims c
        LEFT JOIN payments p
            ON c.Claim_ID = p.Claim_ID
        WHERE p.Claim_ID IS NULL
    ) AS claims_without_payment,

    -- Claims occurring outside the associated policy period.
    (
        SELECT COUNT(*)
        FROM claims c
        JOIN policies p
            ON c.Policy_ID = p.Policy_ID
        WHERE c.Claim_Date < p.Start_Date
           OR c.Claim_Date > p.End_Date
    ) AS claims_outside_policy_period,

    -- Claims exceeding their estimated damage amount.
    (
        SELECT COUNT(*)
        FROM claims
        WHERE Claim_Amount > Estimated_Damage_Cost
    ) AS claims_over_damage,

    -- Payments occurring before their associated claim.
    (
        SELECT COUNT(*)
        FROM payments pay
        JOIN claims c
            ON pay.Claim_ID = c.Claim_ID
        WHERE pay.Payment_Date < c.Claim_Date
    ) AS payments_before_claim;
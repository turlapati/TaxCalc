**Requirements Document: Advanced Post-Tax Income Calculator**

**Version:** 1.1 (Reflecting calculation correction)
**Date:** April 11, 2025

**1. Introduction**

*   **1.1. Purpose:** This document describes the requirements for a client-side web application that calculates the estimated Gross Pre-Tax Annual Income required to achieve a user-specified Desired Annual Post-Tax Income. The calculation considers federal, state, and local income taxes, FICA taxes (Social Security & Medicare), state-specific deductions (like SDI), and user-defined pre-tax benefit deductions.
*   **1.2. Scope:**
    *   The calculator focuses on estimating income requirements for individuals earning wage/salary income in the United States.
    *   It allows users to compare up to four different scenarios based on work/residence locations and benefit contributions.
    *   Calculations are based on configurable tax brackets and rates for the specified tax year (currently 2025, using estimates where final figures aren't available).
    *   The application is implemented as Python progrm using Flet (https://flet.dev/docs/).
    *   It does *not* account for all possible tax complexities (e.g., itemized deductions beyond pre-tax benefits, most tax credits, investment income, self-employment).
*   **1.3. Target Audience:** Developers, QA testers, Technical Project Managers.

**2. Functional Requirements**

*   **2.1. Core Calculation:**
    *   FR-001: The system MUST calculate the Gross Pre-Tax Annual Income required to yield a user-specified Desired Annual Post-Tax Income.
    *   FR-002: The calculation MUST use an iterative ("guess and check") approach to converge on the Gross Pre-Tax Income, as taxes depend on gross income and vice-versa.
    *   FR-003: The iterative calculation MUST stop when the difference between the calculated net income and the target net income is within a defined tolerance (e.g., $0.50) or a maximum number of iterations is reached.
*   **2.2. User Inputs:**
    *   FR-010: The system MUST allow the user to input their Desired Annual Post-Tax Income (numeric).
    *   FR-011: The system MUST allow the user to select their Tax Filing Status (Single, Married Filing Jointly, Married Filing Separately, Head of Household) via a dropdown. This selection applies globally to all scenarios.
    *   FR-012: The system MUST allow the user to define 1 to 4 distinct calculation scenarios.
    *   FR-013: For each scenario, the system MUST allow the user to select a Work State from a dropdown list of all US states and DC.
    *   FR-014: For each scenario, the system MUST allow the user to select a Residence State from a dropdown list of all US states and DC.
    *   FR-015: If the selected Work State has known city-level income taxes configured in the system, the system MUST display a Work City dropdown for that scenario.
    *   FR-016: The Work City dropdown MUST include an "N/A" option and options for all configured cities within the selected Work State.
    *   FR-017: For each scenario, the system MUST allow the user to input annual pre-tax deduction amounts for:
        *   Health Insurance (numeric, default 0)
        *   Dental/Vision Insurance (numeric, default 0)
        *   HSA Contribution (numeric, default 0)
        *   FSA (Health/Dependent Care) Contribution (numeric, default 0)
        *   401k/403b Pre-Tax Contribution (numeric, default 0)
        *   Other Pre-Tax Deductions (numeric, default 0)
    *   FR-018: If the selected Work State has State Disability Insurance (SDI) or similar mandatory state deductions configured, the system MUST display a read-only field showing the calculated annual contribution for that scenario.
*   **2.3. Tax & Deduction Calculations:**
    *   FR-020: The system MUST calculate Federal Income Tax based on the selected Filing Status and configured 2025 progressive tax brackets. Taxable income for this calculation is Gross Income minus applicable Pre-Tax Benefit Deductions.
    *   FR-021: The system MUST calculate FICA taxes (Employee Share):
        *   Social Security tax at the configured rate (6.2%) up to the configured annual wage limit ($177,300 for 2025 est.).
        *   Medicare tax at the configured rate (1.45%) on all gross income.
        *   Additional Medicare tax at the configured rate (0.9%) on gross income exceeding thresholds based on Filing Status.
    *   FR-022: The system MUST calculate State Income Tax for the Work State based on configured state tax brackets (progressive or flat). Taxable income is Gross Income minus applicable Pre-Tax Benefit Deductions.
    *   FR-023: The system MUST calculate State Income Tax for the Residence State *if* it differs from the Work State. The calculation should implement simplified reciprocity logic (e.g., calculate potential residence tax and subtract work state tax paid, minimum zero). Taxable income is Gross Income minus applicable Pre-Tax Benefit Deductions.
    *   FR-024: The system MUST calculate City Income Tax *if* a specific Work City (not "N/A") is selected and configured tax rates exist for that city. Taxable income is Gross Income minus applicable Pre-Tax Benefit Deductions.
    *   FR-025: The system MUST calculate State Disability Insurance (SDI) / Paid Family Leave (PFML) contributions based on configured rates/limits for specific Work States (e.g., CA, NY, NJ, RI, HI). Calculation logic must handle percentage rates, wage caps, and weekly maximums as applicable per state configuration.
    *   FR-026: Pre-Tax Benefit Deductions MUST reduce the income base used for calculating Federal, State, and City *income taxes*. They generally do *not* reduce the income base for FICA or SDI calculations.
*   **2.4. Scenario Management:**
    *   FR-030: The system MUST provide an "Add Scenario" button.
    *   FR-031: The system MUST allow a maximum of 4 scenarios to be added. The "Add Scenario" button should be disabled when the maximum is reached.
    *   FR-032: The system MUST provide a "Remove" button for each scenario except the first one. Removing a scenario should enable the "Add Scenario" button if applicable.
*   **2.5. Output and Display:**
    *   FR-040: The system MUST provide a "Calculate All Scenarios" button to trigger the calculations.
    *   FR-041: After calculation, the system MUST display the results for each valid scenario in a distinct results card.
    *   FR-042: Each results card MUST display:
        *   Scenario Identifier (e.g., "Scenario 1 (NY/NJ)")
        *   Calculated Required Gross Pre-Tax Income
        *   Breakdown of calculated amounts for: Federal Income Tax, Social Security Tax, Medicare Tax, State Tax (Work), State Tax (Residence) (if applicable), City Tax (if applicable), SDI/PFML (if applicable), Total Pre-Tax Benefits.
        *   Total Taxes
        *   Total Deductions (Benefits)
        *   Final Calculated Net Income
        *   The original Target Net Income and the difference from the Calculated Net Income.
    *   FR-043: The system MUST display a stacked bar chart comparing the calculated components across all valid scenarios.
    *   FR-044: The stacked bar chart MUST represent each scenario as a bar.
    *   FR-045: Each bar stack MUST visually represent the relative amounts of: Federal Tax, Social Security, Medicare, State Tax (Work), State Tax (Residence), City Tax, SDI/PFML, and Pre-Tax Benefits.
    *   FR-046: The chart MUST include tooltips showing the specific value of each segment on hover.
    *   FR-047: The chart MUST dynamically hide categories (and legend items) if their value is zero or negligible across all displayed scenarios.
    *   FR-048: The system MUST display a disclaimer regarding the estimations and limitations of the calculator.

**3. Non-Functional Requirements**

*   **3.1. Usability:**
    *   NFR-001: The user interface MUST be clean, professional, and intuitive.
    *   NFR-002: All input fields and buttons MUST be clearly labeled.
    *   NFR-003: Dropdown lists MUST be populated correctly and dynamically where applicable (e.g., Cities based on State).
    *   NFR-004: The application should be reasonably responsive and display correctly on common desktop browser window sizes.
*   **3.2. Performance:**
    *   NFR-010: Scenario calculations should complete within a few seconds under typical conditions.
    *   NFR-011: The iterative calculation MUST include a maximum iteration limit to prevent infinite loops in case of non-convergence.
*   **3.3. Maintainability:**
    *   NFR-020: The code MUST be reasonably well-structured and organized within the single file.
    *   NFR-021: Python code should use meaningful variable and function names.
    *   NFR-022: Tax data (brackets, rates, limits) MUST be stored in clearly defined Python constants/objects, separate from the core calculation logic, to facilitate annual updates.
    *   NFR-023: Comments should be used to explain complex logic sections, especially the iterative calculation and tax rule implementations.
*   **3.4. Accuracy:**
    *   NFR-030: Calculations MUST accurately reflect the implemented tax rules, rates, and brackets for the specified year (2025).
    *   NFR-031: FICA limits and thresholds MUST be correctly applied.
    *   NFR-032: The iterative calculation MUST converge to a result within the specified tolerance under normal input conditions.
    *   NFR-033: Limitations and simplifications (see Section 6) MUST be clearly communicated to the user via the disclaimer.
*   **3.5. Compatibility:**
    *   NFR-040: The application MUST function correctly on the latest versions of major web browsers (Chrome, Firefox, Edge, Safari).

**4. Data Requirements**

*   **4.1. Configuration Data (Constants/Objects):**
    *   Federal Tax Brackets (per filing status)
    *   State Tax Brackets (per state)
    *   City Tax Rates (per city, nested under state)
    *   FICA Rates and Limits (SS Rate/Limit, Medicare Rate/Additional Rate/Thresholds)
    *   SDI Rates and Limits (per applicable state)
*   **4.2. User Input Data:**
    *   Desired Post-Tax Income
    *   Filing Status
    *   Work State (per scenario)
    *   Residence State (per scenario)
    *   Work City (per scenario)
    *   Benefit Deduction amounts (per scenario)
*   **4.3. Calculated Data (Intermediate & Final):**
    *   Gross Pre-Tax Income guess (iterative)
    *   Taxable Income for Income Tax (intermediate)
    *   Individual tax amounts (Federal, State, City, SS, Medicare, SDI)
    *   Total Tax
    *   Calculated Net Income (iterative and final)
    *   Difference from Target Net Income

**5. User Interface (UI) Requirements**

*   **5.1. Layout:** Single-page application layout.
    *   Main Title
    *   Global Inputs Section (Desired Income, Filing Status)
    *   Scenarios Section:
        *   Contains individual Scenario Containers.
        *   "Add Scenario" button below containers.
    *   Results Section: Displays Result Cards side-by-side or stacked.
    *   Chart Section: Displays the stacked bar chart.
    *   Disclaimer Footer.
*   **5.2. Scenario Container Layout:**
    *   Scenario Header (Title, Remove Button)
    *   Input Grid (Work State, City [dynamic], Residence State, SDI [dynamic])
    *   Benefit Deductions Sub-section (labeled input fields in a grid).
*   **5.3. Dynamic UI Elements:**
    *   Work City dropdown and label appear/disappear based on Work State selection.
    *   SDI input field and label appear/disappear based on Work State selection.
    *   "Add Scenario" button becomes disabled when 4 scenarios exist.
    *   "Remove" button is hidden for the first scenario.
*   **5.4. Styling:** Adheres to the defined professional theme (colors, fonts, spacing, shadows, border-radius as implemented in CSS).

**6. Calculation Logic Overview**

*   **6.1. Iterative Solver:** The core uses a numerical method (currently a variation of fixed-point iteration or simple gradient adjustment) to find the `GrossPreTaxIncome` (`G`) such that:
    `G - CalculateTotalTaxes(G) - CalculateTotalBenefits() = TargetNetIncome`
    The loop adjusts `G` based on the difference between the `CalculatedNetIncome` and `TargetNetIncome` until the difference is minimal.
*   **6.2. Tax Calculation Order:** Within each iteration:
    1.  Calculate FICA and SDI based on the current `G`.
    2.  Calculate `IncomeForIncomeTax = G - TotalBenefitDeductions`.
    3.  Calculate Federal, State (Work/Residence), and City income taxes based on `IncomeForIncomeTax`.
    4.  Sum all taxes.
    5.  Calculate `CalculatedNetIncome = G - TotalTaxes - TotalBenefitDeductions`.
*   **6.3. State Reciprocity (Simplified):** Assumes the resident state provides a credit for taxes paid to the work state, up to the amount of tax that would have been due in the resident state. The calculated residence state tax is `max(0, PotentialResidenceTax - WorkStateTax)`.

**7. Assumptions and Limitations**

*   **7.1. Income Type:** Assumes income is solely from W-2 wages/salary. Does not handle self-employment, investments, retirement distributions, etc.
*   **7.2. Tax Year Data:** Uses hardcoded tax rates, brackets, and limits for 2025. Requires manual updates for future years or if official 2025 figures differ significantly from estimates.
*   **7.3. Deductions:** Only considers the specified pre-tax benefit deductions. Does **not** include Standard Deduction or Itemized Deductions (e.g., mortgage interest, SALT, medical expenses beyond FSA/HSA). This is a significant simplification impacting income tax accuracy.
*   **7.4. Tax Credits:** Does **not** include any federal or state tax credits (e.g., Child Tax Credit, Earned Income Tax Credit, education credits, EV credits, etc.).
*   **7.5. Complex Tax Situations:** Does not handle Alternative Minimum Tax (AMT), Net Investment Income Tax (NIIT), foreign income, state-specific nuances beyond basic brackets, or income phase-outs for deductions/credits.
*   **7.6. Benefit Limits:** Does not enforce statutory limits on contributions (e.g., 401k, HSA, FSA limits). Assumes user inputs are valid annual amounts.
*   **7.7. SDI/PFML:** Implementation is limited to a few example states and may not reflect all nuances or specific employer plans.
*   **7.8. State Reciprocity:** The model is a basic simplification and does not cover all complex inter-state agreements.
*   **7.9. Client-Side Only:** All calculations occur in the user's browser; no data is saved or processed server-side.

**8. Potential Future Enhancements**

*   Option to include Standard Deduction based on Filing Status.
*   Option to input estimated Itemized Deductions.
*   Inclusion of major Federal Tax Credits (e.g., CTC).
*   More sophisticated state tax reciprocity handling.
*   Validation of benefit contribution limits.
*   Dynamic fetching/updating of tax data via an API (if available).
*   Ability to save/load scenarios.
*   UI indication during calculation processing.
*   More granular error handling and user feedback.
import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import copy


# Ensure all rates and income levels are strings for Decimal conversion
def _decimalize_bracket_list(bracket_list):
    """Helper function to convert rates/maxIncome in a list of bracket dicts."""
    if not isinstance(bracket_list, list):
        print(f"Warning: Expected a list of brackets, got {type(bracket_list)}")
        return bracket_list # Return unchanged if not a list

    for bracket in bracket_list:
        if isinstance(bracket, dict):
            bracket["rate"] = str(bracket.get("rate", "0")) # Use .get for safety
            max_income = bracket.get("maxIncome")
            if isinstance(max_income, float) and max_income == float('inf'):
                bracket["maxIncome"] = 'inf'
            else:
                bracket["maxIncome"] = str(max_income if max_income is not None else 'inf') # Handle None or missing
        else:
             print(f"Warning: Expected a dict within bracket list, got {type(bracket)}")
    return bracket_list

def decimalize_tax_data(tax_data_raw):
    """Converts rates and maxIncome in various tax bracket structures to strings."""
    decimalized_data = copy.deepcopy(tax_data_raw) # Avoid modifying original raw data

    # Process Federal and State Brackets (Structure: Dict[str, List[Dict]])
    if isinstance(decimalized_data, dict):
        for key, value in decimalized_data.items():
            # Check if the value is a list of dicts (Federal/State structure)
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                 decimalized_data[key] = _decimalize_bracket_list(value)
            # Check if the value is a dict containing lists (City structure)
            elif isinstance(value, dict):
                 for city_key, city_brackets in value.items():
                     if isinstance(city_brackets, list):
                         value[city_key] = _decimalize_bracket_list(city_brackets)
                     else:
                         print(f"Warning: Unexpected structure for city '{city_key}' in state '{key}'")
            # Handle cases where the top-level value might be just a list (if structure changes)
            elif isinstance(value, list) and key not in CITY_TAX_RATES_RAW: # Avoid reprocessing city data if passed directly
                 print(f"Warning: Processing top-level list for key '{key}', assuming it's bracket data.")
                 decimalized_data[key] = _decimalize_bracket_list(value)


    # Explicitly handle City Tax Rates if passed directly (Structure: Dict[str, Dict[str, List[Dict]]])
    # This part is somewhat redundant if CITY_TAX_RATES_RAW is always processed via the main loop above,
    # but provides robustness if the function is called only with city data.
    elif isinstance(decimalized_data, dict) and all(isinstance(v, dict) for v in decimalized_data.values()): # Heuristic for city structure
         for state_key, cities in decimalized_data.items():
             if isinstance(cities, dict):
                 for city_key, city_brackets in cities.items():
                     if isinstance(city_brackets, list):
                         cities[city_key] = _decimalize_bracket_list(city_brackets)
                     else:
                          print(f"Warning: Unexpected structure for city '{city_key}' in state '{state_key}'")
             else:
                 print(f"Warning: Expected dict of cities for state '{state_key}', got {type(cities)}")

    else:
        print(f"Warning: Unrecognized tax data structure type: {type(tax_data_raw)}")


    return decimalized_data


FEDERAL_TAX_BRACKETS_RAW = {
    "single": [
        {"rate": 0.10, "maxIncome": 11925},
        {"rate": 0.12, "maxIncome": 48475},
        {"rate": 0.22, "maxIncome": 103350},
        {"rate": 0.24, "maxIncome": 197300},
        {"rate": 0.32, "maxIncome": 250525},
        {"rate": 0.35, "maxIncome": 626350},
        {"rate": 0.37, "maxIncome": float('inf')},
    ],
    "marriedJointly": [
        {"rate": 0.10, "maxIncome": 23850},
        {"rate": 0.12, "maxIncome": 96950},
        {"rate": 0.22, "maxIncome": 206700},
        {"rate": 0.24, "maxIncome": 394600},
        {"rate": 0.32, "maxIncome": 501050},
        {"rate": 0.35, "maxIncome": 751600},
        {"rate": 0.37, "maxIncome": float('inf')},
    ],
    "marriedSeparately": [
        {"rate": 0.10, "maxIncome": 11925},
        {"rate": 0.12, "maxIncome": 48475},
        {"rate": 0.22, "maxIncome": 103350},
        {"rate": 0.24, "maxIncome": 197300},
        {"rate": 0.32, "maxIncome": 250525},
        {"rate": 0.35, "maxIncome": 375800},
        {"rate": 0.37, "maxIncome": float('inf')},
    ],
    "headOfHousehold": [
        {"rate": 0.10, "maxIncome": 17850},
        {"rate": 0.12, "maxIncome": 63100},
        {"rate": 0.22, "maxIncome": 100500},
        {"rate": 0.24, "maxIncome": 191950},
        {"rate": 0.32, "maxIncome": 243700},
        {"rate": 0.35, "maxIncome": 609350},
        {"rate": 0.37, "maxIncome": float('inf')},
    ],
}

STATE_TAX_BRACKETS_RAW = {
    "AL": [
        {"rate": 0.02, "maxIncome": 500}, 
        {"rate": 0.04, "maxIncome": 3000}, 
        {"rate": 0.05, "maxIncome": float('inf')}
    ],
    "AK": [],
    "AZ": [{"rate": 0.025, "maxIncome": float('inf')}
	],
    "AR": [
        {"rate": 0.02, "maxIncome": 5100}, 
        {"rate": 0.03, "maxIncome": 10300}, 
        {"rate": 0.034, "maxIncome": float('inf')}
    ],
    "CA": [
        {"rate": 0.01, "maxIncome": 10412}, 
        {"rate": 0.02, "maxIncome": 24684}, 
        {"rate": 0.04, "maxIncome": 38959},
        {"rate": 0.06, "maxIncome": 54081}, 
        {"rate": 0.08, "maxIncome": 68350}, 
        {"rate": 0.093, "maxIncome": 349137},
        {"rate": 0.103, "maxIncome": 418966}, 
        {"rate": 0.113, "maxIncome": 698274}, 
        {"rate": 0.123, "maxIncome": float('inf')},
        {"rate": 0.133, "maxIncome": float('inf')} # Note: CA high rates overlap, simplified
    ],
    "CO": [{"rate": 0.04, "maxIncome": float('inf')}],
    "CT": [
        {"rate": 0.03, "maxIncome": 10000}, 
        {"rate": 0.05, "maxIncome": 50000}, 
        {"rate": 0.055, "maxIncome": 100000},
        {"rate": 0.06, "maxIncome": 200000}, 
        {"rate": 0.065, "maxIncome": 250000}, 
        {"rate": 0.069, "maxIncome": 500000},
        {"rate": 0.0699, "maxIncome": float('inf')}
    ],
    "DE": [
        {"rate": 0.022, "maxIncome": 5000}, 
        {"rate": 0.039, "maxIncome": 10000}, 
        {"rate": 0.048, "maxIncome": 20000},
        {"rate": 0.052, "maxIncome": 25000}, 
        {"rate": 0.0555, "maxIncome": 60000}, 
        {"rate": 0.066, "maxIncome": float('inf')}
    ],
    "DC": [
        {"rate": 0.04, "maxIncome": 10000}, 
        {"rate": 0.06, "maxIncome": 40000}, 
        {"rate": 0.065, "maxIncome": 60000},
        {"rate": 0.085, "maxIncome": 250000}, 
        {"rate": 0.095, "maxIncome": 350000}, 
        {"rate": 0.1025, "maxIncome": 1000000},
        {"rate": 0.1075, "maxIncome": float('inf')}
    ],
    "FL": [],
    "GA": [
        {"rate": 0.01, "maxIncome": 750}, 
        {"rate": 0.02, "maxIncome": 2250}, 
        {"rate": 0.03, "maxIncome": 3750},
        {"rate": 0.04, "maxIncome": 5250}, 
        {"rate": 0.05, "maxIncome": 7000}, 
        {"rate": 0.0549, "maxIncome": float('inf')}
    ],
    "HI": [
        {"rate": 0.014, "maxIncome": 2400}, 
        {"rate": 0.032, "maxIncome": 4800}, 
        {"rate": 0.055, "maxIncome": 9600},
        {"rate": 0.064, "maxIncome": 14400}, 
        {"rate": 0.068, "maxIncome": 19200}, 
        {"rate": 0.072, "maxIncome": 24000},
        {"rate": 0.076, "maxIncome": 36000}, 
        {"rate": 0.079, "maxIncome": 48000}, 
        {"rate": 0.0825, "maxIncome": 150000},
        {"rate": 0.09, "maxIncome": 175000}, 
        {"rate": 0.1, "maxIncome": 200000}, 
        {"rate": 0.11, "maxIncome": float('inf')}
    ],
    "ID": [{"rate": 0.01, "maxIncome": 1709},
		{"rate": 0.03, "maxIncome": 5127},
		{"rate": 0.045, "maxIncome": 8545},
		{"rate": 0.058, "maxIncome": float('inf')}
	],
    "IL": [{"rate": 0.0495, "maxIncome": float('inf')}],
    "IN": [{"rate": 0.0305, "maxIncome": float('inf')}],
    "IA": [{"rate": 0.04, "maxIncome": float('inf')}],
    "KS": [{"rate": 0.031, "maxIncome": 15000},
		{"rate": 0.0525, "maxIncome": 30000},
		{"rate": 0.057, "maxIncome": float('inf')}
	],
    "KY": [{"rate": 0.04, "maxIncome": float('inf')}],
    "LA": [{"rate": 0.0185, "maxIncome": float('inf')}],
    "ME": [{"rate": 0.058, "maxIncome": 26050},
		{"rate": 0.0675, "maxIncome": 61600},
		{"rate": 0.0715, "maxIncome": float('inf')}
	],
    "MD": [
        {"rate": 0.02, "maxIncome": 1000},
		{"rate": 0.03, "maxIncome": 2000},
		{"rate": 0.04, "maxIncome": 3000},
        {"rate": 0.0475, "maxIncome": 100000},
		{"rate": 0.05, "maxIncome": 125000},
		{"rate": 0.0525, "maxIncome": 150000},
        {"rate": 0.055, "maxIncome": 250000},
		{"rate": 0.0575, "maxIncome": float('inf')}
    ],
    "MA": [{"rate": 0.05, "maxIncome": 1083150},
		{"rate": 0.09, "maxIncome": float('inf')}],
    "MI": [{"rate": 0.0425, "maxIncome": float('inf')}],
    "MN": [{"rate": 0.0535, "maxIncome": 31690},
		{"rate": 0.068, "maxIncome": 104760},
		{"rate": 0.0785, "maxIncome": 193240},
		{"rate": 0.0985, "maxIncome": float('inf')}
	],
    "MS": [{"rate": 0.04, "maxIncome": float('inf')}],
    "MO": [
        {"rate": 0, "maxIncome": 1000},
		{"rate": 0.015, "maxIncome": 2000},
		{"rate": 0.02, "maxIncome": 3000},
        {"rate": 0.025, "maxIncome": 4000},
		{"rate": 0.03, "maxIncome": 5000},
		{"rate": 0.035, "maxIncome": 6000},
        {"rate": 0.04, "maxIncome": 7000},
		{"rate": 0.045, "maxIncome": 8000},
		{"rate": 0.048, "maxIncome": float('inf')}
    ],
    "MT": [
        {"rate": 0.01, "maxIncome": 3800},
		{"rate": 0.02, "maxIncome": 6500},
		{"rate": 0.03, "maxIncome": 9700},
        {"rate": 0.04, "maxIncome": 13600},
		{"rate": 0.05, "maxIncome": 18700},
		{"rate": 0.059, "maxIncome": 23600},
        {"rate": 0.065, "maxIncome": float('inf')}
    ],
    "NE": [{"rate": 0.0246, "maxIncome": 4030},
		{"rate": 0.0351, "maxIncome": 23320},
		{"rate": 0.0466, "maxIncome": 35730},
		{"rate": 0.0558, "maxIncome": float('inf')}
	],
    "NV": [],
    "NH": [],
    "NJ": [
        {"rate": 0.014, "maxIncome": 20000},
		{"rate": 0.0175, "maxIncome": 35000},
		{"rate": 0.035, "maxIncome": 40000},
        {"rate": 0.05525, "maxIncome": 75000},
		{"rate": 0.0637, "maxIncome": 500000},
		{"rate": 0.0897, "maxIncome": 1000000},
        {"rate": 0.1075, "maxIncome": float('inf')}
    ],
    "NM": [{"rate": 0.017, "maxIncome": 5500},
		{"rate": 0.032, "maxIncome": 11000},
		{"rate": 0.047, "maxIncome": 16500},
		{"rate": 0.059, "maxIncome": float('inf')}
	],
    "NY": [
        {"rate": 0.04, "maxIncome": 8500},
		{"rate": 0.045, "maxIncome": 11700},
		{"rate": 0.0525, "maxIncome": 13900},
        {"rate": 0.055, "maxIncome": 80650},
		{"rate": 0.06, "maxIncome": 215400},
		{"rate": 0.0685, "maxIncome": 1077550},
        {"rate": 0.0965, "maxIncome": 5000000},
		{"rate": 0.103, "maxIncome": 25000000},
		{"rate": 0.109, "maxIncome": float('inf')}
    ],
    "NC": [{"rate": 0.045, "maxIncome": float('inf')}],
    "ND": [
        {"rate": 0.011, "maxIncome": 48475},
		{"rate": 0.0195, "maxIncome": 80500},
		{"rate": 0.022, "maxIncome": 175150},
        {"rate": 0.026, "maxIncome": 282000},
		{"rate": 0.029, "maxIncome": float('inf')}
    ],
    "OH": [{"rate": 0, "maxIncome": 26050},
		{"rate": 0.0275, "maxIncome": float('inf')}
	],
    "OK": [
        {"rate": 0.0025, "maxIncome": 1000},
		{"rate": 0.0075, "maxIncome": 2500},
		{"rate": 0.0175, "maxIncome": 3750},
        {"rate": 0.0275, "maxIncome": 4900},
		{"rate": 0.0375, "maxIncome": 7200},
		{"rate": 0.0475, "maxIncome": float('inf')}
    ],
    "OR": [{"rate": 0.0475, "maxIncome": 4100},
		{"rate": 0.0675, "maxIncome": 10200},
		{"rate": 0.0875, "maxIncome": 125000},
		{"rate": 0.099, "maxIncome": float('inf')}
	],
    "PA": [{"rate": 0.0307, "maxIncome": float('inf')}],
    "RI": [{"rate": 0.0375, "maxIncome": 77100},
		{"rate": 0.0475, "maxIncome": 174700},
		{"rate": 0.0599, "maxIncome": float('inf')}
	],
    "SC": [
        {"rate": 0, "maxIncome": 3370},
		{"rate": 0.03, "maxIncome": 6740},
		{"rate": 0.04, "maxIncome": 10110},
        {"rate": 0.05, "maxIncome": 13480},
		{"rate": 0.06, "maxIncome": 16850},
		{"rate": 0.064, "maxIncome": float('inf')}
    ],
    "TN": [],
    "TX": [],
    "UT": [{"rate": 0.0465, "maxIncome": float('inf')}],
    "VT": [{"rate": 0.0335, "maxIncome": 48475},
		{"rate": 0.066, "maxIncome": 117000},
		{"rate": 0.076, "maxIncome": 242500},
		{"rate": 0.0875, "maxIncome": float('inf')}
    ],
    "VA": [{"rate": 0.02, "maxIncome": 3000},
		{"rate": 0.03, "maxIncome": 5000},
		{"rate": 0.05, "maxIncome": 17000},
		{"rate": 0.0575, "maxIncome": float('inf')}
    ],
    "WA": [],
    "WV": [
        {"rate": 0.0236, "maxIncome": 10000},
		{"rate": 0.0315, "maxIncome": 25000},
		{"rate": 0.0393, "maxIncome": 40000},
        {"rate": 0.0512, "maxIncome": 60000},
		{"rate": 0.0512, "maxIncome": float('inf')}
    ],
    "WI": [{"rate": 0.035, "maxIncome": 14520},
		{"rate": 0.044, "maxIncome": 29040},
		{"rate": 0.053, "maxIncome": 319410},
		{"rate": 0.0765, "maxIncome": float('inf')}
    ],
    "WY": []
}

CITY_TAX_RATES_RAW = {
    "NY": {
        "NYC": [
            {"rate": 0.03078, "maxIncome": 12000},
            {"rate": 0.03762, "maxIncome": 25000},
            {"rate": 0.03819, "maxIncome": 50000},
            {"rate": 0.03876, "maxIncome": float('inf')}
        ]
    },
    "PA": {
        "Philadelphia": [{"rate": 0.038712, "maxIncome": float('inf')}]
    },
    "MD": {
        "Baltimore": [{"rate": 0.0320, "maxIncome": float('inf')}]
    },
    "MO": {
        "Kansas City": [{"rate": 0.01, "maxIncome": float('inf')}],
        "St. Louis": [{"rate": 0.01, "maxIncome": float('inf')}]
    },
    "MI": {
        "Detroit": [{"rate": 0.024, "maxIncome": float('inf')}]
    },
    "DE": {
        "Wilmington": [{"rate": 0.0125, "maxIncome": float('inf')}]
    },
    "CO": { # Note: These often have flat monthly taxes not handled by income rate brackets
        "Denver": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Aurora": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Glendale": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Greenwood Village": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Sheridan": [{"rate": 0.00, "maxIncome": float('inf')}]
    },
    "OH": {
        "Columbus": [{"rate": 0.025, "maxIncome": float('inf')}]
    },
    "KY": {
        "Louisville": [{"rate": 0.0145, "maxIncome": float('inf')}]
    },
    "IN": {
        "Indianapolis": [{"rate": 0.0202, "maxIncome": float('inf')}]
    },
    "AL": {
        "Birmingham": [{"rate": 0.01, "maxIncome": float('inf')}],
        "Bessemer": [{"rate": 0.01, "maxIncome": float('inf')}],
        "Gadsden": [{"rate": 0.02, "maxIncome": float('inf')}],
        "Macon County": [{"rate": 0.01, "maxIncome": float('inf')}]
    },
    "NJ": {
        "Newark": [{"rate": 0.01, "maxIncome": float('inf')}]
    },
    "CA": {
        "San Francisco": [{"rate": 0.0038, "maxIncome": float('inf')}] # Gross Receipts Tax, simplified here
    },
    "WV": { # Note: These often have flat weekly/monthly taxes not handled by income rate brackets
        "Charleston": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Huntington": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Parkersburg": [{"rate": 0.00, "maxIncome": float('inf')}],
        "Weirton": [{"rate": 0.00, "maxIncome": float('inf')}]
    }
}

# --- Process Raw Data into Decimal-Ready Format ---
FEDERAL_TAX_BRACKETS = decimalize_tax_data(FEDERAL_TAX_BRACKETS_RAW)
STATE_TAX_BRACKETS = decimalize_tax_data(STATE_TAX_BRACKETS_RAW)
CITY_TAX_RATES = decimalize_tax_data(CITY_TAX_RATES_RAW)


# --- FICA Rates (Ensure Decimal usage) ---
FICA_RATES = {
    "SOCIAL_SECURITY_RATE": Decimal("0.062"),
    "SOCIAL_SECURITY_LIMIT": Decimal("177300"),
    "MEDICARE_RATE": Decimal("0.0145"),
    "MEDICARE_ADDITIONAL_RATE": Decimal("0.009"),
    "MEDICARE_ADDITIONAL_THRESHOLDS": {
        "single": Decimal("200000"),
        "marriedJointly": Decimal("250000"),
        "marriedSeparately": Decimal("125000"),
        "headOfHousehold": Decimal("200000"),
    }
}

# --- SDI Rates (Ensure Decimal usage) ---
SDI_RATES = {
    "CA": {"rate": Decimal("0.011"), "maxWage": Decimal("160174"), "maxContribution": Decimal("1761.91")},
    "NJ": {"rate": Decimal("0.000"), "maxWage": Decimal("161400"), "maxContribution": Decimal("0")},
    "NY": {"rate": Decimal("0.005"), "maxWage": None, "maxWeeklyDeduction": Decimal("0.60")},
    "RI": {"rate": Decimal("0.012"), "maxWage": Decimal("87000"), "maxContribution": Decimal("1044")},
    "HI": {"rate": Decimal("0.005"), "maxWage": None, "maxWeeklyDeduction": Decimal("6.82")}
}

# --- Helper Functions ---
def to_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    """Safely convert a value to Decimal."""
    if isinstance(value, Decimal):
        return value
    try:
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '')
        if not value: # Handle empty string after cleaning
            return default
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return default

# --- Data Classes ---
@dataclass
class ScenarioInputs:
    controls: Dict[str, ft.Control] = field(default_factory=dict)
    @property
    def work_state(self) -> str: return self.controls.get("work_state_dd", ft.Dropdown()).value or ""
    @property
    def residence_state(self) -> str: return self.controls.get("residence_state_dd", ft.Dropdown()).value or ""
    @property
    def work_city(self) -> str: return self.controls.get("work_city_dd", ft.Dropdown()).value or "N/A"
    @property
    def health_insurance(self) -> Decimal: return to_decimal(self.controls.get("health_tf", ft.TextField()).value)
    @property
    def dental_vision(self) -> Decimal: return to_decimal(self.controls.get("dental_tf", ft.TextField()).value)
    @property
    def hsa(self) -> Decimal: return to_decimal(self.controls.get("hsa_tf", ft.TextField()).value)
    @property
    def fsa(self) -> Decimal: return to_decimal(self.controls.get("fsa_tf", ft.TextField()).value)
    @property
    def retirement_401k(self) -> Decimal: return to_decimal(self.controls.get("retire_tf", ft.TextField()).value)
    @property
    def other_pretax(self) -> Decimal: return to_decimal(self.controls.get("other_tf", ft.TextField()).value)
    @property
    def total_benefit_deductions(self) -> Decimal:
        return (self.health_insurance + self.dental_vision + self.hsa +
                self.fsa + self.retirement_401k + self.other_pretax)

@dataclass
class CalculationResult:
    scenario_id: int
    gross_pretax_income: Decimal
    federal_tax: Decimal
    state_tax_work: Decimal
    state_tax_residence: Decimal
    city_tax: Decimal
    social_security_tax: Decimal
    medicare_tax: Decimal
    sdi_tax: Decimal
    total_benefit_deductions: Decimal
    total_tax: Decimal
    net_income: Decimal
    work_state: str
    residence_state: str
    post_tax_target: Decimal

# --- Core Calculation Logic ---
class TaxCalculator:
    def __init__(self):
        self.MAX_ITERATIONS = 150
        self.TOLERANCE = Decimal('0.50')
        self.ADJUSTMENT_FACTOR = Decimal('0.7')

    def calculate_income_tax(self, income: Decimal, brackets: List[Dict]) -> Decimal:
        if not brackets or income <= 0: return Decimal('0')
        tax = Decimal('0')
        income_in_previous_brackets = Decimal('0')
        for bracket in brackets:
            lower_bound = income_in_previous_brackets
            upper_bound_str = bracket["maxIncome"]
            upper_bound = Decimal('Infinity') if upper_bound_str == 'inf' else Decimal(upper_bound_str)
            if income <= lower_bound: break
            taxable_in_this_bracket = min(income, upper_bound) - lower_bound
            if taxable_in_this_bracket > 0:
                tax += taxable_in_this_bracket * Decimal(bracket["rate"])
            income_in_previous_brackets = upper_bound
            if upper_bound == Decimal('Infinity'): break
        return max(tax, Decimal('0'))

    def calculate_fica(self, gross_income: Decimal, filing_status: str) -> tuple[Decimal, Decimal]:
        gross_income = max(gross_income, Decimal('0'))
        taxable_for_ss = min(gross_income, FICA_RATES["SOCIAL_SECURITY_LIMIT"])
        social_security_tax = taxable_for_ss * FICA_RATES["SOCIAL_SECURITY_RATE"]
        medicare_tax = gross_income * FICA_RATES["MEDICARE_RATE"]
        additional_threshold = FICA_RATES["MEDICARE_ADDITIONAL_THRESHOLDS"][filing_status]
        if gross_income > additional_threshold:
            medicare_tax += (gross_income - additional_threshold) * FICA_RATES["MEDICARE_ADDITIONAL_RATE"]
        return social_security_tax, medicare_tax

    def calculate_sdi(self, gross_income: Decimal, work_state: str) -> Decimal:
        gross_income = max(gross_income, Decimal('0'))
        if work_state not in SDI_RATES: return Decimal('0')
        sdi_info = SDI_RATES[work_state]
        if work_state in ('NY', 'HI'):
            weekly_max = sdi_info["maxWeeklyDeduction"]
            return weekly_max * Decimal('52')
        taxable_wage = gross_income
        if sdi_info["maxWage"] is not None:
             taxable_wage = min(gross_income, sdi_info["maxWage"])
        sdi_tax = taxable_wage * sdi_info["rate"]
        if sdi_info["maxContribution"] is not None:
            sdi_tax = min(sdi_tax, sdi_info["maxContribution"])
        return max(sdi_tax, Decimal('0'))

    def solve_for_gross_income(self, target_net: Decimal, inputs: ScenarioInputs,
                             filing_status: str) -> CalculationResult:
        if not inputs.work_state or not inputs.residence_state:
             raise ValueError("Work State and Residence State must be selected.")
        estimated_initial_taxes = target_net * Decimal('0.40')
        current_guess = target_net + inputs.total_benefit_deductions + estimated_initial_taxes
        iteration = 0
        last_guess = Decimal('0')
        federal_tax, state_tax_work, state_tax_residence, city_tax = (Decimal('0'),)*4
        social_security_tax, medicare_tax, sdi_tax = (Decimal('0'),)*3
        total_benefits, total_tax, calculated_net = (Decimal('0'),)*3
        difference = Decimal('Infinity')

        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            current_guess = max(current_guess, Decimal('0'))
            total_benefits = inputs.total_benefit_deductions
            social_security_tax, medicare_tax = self.calculate_fica(current_guess, filing_status)
            sdi_tax = self.calculate_sdi(current_guess, inputs.work_state)
            sdi_tf = inputs.controls.get("sdi_tf")
            if sdi_tf: sdi_tf.value = self.format_currency(sdi_tax)

            taxable_income_for_income_tax = max(Decimal('0'), current_guess - total_benefits)
            federal_tax = self.calculate_income_tax(taxable_income_for_income_tax, FEDERAL_TAX_BRACKETS.get(filing_status, []))
            state_tax_work = self.calculate_income_tax(taxable_income_for_income_tax, STATE_TAX_BRACKETS.get(inputs.work_state, []))
            state_tax_residence = Decimal('0')
            if inputs.work_state != inputs.residence_state:
                # Calculate potential tax liability in the residence state
                potential_residence_tax = self.calculate_income_tax(taxable_income_for_income_tax, STATE_TAX_BRACKETS.get(inputs.residence_state, []))
                # Apply simplified reciprocity: Resident state tax is the potential tax minus work state tax paid (minimum zero)
                state_tax_residence = max(Decimal('0'), potential_residence_tax - state_tax_work)
            city_tax = Decimal('0')
            if inputs.work_city != "N/A" and inputs.work_state in CITY_TAX_RATES:
                city_brackets = CITY_TAX_RATES[inputs.work_state].get(inputs.work_city)
                if city_brackets: city_tax = self.calculate_income_tax(taxable_income_for_income_tax, city_brackets)

            total_tax = (federal_tax + state_tax_work + state_tax_residence + city_tax +
                         social_security_tax + medicare_tax + sdi_tax)
            calculated_net = current_guess - total_tax - total_benefits
            difference = calculated_net - target_net

            # Check for convergence
            if abs(difference) <= self.TOLERANCE: break

            # Adjust the guess for the next iteration.
            # Move the guess closer to the target by a fraction of the difference.
            # This is a simple fixed-point iteration / gradient adjustment approach.
            adjustment = difference * self.ADJUSTMENT_FACTOR
            current_guess -= adjustment
            last_guess = current_guess # Keep track of the last guess (though not currently used for convergence logic)

        if iteration >= self.MAX_ITERATIONS and abs(difference) > self.TOLERANCE:
            print(f"Warning: Failed to converge for scenario after {self.MAX_ITERATIONS} iterations. Last Diff: {difference}")

        return CalculationResult(
            scenario_id=0,
            gross_pretax_income=current_guess.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            federal_tax=federal_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            state_tax_work=state_tax_work.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            state_tax_residence=state_tax_residence.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            city_tax=city_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            social_security_tax=social_security_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            medicare_tax=medicare_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            sdi_tax=sdi_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            total_benefit_deductions=total_benefits.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            total_tax=total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            net_income=calculated_net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            work_state=inputs.work_state,
            residence_state=inputs.residence_state,
            post_tax_target=target_net
        )

    def format_currency(self, amount: Decimal) -> str:
        if amount is None: return "$0.00"
        return f"${amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"

# --- Flet UI Application Class ---
class TaxCalculatorApp:
    def __init__(self):
        self.calculator = TaxCalculator()
        self.scenarios_data: List[ScenarioInputs] = []
        self.scenario_containers: List[ft.Container] = []
        self.max_scenarios = 4
        self.page: Optional[ft.Page] = None
        self.add_scenario_btn: Optional[ft.ElevatedButton] = None
        # Renamed results_column to results_area, initialized as a standard Column
        self.results_area: Optional[ft.Column] = ft.Column(spacing=10)
        self.scenarios_row: Optional[ft.Row] = None

        self.desired_income_tf: Optional[ft.TextField] = None
        self.filing_status_dd: Optional[ft.Dropdown] = None

        self.filing_statuses = ["single", "marriedJointly", "marriedSeparately", "headOfHousehold"]
        self.states = sorted(list(STATE_TAX_BRACKETS.keys()))
        self.cities_by_state = {state: list(cities.keys()) for state, cities in CITY_TAX_RATES.items()}

    def _create_benefit_tf(self, label: str, key: str) -> ft.TextField:
        """Helper to create a benefit text field."""
        return ft.TextField(
            label=label,
            value="0",
            prefix_text="$",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]*", replacement_string=""),
            data=key,
            dense=True,
            # select_all_on_focus=True # REMOVED
        )

    def create_scenario_controls(self, scenario_id: int) -> ScenarioInputs:
        """Creates the Flet controls for a scenario."""
        controls_dict = {}
        
        work_state_dd = ft.Dropdown(
            label="Work State", options=[ft.dropdown.Option(state) for state in self.states],
            hint_text="Select State",
            dense=False,
            content_padding=ft.padding.symmetric(vertical=10, horizontal=10),
            expand=True # Allow dropdown to expand horizontally
        )
        controls_dict["work_state_dd"] = work_state_dd
        
        residence_state_dd = ft.Dropdown(
            label="Living State", options=[ft.dropdown.Option(state) for state in self.states],
            hint_text="Select State",
            dense=False,
            content_padding=ft.padding.symmetric(vertical=10, horizontal=10),
            expand=True # Allow dropdown to expand horizontally
        )
        controls_dict["residence_state_dd"] = residence_state_dd
        
        work_city_dd = ft.Dropdown(
            label="Work City", options=[ft.dropdown.Option("N/A")], value="N/A", visible=False,
            dense=False,
            content_padding=ft.padding.symmetric(vertical=10, horizontal=10),
            expand=True # Allow dropdown to expand horizontally
            # Note: Dropdown search (Issue #4) is not implemented here.
        )
        controls_dict["work_city_dd"] = work_city_dd
        
        sdi_tf = ft.TextField(
            label="SDI/PFML (Auto)", value="$0.00", read_only=True, visible=False,
            text_align=ft.TextAlign.RIGHT, dense=True,
            border_color=ft.Colors.with_opacity(0.3, ft.Colors.ON_SURFACE),
            expand=True # Allow textfield to expand horizontally
        )
        controls_dict["sdi_tf"] = sdi_tf
        work_state_dd.on_change=lambda e: self.on_work_state_change(e, work_city_dd, sdi_tf)

        # Create benefit text fields
        benefit_fields = [
            ("Health Ins", "health"),
            ("Dental/Vision", "dental"),
            ("HSA", "hsa"),
            ("FSA", "fsa"),
            ("401k/403b", "retire"),
            ("Other PreTax", "other")
        ]
        
        for label, key in benefit_fields:
            controls_dict[f"{key}_tf"] = ft.TextField(
                label=label,
                value="0",
                prefix_text="$",
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]*", replacement_string=""),
                data=key,
                dense=True,
                expand=True
            )
        return ScenarioInputs(controls=controls_dict)

    def create_scenario_container(self, scenario_id: int, scenario_data: ScenarioInputs) -> ft.Container:
        """Creates the visual container for a scenario."""
        controls = scenario_data.controls
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Scenario {scenario_id + 1}", size=16, weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE, tooltip="Remove Scenario",
                        visible=scenario_id > 0,
                        on_click=lambda e, sid=scenario_id: self.remove_scenario(e, sid)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=30),
                # Use simple Row for state/city dropdowns, allow expansion
                ft.Row(
                    [
                        controls["work_state_dd"], # expand=True set inside control creation
                        controls["residence_state_dd"], # expand=True set inside control creation
                    ],
                    spacing=5, # Add spacing between dropdowns
                    # alignment=ft.MainAxisAlignment.START # Align to start
                ),
                # Separate Row for City and SDI, only City is initially hidden
                ft.Row(
                    [
                         controls["work_city_dd"], # expand=True set inside control creation
                         controls["sdi_tf"], # expand=True set inside control creation
                    ],
                     spacing=5,
                    # alignment=ft.MainAxisAlignment.START
                ),
                ft.Divider(height=5, color=ft.Colors.with_opacity(0.5, ft.Colors.GREY)),
                ft.Text("Pre-tax Benefit Deductions (Annual)", weight=ft.FontWeight.BOLD, size=12),
                ft.ResponsiveRow([
                    ft.Column([controls["health_tf"]], col={"xs": 6, "lg":4}),
                    ft.Column([controls["dental_tf"]], col={"xs": 6, "lg":4}),
                    ft.Column([controls["hsa_tf"]], col={"xs": 6, "lg":4}),
                    ft.Column([controls["fsa_tf"]], col={"xs": 6, "lg":4}),
                    ft.Column([controls["retire_tf"]], col={"xs": 6, "lg":4}),
                    ft.Column([controls["other_tf"]], col={"xs": 6, "lg":4}),
                ], spacing=5, run_spacing=5),
            ], spacing=8),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=6,
            margin=ft.margin.only(right=10),
            width=380 # Keep fixed width for horizontal scroll
        )
        return container

    def on_work_state_change(self, e, work_city_dd: ft.Dropdown, sdi_tf: ft.TextField):
        """Handle work state selection changes."""
        state = e.control.value
        work_city_dd.options = [ft.dropdown.Option("N/A")]
        if state in self.cities_by_state:
            work_city_dd.options.extend([ft.dropdown.Option(city) for city in self.cities_by_state[state]])
            work_city_dd.visible = True # Make sure visibility is set correctly
        else:
            work_city_dd.value = "N/A"
            work_city_dd.visible = False # Make sure visibility is set correctly
        sdi_tf.visible = state in SDI_RATES
        sdi_tf.value = "$0.00"
        if self.page: self.page.update() # Update the page to reflect visibility changes

    def remove_scenario(self, e, scenario_id_to_remove: int):
        """Remove a scenario from the list and UI."""
        if len(self.scenarios_data) <= 1: return

        current_index = -1
        if scenario_id_to_remove < len(self.scenario_containers):
             container_to_remove = self.scenario_containers[scenario_id_to_remove]
             if self.scenarios_row and container_to_remove in self.scenarios_row.controls:
                 current_index = self.scenarios_row.controls.index(container_to_remove)
                 self.scenarios_data.pop(scenario_id_to_remove)
                 self.scenario_containers.pop(scenario_id_to_remove)
                 self.scenarios_row.controls.pop(current_index)
             else:
                 print(f"Error: Container for scenario {scenario_id_to_remove} not found in UI row.")
                 return
        else:
             print(f"Error: Invalid scenario ID {scenario_id_to_remove} for removal.")
             return

        for i, container in enumerate(self.scenario_containers):
            title_row = container.content.controls[0]
            title_text = title_row.controls[0]
            remove_button = title_row.controls[1]
            title_text.value = f"Scenario {i + 1}"
            remove_button.visible = i > 0
            remove_button.on_click=lambda _, sid=i: self.remove_scenario(_, sid)

        self.add_scenario_btn.visible = len(self.scenarios_data) < self.max_scenarios
        if self.page: self.page.update()

    def create_result_card(self, result: CalculationResult) -> ft.Container:
        """Create a result card displaying calculation results."""
        format_currency = self.calculator.format_currency
        gross = result.gross_pretax_income
        rows = []
        def add_row(label, value, show_perc=True):
             value_dec = to_decimal(value)
             perc_str = f"{(value_dec / gross * 100):.1f}%" if gross > 0 and show_perc else ""
             rows.append(ft.DataRow(cells=[
                 ft.DataCell(ft.Text(label, size=11)),
                 ft.DataCell(ft.Text(format_currency(value_dec), size=11)),
                 ft.DataCell(ft.Text(perc_str, size=11))
             ]))
        # add_row("Gross Pre-Tax Income", gross, show_perc=False)
        add_row("Net Income", result.net_income)
        add_row("Federal Income Tax", result.federal_tax)
        add_row("Social Security Tax", result.social_security_tax)
        add_row("Medicare Tax", result.medicare_tax)
        add_row("State Tax (Work)", result.state_tax_work)
        if result.state_tax_residence > 0: add_row("State Tax (Residence)", result.state_tax_residence)
        if result.city_tax > 0: add_row("City Tax", result.city_tax)
        if result.sdi_tax > 0: add_row("SDI/PFML Tax", result.sdi_tax)
        add_row("Pre-Tax Benefits", result.total_benefit_deductions)
        add_row("Total Tax", result.total_tax)
        #
        net_diff = result.net_income - result.post_tax_target
        diff_color = ft.Colors.RED if abs(net_diff) > self.calculator.TOLERANCE else ft.Colors.GREEN

        return ft.Container(
            content=ft.Column([
                ft.Text(f"Scenario {result.scenario_id + 1} ({result.work_state}/{result.residence_state})", size=14, weight=ft.FontWeight.BOLD),
                ft.DataTable(
                    # column_spacing=15, 
                    heading_row_height=30, 
                    data_row_min_height=25,
                    columns=[
                        ft.DataColumn(ft.Text("Item", size=11)),
                        ft.DataColumn(ft.Text("Amount", size=11), numeric=True),
                        ft.DataColumn(ft.Text("% Gross", size=11), numeric=True)
                    ],
                    rows=rows
                ),
                ft.Divider(height=3),
                ft.Row([ft.Text("Gross Pre-Tax Income:", weight=ft.FontWeight.BOLD, size=11), ft.Text(format_currency(gross), size=11)]),
            ], spacing=3),
            padding=10, border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=6 # Removed margin and width, handled in handler now
            # margin=ft.margin.only(bottom=10) # Removed
        )

    def create_comparison_chart(self, results: List[CalculationResult]) -> Optional[ft.Container]:
        """Create a stacked bar chart comparing scenarios using ft.PlotlyChart."""
        if not results: return None
        scenarios = [f"Scenario {r.scenario_id + 1} - {r.work_state}/{r.residence_state}" for r in results]
        fig = go.Figure()
        components = [
            ("Federal Tax", "federal_tax", 'rgba(214, 40, 40, 0.8)'),
            ("Social Security", "social_security_tax", 'rgba(60, 100, 170, 0.8)'),
            ("Medicare", "medicare_tax", 'rgba(0, 150, 190, 0.8)'),
            ("State Tax (Work)", "state_tax_work", 'rgba(240, 180, 0, 0.8)'),
            ("State Tax (Res)", "state_tax_residence", 'rgba(255, 140, 0, 0.8)'),
            ("City Tax", "city_tax", 'rgba(150, 80, 200, 0.8)'),
            ("SDI/PFML", "sdi_tax", 'rgba(180, 180, 180, 0.8)'),
            ("Pre-Tax Benefits", "total_benefit_deductions", 'rgba(70, 180, 70, 0.8)')
        ]
        for name, attr, color in components:
            values = [getattr(r, attr, Decimal('0')) for r in results]
            if any(v > Decimal('0.01') for v in values):
                fig.add_trace(go.Bar(name=name, x=scenarios, y=[float(v) for v in values], marker_color=color, hovertemplate='%{y:$,.2f}<extra></extra>'))
        fig.update_layout(
            barmode='stack', title_text="Tax & Deduction Comparison", yaxis_title="Amount (USD)",
            yaxis_tickprefix="$", yaxis_tickformat=",.0f",
            # Move legend below the chart, centered horizontally
            legend=dict(
                orientation="h",
                yanchor="top", # Anchor legend top to the y position
                y=-0.2,      # Position legend below x-axis (adjust as needed)
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            margin=dict(l=10, r=10, t=40, b=100), # Further increase bottom margin for legend + rotated labels
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            # xaxis_tickangle=-45 # Rotate x-axis labels
        )
        fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
        chart_control = PlotlyChart(fig, expand=True)
        # Ensure the container itself expands horizontally
        return ft.Container(content=chart_control, margin=ft.margin.only(top=15), height=400, expand=True)

    def calculate_scenarios_handler(self, e):
        """Event handler for the calculate button."""
        # Use results_area instead of results_column
        if not self.page or not self.results_area: return
        self.results_area.controls.clear()
        loading_indicator = ft.ProgressRing(width=20, height=20, stroke_width=2)
        self.results_area.controls.append(ft.Row([loading_indicator, ft.Text("Calculating...")], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

        try:
            desired_income_str = self.desired_income_tf.value if self.desired_income_tf else "0"
            filing_status = self.filing_status_dd.value if self.filing_status_dd else ""
            desired_income = to_decimal(desired_income_str)
            if desired_income <= 0: self.show_error("Desired income must be positive."); self.results_area.controls.clear(); self.page.update(); return
            if not filing_status: self.show_error("Please select a filing status."); self.results_area.controls.clear(); self.page.update(); return
        except (AttributeError, InvalidOperation) as err:
             self.show_error(f"Could not read global inputs: {err}"); self.results_area.controls.clear(); self.page.update(); return

        results = []
        has_errors = False
        # Clear loading indicator before adding results
        self.results_area.controls.clear()

        result_cards = []
        error_cards = []
        for i, scenario_data in enumerate(self.scenarios_data):
            try:
                result = self.calculator.solve_for_gross_income(desired_income, scenario_data, filing_status)
                result.scenario_id = i
                results.append(result)
                result_card = self.create_result_card(result)
                # Add fixed width to result cards for horizontal layout
                result_card.width = 350 # Adjust width as needed
                result_card.margin = ft.margin.only(right=10) # Add spacing between cards
                result_cards.append(result_card)
            except (ValueError, InvalidOperation) as calc_err:
                has_errors = True
                error_card = ft.Container(
                    content=ft.Column([
                         ft.Text(f"Scenario {i + 1} Error", color=ft.Colors.ERROR, weight=ft.FontWeight.BOLD),
                         ft.Text(str(calc_err), size=11)
                    ]), padding=10, border=ft.border.all(1, ft.Colors.ERROR), border_radius=6,
                    width=350, margin=ft.margin.only(right=10) # Match width/margin
                )
                error_cards.append(error_card)

        # Create a scrollable Row for result/error cards
        results_row = ft.Row(
            controls=result_cards + error_cards, # Display results first, then errors
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START # Align cards to the top
        )
        # Add the results row directly to the results_area
        self.results_area.controls.append(results_row)

        if results:
            chart_container = self.create_comparison_chart(results)
             # Add the chart container directly to the results_area
            if chart_container: self.results_area.controls.append(chart_container)

        if results or has_errors:
             # Check if disclaimer already exists in the results_area
             disclaimer_exists = any(isinstance(c, ft.Container) and isinstance(c.content, ft.Text) and "Disclaimer" in c.content.value for c in self.results_area.controls if not isinstance(c, ft.Row))
             if not disclaimer_exists:
                 disclaimer = ft.Text(
                    "Disclaimer: Estimates based on simplified 2025 rules. Does not include all deductions/credits. Consult a tax professional.",
                    size=10, italic=True, color=ft.Colors.ON_SURFACE_VARIANT
                 )
                  # Add the disclaimer container directly to the results_area
                 self.results_area.controls.append(ft.Container(disclaimer, margin=ft.margin.only(top=10)))

        self.page.update()

    def show_error(self, message: str):
        """Display an error message using the page banner."""
        if not self.page: return
        self.page.show_snack_bar(
             ft.SnackBar(ft.Text(message), open=True, bgcolor=ft.Colors.ERROR_CONTAINER)
        )

    def close_banner(self, e):
        if not self.page or not self.page.banner: return
        self.page.banner.open = False
        self.page.update()

    def add_scenario_handler(self, e):
        """Add a new scenario UI and data structure."""
        if len(self.scenarios_data) < self.max_scenarios:
            scenario_id = len(self.scenarios_data)
            new_scenario_data = self.create_scenario_controls(scenario_id)
            self.scenarios_data.append(new_scenario_data)
            new_scenario_container = self.create_scenario_container(scenario_id, new_scenario_data)
            self.scenario_containers.append(new_scenario_container)

            if self.scenarios_row:
                 self.scenarios_row.controls.append(new_scenario_container)

            self.add_scenario_btn.visible = len(self.scenarios_data) < self.max_scenarios
            if self.page: self.page.update()

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Compact Post-Tax Income Calculator (2025)"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 10
        page.vertical_alignment = ft.MainAxisAlignment.START

        # --- Global Inputs ---
        self.desired_income_tf = ft.TextField(
            label="Desired Annual Post-Tax Income", value="500000", prefix_text="$",
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]*", replacement_string=""),
            dense=False,
            content_padding=ft.padding.symmetric(vertical=10, horizontal=10),
            expand=True,
            autofocus=True  # First field gets autofocus
        )
        self.filing_status_dd = ft.Dropdown(
            label="Filing Status", value="single",
            content_padding=ft.padding.symmetric(vertical=10, horizontal=10),
            dense=False,
            expand=True,
            options=[
                ft.dropdown.Option("single", "Single"),
                ft.dropdown.Option("marriedJointly", "Married Filing Jointly"),
                ft.dropdown.Option("marriedSeparately", "Married Filing Separately"),
                ft.dropdown.Option("headOfHousehold", "Head of Household")
            ]
        )
        global_settings_container = ft.Container(
            content=ft.Row([
                ft.Column([self.desired_income_tf], expand=True), # Changed from ResponsiveRow to Row with expand
                ft.Column([self.filing_status_dd], expand=True)
            ], spacing=10),
            padding=10, border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=6, margin=ft.margin.only(bottom=15)
        )

        # --- Scenarios ---
        first_scenario_data = self.create_scenario_controls(0)
        self.scenarios_data.append(first_scenario_data)
        first_scenario_container = self.create_scenario_container(0, first_scenario_data)
        self.scenario_containers.append(first_scenario_container)

        self.scenarios_row = ft.Row(
            controls=[first_scenario_container],
            scroll=ft.ScrollMode.ADAPTIVE, spacing=10
        )

        self.add_scenario_btn = ft.ElevatedButton(
            "Add Scenario", icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self.add_scenario_handler,
            visible=len(self.scenarios_data) < self.max_scenarios,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), height=35
        )

        # --- Calculate Button ---
        calculate_btn = ft.ElevatedButton(
            "Calculate All Scenarios", icon=ft.Icons.CALCULATE,
            on_click=self.calculate_scenarios_handler,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5)),
            height=40,
        )

        # --- Page Layout ---
        page.add(
            ft.Column(
                [
                    ft.Text("Advanced Post-Tax Income Calculator (2025)", size=22, weight=ft.FontWeight.BOLD),
                    global_settings_container,
                    ft.Row([
                        ft.Text("Scenarios", size=18, weight=ft.FontWeight.BOLD),
                        self.add_scenario_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(self.scenarios_row, margin=ft.margin.only(top=5, bottom=15)),
                    ft.Container(calculate_btn, alignment=ft.alignment.center),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(ft.Text("Results", size=18, weight=ft.FontWeight.BOLD), margin=ft.margin.only(top=10)),
                    # Ensure the container holding the results_area expands
                    ft.Container(self.results_area, padding=ft.padding.only(bottom=20), expand=True)
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True
            )
        )
        page.update()

# --- Main Execution ---
def run_app():
    # 
    ft.app(target=TaxCalculatorApp().main)

if __name__ == "__main__":
    run_app()

import os


# =============================
# Data source configuration
# =============================

# Default CSV path. You can override this by setting the BLOOD_PRESSURE_CSV
# environment variable before running the app.
DATA_PATH = os.environ.get("BLOOD_PRESSURE_CSV", "Blood_Pressure.csv")


# =============================
# Dataset column configuration
# =============================

# Columns used by the dashboard.
# If the CSV contains extra columns, they are ignored during loading.
ALLOWED_COLUMNS = [
    "Patient_ID",
    "Year",
    "Country",
    "WHO_Region",
    "Income_Level",
    "ISO2_Country_Code",
    "Age",
    "Age_Group",
    "Sex",
    "BMI",
    "BMI_Category",
    "Smoking_Status",
    "Physical_Activity",
    "Diet_Salt_Intake",
    "Stress_Level",
    "Diabetes",
    "Family_Hx_Hypertension",
    "Systolic_BP_mmHg",
    "Diastolic_BP_mmHg",
    "Pulse_Pressure_mmHg",
    "Mean_Arterial_Pressure",
    "Heart_Rate_bpm",
    "BP_Category",
    "Country_HTN_Prevalence_pct",
    "Age_Category",
    "BP_Category_2",
]


# Columns that should be converted to numeric values when the data loads.
NUMERIC_COLUMNS = [
    "Year",
    "Age",
    "BMI",
    "Systolic_BP_mmHg",
    "Diastolic_BP_mmHg",
    "Pulse_Pressure_mmHg",
    "Mean_Arterial_Pressure",
    "Heart_Rate_bpm",
    "Country_HTN_Prevalence_pct",
]


# =============================
# Map metric configuration
# =============================

# Metrics available in the map dropdown.
# Keys are dataframe column names.
# Values are user-friendly labels shown in the dashboard.
MAP_METRICS = {
    "Country_HTN_Prevalence_pct": "HTN prevalence (%)",
    "Systolic_BP_mmHg": "Mean systolic BP (mmHg)",
    "Diastolic_BP_mmHg": "Mean diastolic BP (mmHg)",
    "Pulse_Pressure_mmHg": "Mean pulse pressure (mmHg)",
    "Mean_Arterial_Pressure": "Mean arterial pressure (mmHg)",
    "Heart_Rate_bpm": "Mean heart rate (bpm)",
    "BMI": "Mean BMI",
    "Age": "Mean age",
}


# Default map metric used when the dashboard first loads or filters reset.
DEFAULT_MAP_METRIC = "Country_HTN_Prevalence_pct"


# =============================
# Color configuration
# =============================

# Custom teal color scale used by the choropleth map.
TEAL_SCALE = [
    [0.0, "#cfeeed"],
    [0.2, "#a8dddd"],
    [0.4, "#74c6c3"],
    [0.6, "#43aba7"],
    [0.8, "#1f8482"],
    [1.0, "#0b5f60"],
]
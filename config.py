import os

DATA_PATH = os.environ.get("BLOOD_PRESSURE_CSV", "Blood_Pressure.csv")

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

TEAL_SCALE = [
    [0.0, "#cfeeed"],
    [0.2, "#a8dddd"],
    [0.4, "#74c6c3"],
    [0.6, "#43aba7"],
    [0.8, "#1f8482"],
    [1.0, "#0b5f60"],
]
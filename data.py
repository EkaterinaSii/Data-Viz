import os
from typing import Optional, List

import pandas as pd

from config import ALLOWED_COLUMNS, NUMERIC_COLUMNS


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find '{path}'. Put Blood_Pressure.csv in the same folder "
            "or set BLOOD_PRESSURE_CSV to the full path."
        )

    df = pd.read_csv(path)

    available = [c for c in ALLOWED_COLUMNS if c in df.columns]
    missing = [c for c in ALLOWED_COLUMNS if c not in df.columns]

    if missing:
        print("Warning: missing columns:", missing)

    df = df[available].copy()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in df.columns:
        if col not in NUMERIC_COLUMNS:
            df[col] = df[col].astype("string").fillna("Unknown")

    return df


def dropdown_options(series: pd.Series) -> List[dict]:
    values = sorted(v for v in series.dropna().astype(str).unique() if v != "Unknown")
    return [{"label": v, "value": v} for v in values]


def apply_filters(
    df: pd.DataFrame,
    year_range: Optional[List[int]],
    sex: Optional[str],
    age_group: Optional[str],
    bmi_category: Optional[str],
    smoking: Optional[str],
    physical: Optional[str],
    salt: Optional[str],
    stress: Optional[str],
    diabetes: Optional[str],
    family_hx: Optional[str],
) -> pd.DataFrame:
    dff = df.copy()

    if year_range and "Year" in dff.columns:
        dff = dff[(dff["Year"] >= year_range[0]) & (dff["Year"] <= year_range[1])]

    if sex:
        dff = dff[dff["Sex"] == sex]

    if age_group:
        dff = dff[dff["Age_Group"] == age_group]

    if bmi_category:
        dff = dff[dff["BMI_Category"] == bmi_category]

    if smoking:
        dff = dff[dff["Smoking_Status"] == smoking]

    if physical:
        dff = dff[dff["Physical_Activity"] == physical]

    if salt:
        dff = dff[dff["Diet_Salt_Intake"] == salt]

    if stress:
        dff = dff[dff["Stress_Level"] == stress]

    if diabetes:
        dff = dff[dff["Diabetes"] == diabetes]

    if family_hx:
        dff = dff[dff["Family_Hx_Hypertension"] == family_hx]

    return dff


def aggregate_for_map(dff: pd.DataFrame, metric: str) -> pd.DataFrame:
    columns = [
        "Country",
        metric,
        "Patients",
        "WHO_Region",
        "Income_Level",
        "ISO2_Country_Code",
    ]

    if dff.empty:
        return pd.DataFrame(columns=columns)

    agg = (
        dff.groupby("Country", dropna=False)
        .agg(
            **{
                metric: (metric, "mean"),
                "Patients": ("Patient_ID", "count"),
                "WHO_Region": (
                    "WHO_Region",
                    lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown",
                ),
                "Income_Level": (
                    "Income_Level",
                    lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown",
                ),
                "ISO2_Country_Code": (
                    "ISO2_Country_Code",
                    lambda x: x.dropna().iloc[0] if not x.dropna().empty else "",
                ),
            }
        )
        .reset_index()
    )

    agg[metric] = agg[metric].round(2)
    agg["ISO2_Country_Code"] = agg["ISO2_Country_Code"].astype(str).str.upper()

    return agg
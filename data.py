import os
from typing import Optional, List

import pandas as pd

from config import ALLOWED_COLUMNS, NUMERIC_COLUMNS


def load_data(path: str) -> pd.DataFrame:
    """
    Loads the blood pressure CSV file and prepares it for the dashboard.

    This function:
    - checks that the CSV file exists
    - reads the data into a pandas dataframe
    - keeps only the dashboard columns
    - creates missing expected columns if needed
    - converts numeric columns to numeric values
    - fills missing categorical values with "Unknown"

    Parameters:
    - path: Path to the CSV file.

    Returns:
    - A cleaned pandas dataframe ready for filtering and visualization.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find '{path}'. Put Blood_Pressure.csv in the same folder "
            "or set BLOOD_PRESSURE_CSV to the full path."
        )

    df = pd.read_csv(path)

    missing_columns = [
        column
        for column in ALLOWED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        print("Warning: missing columns:", missing_columns)

    # Create missing expected columns so the rest of the app does not fail.
    for column in missing_columns:
        df[column] = pd.NA

    # Keep only the columns used by the dashboard, in the expected order.
    df = df[ALLOWED_COLUMNS].copy()

    # Convert numeric columns safely.
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert categorical/text columns safely.
    for column in df.columns:
        if column not in NUMERIC_COLUMNS:
            df[column] = df[column].astype("string").fillna("Unknown")

    return df


def dropdown_options(series: pd.Series) -> List[dict]:
    """
    Creates Dash dropdown options from a dataframe column.

    The function:
    - removes missing values
    - removes "Unknown"
    - sorts values alphabetically
    - returns options in Dash format

    Parameters:
    - series: Pandas series used to build dropdown values.

    Returns:
    - A list of dictionaries with "label" and "value" keys.
    """
    values = sorted(
        value
        for value in series.dropna().astype(str).unique()
        if value != "Unknown"
    )

    return [
        {
            "label": value,
            "value": value,
        }
        for value in values
    ]


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
    """
    Applies all selected dashboard filters to the dataframe.

    Filters include:
    - year range
    - sex
    - age group
    - BMI category
    - smoking status
    - physical activity
    - diet salt intake
    - stress level
    - diabetes
    - family history of hypertension

    Parameters:
    - df: Full dashboard dataframe.
    - year_range: Selected year range from the slider.
    - sex: Selected sex filter.
    - age_group: Selected age group filter.
    - bmi_category: Selected BMI category filter.
    - smoking: Selected smoking status filter.
    - physical: Selected physical activity filter.
    - salt: Selected diet salt intake filter.
    - stress: Selected stress level filter.
    - diabetes: Selected diabetes filter.
    - family_hx: Selected family history filter.

    Returns:
    - A filtered pandas dataframe.
    """
    dff = df.copy()

    if year_range and len(year_range) == 2 and "Year" in dff.columns:
        dff = dff[
            (dff["Year"] >= year_range[0])
            & (dff["Year"] <= year_range[1])
        ]

    dff = filter_by_value(dff, "Sex", sex)
    dff = filter_by_value(dff, "Age_Group", age_group)
    dff = filter_by_value(dff, "BMI_Category", bmi_category)
    dff = filter_by_value(dff, "Smoking_Status", smoking)
    dff = filter_by_value(dff, "Physical_Activity", physical)
    dff = filter_by_value(dff, "Diet_Salt_Intake", salt)
    dff = filter_by_value(dff, "Stress_Level", stress)
    dff = filter_by_value(dff, "Diabetes", diabetes)
    dff = filter_by_value(dff, "Family_Hx_Hypertension", family_hx)

    return dff


def filter_by_value(
    df: pd.DataFrame,
    column: str,
    value: Optional[str],
) -> pd.DataFrame:
    """
    Filters a dataframe by one column and one selected value.

    If the value is empty or the column is missing, the dataframe is
    returned unchanged.

    Parameters:
    - df: Dataframe to filter.
    - column: Column name to filter by.
    - value: Selected value.

    Returns:
    - Filtered dataframe.
    """
    if value and column in df.columns:
        return df[df[column] == value]

    return df


def aggregate_for_map(dff: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    Aggregates filtered data by country for the choropleth map.

    For each country, this function calculates:
    - mean selected metric
    - patient count
    - most common WHO region
    - most common income level
    - first available ISO2 country code

    Parameters:
    - dff: Filtered dataframe.
    - metric: Numeric metric selected for the map.

    Returns:
    - Aggregated dataframe used by the map figure.
    """
    output_columns = [
        "Country",
        metric,
        "Patients",
        "WHO_Region",
        "Income_Level",
        "ISO2_Country_Code",
    ]

    if dff.empty or metric not in dff.columns or "Country" not in dff.columns:
        return pd.DataFrame(columns=output_columns)

    dff = dff.copy()

    # Make sure required grouping/display columns exist.
    for column in ["WHO_Region", "Income_Level", "ISO2_Country_Code"]:
        if column not in dff.columns:
            dff[column] = "Unknown"

    if "Patient_ID" not in dff.columns:
        dff["Patient_ID"] = range(1, len(dff) + 1)

    dff[metric] = pd.to_numeric(dff[metric], errors="coerce")

    agg = (
        dff.groupby("Country", dropna=False)
        .agg(
            **{
                metric: (metric, "mean"),
                "Patients": ("Patient_ID", "count"),
                "WHO_Region": ("WHO_Region", most_common_value),
                "Income_Level": ("Income_Level", most_common_value),
                "ISO2_Country_Code": ("ISO2_Country_Code", first_available_value),
            }
        )
        .reset_index()
    )

    agg[metric] = agg[metric].round(2)
    agg["ISO2_Country_Code"] = (
        agg["ISO2_Country_Code"]
        .astype(str)
        .str.upper()
    )

    return agg[output_columns]


def most_common_value(series: pd.Series) -> str:
    """
    Returns the most common non-missing value in a series.

    If no value is available, returns "Unknown".

    Parameters:
    - series: Pandas series.

    Returns:
    - Most common value as a string.
    """
    cleaned = series.dropna().astype(str)

    if cleaned.empty:
        return "Unknown"

    mode = cleaned.mode()

    if mode.empty:
        return "Unknown"

    return mode.iloc[0]


def first_available_value(series: pd.Series) -> str:
    """
    Returns the first non-missing value in a series.

    If no value is available, returns an empty string.

    Parameters:
    - series: Pandas series.

    Returns:
    - First available value as a string.
    """
    cleaned = series.dropna().astype(str)

    if cleaned.empty:
        return ""

    return cleaned.iloc[0]
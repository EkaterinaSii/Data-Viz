from typing import Optional, List

import pandas as pd
from dash import html

from config import MAP_METRICS


INFO_HELP = {
    "Avg systolic": [
        html.B("What it is: "),
        "\nSystolic blood pressure is the top number in a blood pressure reading. It reflects pressure in the arteries when the heart contracts.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\n90–119 mmHg is a typical adult range. \n120–129 mmHg is elevated. \n130 mmHg and above may suggest hypertension.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nHigher systolic pressure can increase the risk of heart disease, stroke, and kidney damage.",
    ],
    "Avg diastolic": [
        html.B("What it is: "),
        "\nDiastolic blood pressure is the bottom number in a blood pressure reading. It reflects pressure in the arteries when the heart relaxes between beats.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\n60–79 mmHg is commonly considered typical. \n80 mmHg or above may indicate hypertension.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nHigh diastolic pressure can strain blood vessels and raise cardiovascular risk over time.",
    ],
    "Avg MAP": [
        html.B("What it is: "),
        "\nMean arterial pressure (MAP) estimates the average pressure pushing blood through the arteries during one cardiac cycle.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\n70–100 mmHg is often considered adequate for organ perfusion in adults.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nToo high can stress blood vessels, while too low can reduce blood flow to vital organs.",
    ],
    "Avg pulse pressure": [
        html.B("What it is: "),
        "\nPulse pressure is the difference between systolic and diastolic pressure.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\n30–50 mmHg is common in many healthy adults.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nPersistently high pulse pressure may be linked with arterial stiffness and higher cardiovascular risk.",
    ],
    "Avg heart rate": [
        html.B("What it is: "),
        "\nHeart rate is the number of heartbeats per minute.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\nFor many adults at rest, around 60–100 bpm is a common reference range.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nPersistently high resting heart rate can be associated with stress, poor fitness, or heart problems.",
    ],
    "HTN prevalence": [
        html.B("What it is: "),
        "\nHypertension prevalence is the share of people in the dataset or country estimated to have high blood pressure.",
        html.Br(),
        html.Br(),
        html.B("Typical range: "),
        "\nHigher percentages suggest a larger population burden of cardiovascular risk.",
        html.Br(),
        html.Br(),
        html.B("Why it matters: "),
        "\nHigher prevalence can indicate greater expected risk of stroke, heart disease, and kidney complications at population level.",
    ],
    "BMI": [
        html.B("What it is: "),
        "\nBody mass index (BMI) relates weight to height.",
        html.Br(),
        html.Br(),
        html.B("Typical categories:"),
        "\nUnder 18.5: underweight\n"
        "18.5–24.9: healthy range\n"
        "25.0–29.9: overweight\n"
        "30 or more: obesity\n\n",
        html.B("Why it matters: "),
        "\nHigher BMI is often associated with greater risk of hypertension, diabetes, and cardiovascular disease.",
    ],
}


def help_icon(text):
    return html.Span(
        [
            html.Span("?", className="help-icon-mark"),
            html.Div(text, className="help-tooltip-box"),
        ],
        className="help-tooltip-wrap",
    )


def stat_card(label: str, value: str, tooltip=None):
    label_row = html.Div(
        [
            html.Span(label, className="stat-label-text"),
            help_icon(tooltip) if tooltip else None,
        ],
        className="stat-label-row",
    )

    return html.Div(
        [
            html.Div(label_row, className="stat-label"),
            html.Div(value, className="stat-value"),
        ],
        className="stat-card",
    )


def info_cards_for_df(dff: pd.DataFrame, country: Optional[str] = None) -> List:
    if dff.empty:
        return [html.Div("No data for the selected filters.", className="info-empty")]

    title = country if country else "Dataset overview"

    years = (
        f"{int(dff['Year'].min())}–{int(dff['Year'].max())}"
        if "Year" in dff.columns and dff["Year"].notna().any()
        else "N/A"
    )

    return [
        stat_card("Scope", title),
        stat_card("Patients", f"{len(dff):,}"),
        stat_card(
            "Countries",
            f"{dff['Country'].nunique():,}" if "Country" in dff.columns else "N/A",
        ),
        stat_card("Years", years),
        stat_card(
            "Avg systolic",
            f"{dff['Systolic_BP_mmHg'].mean():.1f} mmHg"
            if dff["Systolic_BP_mmHg"].notna().any()
            else "N/A",
            INFO_HELP["Avg systolic"],
        ),
        stat_card(
            "Avg diastolic",
            f"{dff['Diastolic_BP_mmHg'].mean():.1f} mmHg"
            if dff["Diastolic_BP_mmHg"].notna().any()
            else "N/A",
            INFO_HELP["Avg diastolic"],
        ),
        stat_card(
            "Avg MAP",
            f"{dff['Mean_Arterial_Pressure'].mean():.1f} mmHg"
            if dff["Mean_Arterial_Pressure"].notna().any()
            else "N/A",
            INFO_HELP["Avg MAP"],
        ),
        stat_card(
            "Avg pulse pressure",
            f"{dff['Pulse_Pressure_mmHg'].mean():.1f} mmHg"
            if dff["Pulse_Pressure_mmHg"].notna().any()
            else "N/A",
            INFO_HELP["Avg pulse pressure"],
        ),
        stat_card(
            "Avg heart rate",
            f"{dff['Heart_Rate_bpm'].mean():.1f} bpm"
            if dff["Heart_Rate_bpm"].notna().any()
            else "N/A",
            INFO_HELP["Avg heart rate"],
        ),
        stat_card(
            "HTN prevalence",
            f"{dff['Country_HTN_Prevalence_pct'].mean():.1f}%"
            if dff["Country_HTN_Prevalence_pct"].notna().any()
            else "N/A",
            INFO_HELP["HTN prevalence"],
        ),
        stat_card(
            "BMI",
            f"{dff['BMI'].mean():.1f}" if dff["BMI"].notna().any() else "N/A",
            INFO_HELP["BMI"],
        ),
    ]


def overview_note():
    return html.Div(
        [
            html.H3("Why this matters", className="panel-title"),
            html.P(
                "High blood pressure is one of the most important cardiovascular risk factors worldwide. "
                "It can increase the risk of stroke, heart disease, kidney damage, and other long-term complications. "
                "Looking at differences across countries and population groups helps reveal where the burden is highest "
                "and which combinations of factors may be linked to greater risk.\n\n"
                "This dashboard makes it easier to explore patterns in hypertension prevalence, systolic and diastolic blood pressure, "
                "pulse pressure, heart rate, BMI, and age. By comparing these measures across sex, age group, smoking status, "
                "physical activity, salt intake, stress level, diabetes, and family history, users can identify trends that may support "
                "prevention, early detection, and better public health decision-making.\n\n"
                "The goal is not only to describe the data, but also to help highlight populations that may benefit most from lifestyle "
                "interventions, screening programs, and more targeted treatment strategies.",
                className="overview-note-text",
            ),
        ],
        className="overview-note-wrap",
    )


def build_active_filters_box(
    metric,
    year_range,
    sex,
    age_group,
    bmi_category,
    smoking,
    physical,
    salt,
    stress,
    diabetes,
    family_hx,
    year_min,
    year_max,
    selected_country=None,
):
    chips = []

    if selected_country:
        chips.append(f"Country: {selected_country}")

    if metric:
        chips.append(f"Metric: {MAP_METRICS.get(metric, metric)}")

    if year_range and (year_range[0] != year_min or year_range[1] != year_max):
        chips.append(f"Years: {year_range[0]}–{year_range[1]}")

    if sex:
        chips.append(f"Sex: {sex}")

    if age_group:
        chips.append(f"Age group: {age_group}")

    if bmi_category:
        chips.append(f"BMI: {bmi_category}")

    if smoking:
        chips.append(f"Smoking: {smoking}")

    if physical:
        chips.append(f"Physical activity: {physical}")

    if salt:
        chips.append(f"Salt intake: {salt}")

    if stress:
        chips.append(f"Stress: {stress}")

    if diabetes:
        chips.append(f"Diabetes: {diabetes}")

    if family_hx:
        chips.append(f"Family history: {family_hx}")

    if not chips:
        content = html.Div("No active filters selected.", className="active-filters-empty")
    else:
        content = html.Div(
            [html.Span(chip, className="filter-chip") for chip in chips],
            className="active-filters-chips",
        )

    return html.Div(
        [
            html.H3("Active filters", className="panel-title"),
            content,
        ],
        className="active-filters-wrap",
    )
from typing import Optional, List, Any

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


def help_icon(text: Any):
    """
    Builds the small question-mark icon and hover tooltip.

    Parameters:
    - text: Dash HTML content shown inside the tooltip.

    Returns:
    - A Dash html.Span containing the icon and tooltip box.
    """
    return html.Span(
        [
            html.Span("?", className="help-icon-mark"),
            html.Div(text, className="help-tooltip-box"),
        ],
        className="help-tooltip-wrap",
    )


def stat_card(label: str, value: str, tooltip: Optional[Any] = None):
    """
    Builds one statistic card for the dashboard information panels.

    Parameters:
    - label: Small text label, such as "Avg systolic".
    - value: Main displayed value, such as "125.8 mmHg".
    - tooltip: Optional help text shown when hovering over the question mark.

    Returns:
    - A Dash html.Div styled as a statistic card.
    """
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


def format_mean(
    df: pd.DataFrame,
    column: str,
    suffix: str = "",
    decimals: int = 1,
) -> str:
    """
    Safely formats the mean value of a numeric dataframe column.

    If the column is missing or contains no valid values, the function
    returns "N/A" instead of causing an error.

    Parameters:
    - df: Filtered dataframe.
    - column: Column name to average.
    - suffix: Optional unit suffix, such as " mmHg" or "%".
    - decimals: Number of decimal places.

    Returns:
    - A formatted string.
    """
    if column not in df.columns:
        return "N/A"

    numeric_values = pd.to_numeric(df[column], errors="coerce")

    if not numeric_values.notna().any():
        return "N/A"

    return f"{numeric_values.mean():.{decimals}f}{suffix}"


def info_cards_for_df(dff: pd.DataFrame, country: Optional[str] = None) -> List:
    """
    Builds the overview statistic cards for either the full dataset
    or one selected country.

    Parameters:
    - dff: Filtered dataframe.
    - country: Optional selected country name.

    Returns:
    - A list of Dash components used inside the stats grid.
    """
    if dff.empty:
        return [
            html.Div(
                "No data for the selected filters.",
                className="info-empty",
            )
        ]

    title = country if country else "Dataset overview"

    years = "N/A"
    if "Year" in dff.columns:
        year_values = pd.to_numeric(dff["Year"], errors="coerce")
        if year_values.notna().any():
            years = f"{int(year_values.min())}–{int(year_values.max())}"

    countries = (
        f"{dff['Country'].nunique():,}"
        if "Country" in dff.columns
        else "N/A"
    )

    return [
        stat_card("Scope", title),
        stat_card("Patients", f"{len(dff):,}"),
        stat_card("Countries", countries),
        stat_card("Years", years),
        stat_card(
            "Avg systolic",
            format_mean(dff, "Systolic_BP_mmHg", " mmHg"),
            INFO_HELP["Avg systolic"],
        ),
        stat_card(
            "Avg diastolic",
            format_mean(dff, "Diastolic_BP_mmHg", " mmHg"),
            INFO_HELP["Avg diastolic"],
        ),
        stat_card(
            "Avg MAP",
            format_mean(dff, "Mean_Arterial_Pressure", " mmHg"),
            INFO_HELP["Avg MAP"],
        ),
        stat_card(
            "Avg pulse pressure",
            format_mean(dff, "Pulse_Pressure_mmHg", " mmHg"),
            INFO_HELP["Avg pulse pressure"],
        ),
        stat_card(
            "Avg heart rate",
            format_mean(dff, "Heart_Rate_bpm", " bpm"),
            INFO_HELP["Avg heart rate"],
        ),
        stat_card(
            "HTN prevalence",
            format_mean(dff, "Country_HTN_Prevalence_pct", "%"),
            INFO_HELP["HTN prevalence"],
        ),
        stat_card(
            "BMI",
            format_mean(dff, "BMI"),
            INFO_HELP["BMI"],
        ),
    ]


def overview_note():
    """
    Builds the explanatory "Why this matters" card for the overview page.

    Returns:
    - A Dash html.Div containing the project explanation.
    """
    return html.Div(
        [
            html.H3("Why this matters", className="panel-title"),
            html.Div(
                [
                    html.P(
                        [
                            "High blood pressure is a major risk factor for serious health problems, including ",
                            html.B("stroke"),
                            ", ",
                            html.B("heart disease"),
                            ", and ",
                            html.B("kidney damage"),
                            ".",
                        ]
                    ),
                    html.P("This dashboard helps users explore:"),
                    html.Ul(
                        [
                            html.Li(html.B("Hypertension prevalence")),
                            html.Li(html.B("Systolic and diastolic blood pressure")),
                            html.Li(html.B("Pulse pressure and heart rate")),
                            html.Li(html.B("BMI and age patterns")),
                        ]
                    ),
                    html.P(
                        [
                            "It also compares results across key groups, such as ",
                            html.B("sex"),
                            ", ",
                            html.B("age group"),
                            ", ",
                            html.B("smoking status"),
                            ", ",
                            html.B("physical activity"),
                            ", ",
                            html.B("salt intake"),
                            ", ",
                            html.B("stress level"),
                            ", ",
                            html.B("diabetes"),
                            ", and ",
                            html.B("family history"),
                            ".",
                        ]
                    ),
                    html.P(
                        [
                            "These insights can help identify ",
                            html.B("higher-risk populations"),
                            " and support ",
                            html.B("prevention"),
                            ", ",
                            html.B("screening"),
                            ", ",
                            html.B("lifestyle interventions"),
                            ", and better public health decisions.",
                        ]
                    ),
                ],
                className="overview-note-text",
            ),
        ],
        className="overview-note-wrap",
    )


def add_filter_chip(
    chips: list[tuple[str, str]],
    filter_key: str,
    label: str,
    value: Optional[str],
) -> None:
    """
    Adds one active filter chip if a filter value exists.

    Parameters:
    - chips: List that stores active filter chips.
    - filter_key: Internal key used by callbacks to clear the filter.
    - label: Human-readable filter name.
    - value: Current filter value.
    """
    if value:
        chips.append((filter_key, f"{label}: {value}"))


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
    """
    Builds the active filters panel.

    The panel always shows the selected map metric. Other filter chips
    appear only when the user has selected them. Each chip is clickable
    and can be removed through the matching callback.

    Parameters:
    - metric: Selected map metric.
    - year_range: Selected year slider range.
    - sex: Selected sex filter.
    - age_group: Selected age group filter.
    - bmi_category: Selected BMI category filter.
    - smoking: Selected smoking status filter.
    - physical: Selected physical activity filter.
    - salt: Selected salt intake filter.
    - stress: Selected stress level filter.
    - diabetes: Selected diabetes filter.
    - family_hx: Selected family history filter.
    - year_min: Minimum available year.
    - year_max: Maximum available year.
    - selected_country: Optional selected country.

    Returns:
    - A Dash html.Div containing active filter chips.
    """
    chips = []

    metric_label = MAP_METRICS.get(metric, metric)
    chips.append(("metric", f"Metric: {metric_label}"))

    if selected_country:
        chips.append(("country", f"Country: {selected_country}"))

    if year_range and len(year_range) == 2:
        if year_range[0] != year_min or year_range[1] != year_max:
            chips.append(("year", f"Years: {year_range[0]}–{year_range[1]}"))

    add_filter_chip(chips, "sex", "Sex", sex)
    add_filter_chip(chips, "age_group", "Age group", age_group)
    add_filter_chip(chips, "bmi_category", "BMI", bmi_category)
    add_filter_chip(chips, "smoking", "Smoking", smoking)
    add_filter_chip(chips, "physical", "Physical activity", physical)
    add_filter_chip(chips, "salt", "Salt intake", salt)
    add_filter_chip(chips, "stress", "Stress", stress)
    add_filter_chip(chips, "diabetes", "Diabetes", diabetes)
    add_filter_chip(chips, "family_hx", "Family history", family_hx)

    content = html.Div(
        [
            html.Button(
                [
                    html.Span(label),
                    html.Span(" ×", className="filter-chip-x"),
                ],
                id={"type": "remove-filter-chip", "filter": filter_key},
                n_clicks=0,
                className="filter-chip",
            )
            for filter_key, label in chips
        ],
        className="active-filters-chips",
    )

    return html.Div(
        [
            html.Div(
                [
                    html.H3("Active filters", className="panel-title"),
                ],
                className="active-filters-header",
            ),
            content,
        ],
        className="active-filters-wrap",
    )
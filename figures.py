from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import MAP_METRICS, TEAL_SCALE


# =============================
# Shared constants
# =============================

SYSTOLIC_REFERENCE_RANGE = (90, 120)
DIASTOLIC_REFERENCE_RANGE = (60, 80)

DEFAULT_BP_CATEGORY_ORDER = [
    "Normal",
    "Elevated",
    "Stage 1 Hypertension",
    "Stage 2 Hypertension",
    "Severe Hypertension",
]

DEFAULT_AGE_GROUP_ORDER = [
    "Infant (0-1)",
    "Early Childhood (1-5)",
    "Middle Childhood (6-10)",
    "Early Adolescence (11-15)",
    "Late Adolescence (16-18)",
    "Young Adult (19-29)",
    "Adult (30-39)",
    "Middle-Aged (40-49)",
    "Middle-Aged Senior (50-59)",
    "Young Elderly (60-69)",
    "Elderly (70-79)",
    "Very Elderly (80+)",
]

DEFAULT_DIABETES_ORDER = [
    "No Diabetes",
    "Has Diabetes",
]


# =============================
# Shared helpers
# =============================

def empty_figure(message: str):
    """
    Creates an empty Plotly figure with a centered message.

    Used when the selected filters produce no usable data for a chart.
    """
    fig = go.Figure()

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        annotations=[
            {
                "text": message,
                "showarrow": False,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 16},
            }
        ],
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


def _available_columns(df: pd.DataFrame, columns: list[str]) -> bool:
    """
    Checks whether all required columns exist in a dataframe.

    This prevents chart functions from failing if the dataset is missing
    one or more expected columns.
    """
    return all(column in df.columns for column in columns)


def _existing_ordered_values(series: pd.Series, preferred_order: list[str]) -> list[str]:
    """
    Returns values from a preferred order that actually exist in the data.

    This keeps chart categories visually consistent while avoiding empty
    categories that are not present for the selected country or filters.
    """
    existing_values = series.dropna().astype(str).unique().tolist()

    return [
        value
        for value in preferred_order
        if value in existing_values
    ]


# =============================
# Map
# =============================

def make_map(
    map_df: pd.DataFrame,
    metric: str,
    selected_country: Optional[str] = None,
    compact: bool = False,
):
    """
    Creates the global or focused country choropleth map.

    If no country is selected, the map shows all available countries.
    If a country is selected, the map zooms to that country.
    """
    if map_df.empty:
        fig = go.Figure()

        fig.update_layout(
            template="plotly_white",
            autosize=True,
            height=None,
            annotations=[
                {
                    "text": "No data available for the selected filters",
                    "showarrow": False,
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "font": {"size": 18},
                }
            ],
            margin=dict(l=0, r=0, t=10, b=0),
        )

        return fig

    fig = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color=metric,
        hover_name="Country",
        custom_data=["Patients", "WHO_Region", "Income_Level"],
        color_continuous_scale=TEAL_SCALE,
        projection="natural earth",
    )

    if selected_country:
        fig.add_trace(
            go.Scattergeo(
                locations=map_df["Country"],
                locationmode="country names",
                text=map_df["Country"],
                mode="text",
                hoverinfo="none",
                hovertemplate=None,
                textfont=dict(size=14, color="black"),
                showlegend=False,
            )
        )

    fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>"
            + f"{MAP_METRICS.get(metric, metric)}: "
            + "%{z:.2f}<br>"
            + "Patients: %{customdata[0]:,.0f}<br>"
            + "Income level: %{customdata[2]}<extra></extra>"
        ),
        marker_line_color="white",
        marker_line_width=0.5,
    )

    if selected_country:
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="rgba(0,0,0,0)",
            domain=dict(x=[0, 1], y=[0, 1]),
        )
    else:
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            showcountries=True,
            countrycolor="white",
            bgcolor="rgba(0,0,0,0)",
            domain=dict(x=[0, 1], y=[0.02, 0.96]),
            projection_scale=1.28,
            lataxis_range=[-58, 85],
            lonaxis_range=[-180, 180],
        )

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(
            title=MAP_METRICS.get(metric, metric),
            len=0.50 if not compact else 0.55,
            y=0.50,
        ),
        clickmode="event+select",
    )

    return fig


# =============================
# Historical blood pressure plot
# =============================

def make_historical_bp_figure(country_df: pd.DataFrame, mode: str = "year"):
    """
    Creates the main blood pressure history chart.

    Mode options:
    - "year": shows average systolic and diastolic BP by year
    - "record": shows systolic and diastolic BP by individual database record

    The chart also includes colored reference bands for systolic and
    diastolic blood pressure ranges.
    """
    required_cols = ["Systolic_BP_mmHg", "Diastolic_BP_mmHg"]

    if country_df.empty or not _available_columns(country_df, required_cols):
        return empty_figure("No blood pressure data available.")

    dff = country_df.copy()

    dff["Systolic_BP_mmHg"] = pd.to_numeric(
        dff["Systolic_BP_mmHg"],
        errors="coerce",
    )
    dff["Diastolic_BP_mmHg"] = pd.to_numeric(
        dff["Diastolic_BP_mmHg"],
        errors="coerce",
    )

    dff = dff.dropna(subset=["Systolic_BP_mmHg", "Diastolic_BP_mmHg"])

    if dff.empty:
        return empty_figure("No blood pressure data available.")

    mode = mode or "year"

    if mode == "record":
        plot_df = _prepare_record_bp_data(dff)
        x_col = "Record_No"
        x_title = "Record in database"
        title = "Blood pressure by database record"
    else:
        plot_df = _prepare_yearly_bp_data(dff)

        if plot_df.empty:
            return empty_figure("No year data available for historical trend.")

        x_col = "Year"
        x_title = "Year"
        title = "Historical trend: systolic and diastolic blood pressure"

    n_points = len(plot_df)
    trace_mode = "lines+markers" if n_points <= 80 else "lines"

    fig = go.Figure()

    _add_bp_reference_bands(fig)
    _add_bp_line_traces(fig, plot_df, x_col, x_title, trace_mode)
    _add_bp_reference_labels(fig)

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        title=title,
        margin=dict(l=10, r=10, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
            font=dict(size=12),
        ),
        hovermode="x unified" if mode == "year" else "closest",
        xaxis_title=x_title,
        yaxis_title="Blood pressure (mmHg)",
    )

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)

    if mode == "year":
        fig.update_xaxes(dtick=5)

    return fig


def _prepare_record_bp_data(dff: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares blood pressure data for record-level plotting.

    Each row becomes one record on the x-axis. Data is sorted by year and
    patient ID when those columns are available.
    """
    sort_cols = []

    if "Year" in dff.columns:
        sort_cols.append("Year")

    if "Patient_ID" in dff.columns:
        sort_cols.append("Patient_ID")

    if sort_cols:
        dff = dff.sort_values(sort_cols)

    plot_df = dff.reset_index(drop=True)
    plot_df["Record_No"] = plot_df.index + 1

    return plot_df


def _prepare_yearly_bp_data(dff: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares blood pressure data for yearly trend plotting.

    The function calculates the average systolic and diastolic blood
    pressure for each year.
    """
    if "Year" not in dff.columns:
        return pd.DataFrame()

    plot_df = (
        dff.groupby("Year", as_index=False)[
            ["Systolic_BP_mmHg", "Diastolic_BP_mmHg"]
        ]
        .mean()
        .sort_values("Year")
    )

    return plot_df


def _add_bp_reference_bands(fig: go.Figure) -> None:
    """
    Adds colored reference bands for systolic and diastolic blood pressure.

    These shaded regions make it easier to visually compare chart values
    against common reference ranges.
    """
    systolic_low, systolic_high = SYSTOLIC_REFERENCE_RANGE
    diastolic_low, diastolic_high = DIASTOLIC_REFERENCE_RANGE

    fig.add_hrect(
        y0=systolic_low,
        y1=systolic_high,
        fillcolor="#0b8f83",
        opacity=0.12,
        line_width=0,
        layer="below",
    )

    fig.add_hrect(
        y0=diastolic_low,
        y1=diastolic_high,
        fillcolor="#b36b12",
        opacity=0.14,
        line_width=0,
        layer="below",
    )


def _add_bp_line_traces(
    fig: go.Figure,
    plot_df: pd.DataFrame,
    x_col: str,
    x_title: str,
    trace_mode: str,
) -> None:
    """
    Adds systolic and diastolic blood pressure line traces to a figure.
    """
    fig.add_trace(
        go.Scatter(
            x=plot_df[x_col],
            y=plot_df["Systolic_BP_mmHg"],
            mode=trace_mode,
            name="Systolic BP",
            line=dict(color="#0b8f83", width=3),
            marker=dict(size=6),
            hovertemplate=(
                f"{x_title}: " + "%{x}<br>"
                "Systolic BP: %{y:.1f} mmHg"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plot_df[x_col],
            y=plot_df["Diastolic_BP_mmHg"],
            mode=trace_mode,
            name="Diastolic BP",
            line=dict(color="#a86616", width=3),
            marker=dict(size=6),
            hovertemplate=(
                f"{x_title}: " + "%{x}<br>"
                "Diastolic BP: %{y:.1f} mmHg"
                "<extra></extra>"
            ),
        )
    )


def _add_bp_reference_labels(fig: go.Figure) -> None:
    """
    Adds text labels for the systolic and diastolic reference bands.
    """
    systolic_low, systolic_high = SYSTOLIC_REFERENCE_RANGE
    diastolic_low, diastolic_high = DIASTOLIC_REFERENCE_RANGE

    fig.add_annotation(
        x=0.99,
        y=(systolic_low + systolic_high) / 2,
        xref="paper",
        yref="y",
        text="Systolic reference range",
        showarrow=False,
        xanchor="right",
        font=dict(size=11, color="#0b5f60"),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor="rgba(11,95,96,0.25)",
        borderwidth=1,
    )

    fig.add_annotation(
        x=0.99,
        y=(diastolic_low + diastolic_high) / 2,
        xref="paper",
        yref="y",
        text="Diastolic reference range",
        showarrow=False,
        xanchor="right",
        font=dict(size=11, color="#8a520f"),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor="rgba(179,107,18,0.25)",
        borderwidth=1,
    )


def make_country_figures(country_df: pd.DataFrame, bp_mode: str = "year"):
    """
    Creates all charts used on the country-specific dashboard screen.

    Returns:
    - historical blood pressure chart
    - BP category by age group chart
    - BP category by diabetes status chart
    """
    if country_df.empty:
        msg = empty_figure("No country data to display.")
        return msg, msg, msg

    fig_trend = make_historical_bp_figure(country_df, mode=bp_mode)
    fig_bp_cat = make_bp_category_figure(country_df)
    fig_diabetes = make_diabetes_bp_category_figure(country_df)

    return fig_trend, fig_bp_cat, fig_diabetes


# =============================
# Diabetes stacked bar plot
# =============================

def make_diabetes_bp_category_figure(country_df: pd.DataFrame):
    """
    Creates a 100% stacked bar chart showing BP category distribution
    by diabetes status.

    The y-axis shows the percentage of people within each diabetes group.
    Hover information is disabled because the chart already displays
    percentage labels directly.
    """
    required_cols = {"Diabetes", "BP_Category_2"}

    if country_df.empty or not required_cols.issubset(country_df.columns):
        return empty_figure("No diabetes and BP category data available.")

    dff = country_df[["Diabetes", "BP_Category_2"]].copy()
    dff = dff.dropna()

    if dff.empty:
        return empty_figure("No diabetes and BP category data available.")

    dff["Diabetes_Status"] = dff["Diabetes"].apply(_clean_diabetes_label)

    existing_bp = _existing_ordered_values(
        dff["BP_Category_2"],
        DEFAULT_BP_CATEGORY_ORDER,
    )

    existing_diabetes = _existing_ordered_values(
        dff["Diabetes_Status"],
        DEFAULT_DIABETES_ORDER,
    )

    extra_diabetes = [
        status
        for status in dff["Diabetes_Status"].astype(str).unique().tolist()
        if status not in existing_diabetes
    ]

    existing_diabetes = existing_diabetes + sorted(extra_diabetes)

    if not existing_bp or not existing_diabetes:
        return empty_figure("No diabetes and BP category data available.")

    counts = (
        dff.groupby(["Diabetes_Status", "BP_Category_2"])
        .size()
        .reset_index(name="Count")
    )

    totals = (
        counts.groupby("Diabetes_Status")["Count"]
        .sum()
        .reset_index(name="Total")
    )

    plot_df = counts.merge(totals, on="Diabetes_Status", how="left")
    plot_df["Percentage"] = (plot_df["Count"] / plot_df["Total"] * 100).round(1)

    fig = px.bar(
        plot_df,
        x="Diabetes_Status",
        y="Percentage",
        color="BP_Category_2",
        category_orders={
            "Diabetes_Status": existing_diabetes,
            "BP_Category_2": existing_bp,
        },
        title="Blood pressure category by diabetes status",
        labels={
            "Diabetes_Status": "Diabetes status",
            "Percentage": "Percentage of people",
            "BP_Category_2": "BP category",
        },
        text="Percentage",
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        insidetextanchor="middle",
        hoverinfo="skip",
        hovertemplate=None,
        cliponaxis=False,
    )

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        barmode="stack",
        margin=dict(l=10, r=120, t=50, b=55),
        legend_title_text="BP category",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.85)",
        ),
        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
        ),
    )

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)

    return fig


def _clean_diabetes_label(value: object) -> str:
    """
    Standardizes diabetes labels into clearer display names.

    For example:
    - yes, true, 1 -> Has Diabetes
    - no, false, 0 -> No Diabetes
    """
    value = str(value).strip()
    lower_value = value.lower()

    yes_values = {"yes", "has diabetes", "diabetes", "true", "1"}
    no_values = {"no", "no diabetes", "non-diabetic", "false", "0"}

    if lower_value in yes_values:
        return "Has Diabetes"

    if lower_value in no_values:
        return "No Diabetes"

    return value


# =============================
# BP category by age group plot
# =============================

def make_bp_category_figure(country_df: pd.DataFrame):
    """
    Creates a grouped bar chart showing BP category counts by age group.

    The gray background bars show total people per BP category.
    Colored bars show how those totals are distributed by age group.
    """
    required_cols = {"BP_Category_2", "Age_Group"}

    if country_df.empty or not required_cols.issubset(country_df.columns):
        return empty_figure("No BP category data available.")

    existing_bp = _existing_ordered_values(
        country_df["BP_Category_2"],
        DEFAULT_BP_CATEGORY_ORDER,
    )

    if not existing_bp:
        return empty_figure("No BP category data available.")

    total_counts = (
        country_df.groupby("BP_Category_2")
        .size()
        .reindex(existing_bp, fill_value=0)
        .reset_index(name="Count")
    )

    age_counts = (
        country_df.groupby(["BP_Category_2", "Age_Group"])
        .size()
        .reset_index(name="Count")
    )

    fig = go.Figure()

    spacing = 1.4
    x_positions = [i * spacing for i in range(len(existing_bp))]

    fig.add_trace(
        go.Bar(
            x=x_positions,
            y=total_counts["Count"],
            name="Total",
            marker_color="lightgray",
            opacity=0.65,
            width=1.4,
            hoverinfo="none",
            showlegend=False,
        )
    )

    age_groups = _existing_ordered_values(
        country_df["Age_Group"],
        DEFAULT_AGE_GROUP_ORDER,
    )

    n_groups = max(len(age_groups), 1)
    bar_width = min(1.5 / n_groups, 0.15)

    for index, age_group in enumerate(age_groups):
        age_series = (
            age_counts.loc[age_counts["Age_Group"] == age_group]
            .set_index("BP_Category_2")["Count"]
            .reindex(existing_bp, fill_value=0)
        )

        offset = (index - (n_groups - 1) / 2) * bar_width
        x_age = [x + offset for x in x_positions]

        fig.add_trace(
            go.Bar(
                x=x_age,
                y=age_series.values,
                name=age_group,
                width=bar_width,
                customdata=[[age_group]] * len(age_series.values),
                hovertemplate=(
                    "Age group: %{customdata[0]}<br>"
                    "Count: %{y}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        barmode="overlay",
        title="People count by BP category and age group",
        xaxis_title="Blood pressure category",
        yaxis_title="People count",
        margin=dict(l=10, r=160, t=50, b=80),
        legend_title_text="Age group",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.85)",
        ),
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=x_positions,
        ticktext=existing_bp,
        tickangle=20,
        range=[x_positions[0] - 0.8, x_positions[-1] + 0.8],
        automargin=True,
    )

    fig.update_yaxes(automargin=True)

    return fig
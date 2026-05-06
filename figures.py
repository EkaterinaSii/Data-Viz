from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import MAP_METRICS, TEAL_SCALE


def empty_figure(message: str, height: int = 320):
    fig = go.Figure()

    fig.update_layout(
        template="plotly_white",
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
        height=height,
    )

    return fig


def make_map(
    map_df: pd.DataFrame,
    metric: str,
    selected_country: Optional[str] = None,
    compact: bool = False,
):
    if map_df.empty:
        fig = go.Figure()

        fig.update_layout(
            template="plotly_white",
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
            margin=dict(l=0, r=0, t=50, b=0),
            height=280 if compact else 680,
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
            domain=dict(x=[0, 1], y=[0.10, 0.90]),
            projection_scale=1.18,
            lataxis_range=[-58, 85],
            lonaxis_range=[-180, 180],
        )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=45, b=0),
        height=440 if compact else 720,
        coloraxis_colorbar=dict(
            title=MAP_METRICS.get(metric, metric),
            len=0.62,
            y=0.5,
        ),
        title=dict(
            text=(
                f"Global map: {MAP_METRICS.get(metric, metric)}"
                if not selected_country
                else f"Focused map: {selected_country}"
            ),
            x=0.02,
            xanchor="left",
        ),
        clickmode="event+select",
    )

    return fig


def make_country_figures(country_df: pd.DataFrame):
    if country_df.empty:
        msg = empty_figure("No country data to display.")
        return msg, msg, msg, msg

    trend = (
        country_df.groupby("Year", as_index=False)[
            ["Systolic_BP_mmHg", "Diastolic_BP_mmHg", "Mean_Arterial_Pressure"]
        ]
        .mean()
        .sort_values("Year")
    )

    fig_trend = px.line(
        trend,
        x="Year",
        y=["Systolic_BP_mmHg", "Diastolic_BP_mmHg", "Mean_Arterial_Pressure"],
        markers=True,
        title="Trend over years",
    )

    fig_trend.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="Metric",
        height=340,
    )

    age_bp = (
        country_df.groupby("Age_Group", as_index=False)[
            ["Systolic_BP_mmHg", "Diastolic_BP_mmHg"]
        ]
        .mean()
        .sort_values("Age_Group")
    )

    fig_age = px.bar(
        age_bp,
        x="Age_Group",
        y=["Systolic_BP_mmHg", "Diastolic_BP_mmHg"],
        barmode="group",
        title="BP by age group",
    )

    fig_age.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="Metric",
        height=420,
    )

    fig_sex = px.box(
        country_df,
        x="Sex",
        y="Systolic_BP_mmHg",
        color="Sex",
        points="outliers",
        title="Systolic BP by sex",
    )

    fig_sex.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        height=420,
    )

    fig_bp_cat = make_bp_category_figure(country_df)

    return fig_trend, fig_age, fig_sex, fig_bp_cat


def make_bp_category_figure(country_df: pd.DataFrame):
    bp_order = [
        "Normal",
        "Elevated",
        "Stage 1 Hypertension",
        "Stage 2 Hypertension",
        "Severe Hypertension",
    ]

    existing_bp = [
        bp
        for bp in bp_order
        if bp in country_df["BP_Category_2"].dropna().astype(str).unique().tolist()
    ]

    if not existing_bp:
        return empty_figure("No BP category data available.", height=420)

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
        )
    )

    age_order = [
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

    age_groups = [
        age
        for age in age_order
        if age in country_df["Age_Group"].dropna().astype(str).unique().tolist()
    ]

    n_groups = max(len(age_groups), 1)
    bar_width = min(1.5 / n_groups, 0.15)

    for i, age_group in enumerate(age_groups):
        age_series = (
            age_counts.loc[age_counts["Age_Group"] == age_group]
            .set_index("BP_Category_2")["Count"]
            .reindex(existing_bp, fill_value=0)
        )

        offset = (i - (n_groups - 1) / 2) * bar_width
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
        barmode="overlay",
        title="People count by BP category and age group",
        xaxis_title="Blood pressure category",
        yaxis_title="People count",
        margin=dict(l=10, r=10, t=50, b=60),
        height=420,
        legend_title_text="Age group",
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=x_positions,
        ticktext=existing_bp,
        range=[x_positions[0] - 0.8, x_positions[-1] + 0.8],
    )

    return fig
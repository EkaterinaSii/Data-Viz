from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import MAP_METRICS, TEAL_SCALE


def empty_figure(message: str):
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
            margin=dict(l=0, r=0, t=50, b=0),
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
                len=0.50,
                y=0.50,
            ),
            clickmode="event+select",
        )

    return fig


def make_country_figures(country_df: pd.DataFrame):
    if country_df.empty:
        msg = empty_figure("No country data to display.")
        return msg, msg, msg

    # -----------------------------
    # Plot 1: Historical SBP / DBP trend
    # -----------------------------
    trend = (
        country_df.groupby("Year", as_index=False)[
            ["Systolic_BP_mmHg", "Diastolic_BP_mmHg"]
        ]
        .mean()
        .sort_values("Year")
    )

    fig_trend = px.line(
        trend,
        x="Year",
        y=["Systolic_BP_mmHg", "Diastolic_BP_mmHg"],
        markers=True,
        title="Historical trend: systolic and diastolic blood pressure",
    )

    fig_trend.update_layout(
        template="plotly_white",
        autosize=True,
        height=None,
        margin=dict(l=10, r=10, t=50, b=40),
        legend_title_text="Metric",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        ),
    )

    fig_trend.update_xaxes(automargin=True)
    fig_trend.update_yaxes(title="mmHg", automargin=True)

    # -----------------------------
    # Plot 2: BP category by age group
    # -----------------------------
    fig_bp_cat = make_bp_category_figure(country_df)

    # -----------------------------
    # Plot 3: BP category by diabetes status
    # -----------------------------
    fig_diabetes = make_diabetes_bp_category_figure(country_df)

    return fig_trend, fig_bp_cat, fig_diabetes

def make_diabetes_bp_category_figure(country_df: pd.DataFrame):
    required_cols = {"Diabetes", "BP_Category_2"}

    if country_df.empty or not required_cols.issubset(country_df.columns):
        return empty_figure("No diabetes and BP category data available.")

    dff = country_df[["Diabetes", "BP_Category_2"]].copy()
    dff = dff.dropna()

    if dff.empty:
        return empty_figure("No diabetes and BP category data available.")

    def clean_diabetes_label(value):
        value = str(value).strip()
        lower_value = value.lower()

        yes_values = {"yes", "has diabetes", "diabetes", "true", "1"}
        no_values = {"no", "no diabetes", "non-diabetic", "false", "0"}

        if lower_value in yes_values:
            return "Has Diabetes"
        if lower_value in no_values:
            return "No Diabetes"

        return value

    dff["Diabetes_Status"] = dff["Diabetes"].apply(clean_diabetes_label)

    bp_order = [
        "Normal",
        "Elevated",
        "Stage 1 Hypertension",
        "Stage 2 Hypertension",
        "Severe Hypertension",
    ]

    diabetes_order = ["No Diabetes", "Has Diabetes"]

    existing_bp = [
        bp for bp in bp_order
        if bp in dff["BP_Category_2"].astype(str).unique().tolist()
    ]

    existing_diabetes = [
        status for status in diabetes_order
        if status in dff["Diabetes_Status"].astype(str).unique().tolist()
    ]

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
            font=dict(size=9),
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
            font=dict(size=8),
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
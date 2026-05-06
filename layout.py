from dash import dcc, html

from config import MAP_METRICS
from data import dropdown_options


def build_layout(df, year_min: int, year_max: int):
    return html.Div(
        [
            dcc.Store(id="selected-country"),
            dcc.Store(id="selected-sex"),
            dcc.Store(id="selected-smoking"),

            html.Div(
                [
                    html.H1("Blood Pressure Dashboard", className="page-title"),
                    html.P(
                        "Data visualization dashboard for exploring blood pressure metrics across countries and demographics.\n"
                        "Click on the map to focus on a specific country, or use the filters to explore different subsets of the data.\n"
                        "Made by Ekaterina Siikavirta",
                        className="page-subtitle",
                    ),
                ],
                className="header",
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Filters", className="panel-title"),

                            html.Label("Map metric"),
                            dcc.Dropdown(
                                id="metric-dropdown",
                                options=[
                                    {"label": v, "value": k}
                                    for k, v in MAP_METRICS.items()
                                ],
                                value="Country_HTN_Prevalence_pct",
                                clearable=False,
                            ),

                            html.Label("Year range"),
                            dcc.RangeSlider(
                                id="year-range",
                                min=year_min,
                                max=year_max,
                                step=1,
                                value=[year_min, year_max],
                                marks={year_min: str(year_min), year_max: str(year_max)},
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),

                            html.Label("Sex"),
                            html.Div(
                                [
                                    html.Button(
                                        html.Img(
                                            src="/assets/male-icon.png",
                                            className="sex-icon",
                                        ),
                                        id="sex-male-btn",
                                        n_clicks=0,
                                        className="sex-btn",
                                    ),
                                    html.Button(
                                        html.Img(
                                            src="/assets/female-icon.png",
                                            className="sex-icon",
                                        ),
                                        id="sex-female-btn",
                                        n_clicks=0,
                                        className="sex-btn",
                                    ),
                                ],
                                className="sex-toggle-row",
                            ),

                            html.Label("Age group"),
                            dcc.Dropdown(
                                id="age-group-dropdown",
                                options=dropdown_options(df["Age_Group"]),
                                placeholder="All",
                            ),

                            html.Label("BMI category"),
                            dcc.Dropdown(
                                id="bmi-category-dropdown",
                                options=dropdown_options(df["BMI_Category"]),
                                placeholder="All",
                            ),

                            html.Label("Smoking status"),
                            html.Div(
                                [
                                    html.Button(
                                        [
                                            html.Img(
                                                src="/assets/no-smoking-icon.png",
                                                className="smoking-icon",
                                            ),
                                            html.Span(
                                                "Non-Smoker",
                                                className="smoking-btn-label",
                                            ),
                                        ],
                                        id="smoking-non-btn",
                                        n_clicks=0,
                                        className="smoking-btn",
                                    ),
                                    html.Button(
                                        [
                                            html.Img(
                                                src="/assets/smoking-status.png",
                                                className="smoking-icon",
                                            ),
                                            html.Span(
                                                "Current Smoker",
                                                className="smoking-btn-label",
                                            ),
                                        ],
                                        id="smoking-current-btn",
                                        n_clicks=0,
                                        className="smoking-btn",
                                    ),
                                    html.Button(
                                        [
                                            html.Img(
                                                src="/assets/ex-smoker.png",
                                                className="smoking-icon",
                                            ),
                                            html.Span(
                                                "Ex-Smoker",
                                                className="smoking-btn-label",
                                            ),
                                        ],
                                        id="smoking-ex-btn",
                                        n_clicks=0,
                                        className="smoking-btn",
                                    ),
                                ],
                                className="smoking-toggle-row",
                            ),

                            html.Label("Physical activity"),
                            dcc.Dropdown(
                                id="physical-dropdown",
                                options=dropdown_options(df["Physical_Activity"]),
                                placeholder="All",
                            ),

                            html.Label("Diet salt intake"),
                            dcc.Dropdown(
                                id="salt-dropdown",
                                options=dropdown_options(df["Diet_Salt_Intake"]),
                                placeholder="All",
                            ),

                            html.Label("Stress level"),
                            dcc.Dropdown(
                                id="stress-dropdown",
                                options=dropdown_options(df["Stress_Level"]),
                                placeholder="All",
                            ),

                            html.Label("Diabetes"),
                            dcc.Dropdown(
                                id="diabetes-dropdown",
                                options=dropdown_options(df["Diabetes"]),
                                placeholder="All",
                            ),

                            html.Label("Family history of hypertension"),
                            dcc.Dropdown(
                                id="family-dropdown",
                                options=dropdown_options(df["Family_Hx_Hypertension"]),
                                placeholder="All",
                            ),

                            html.Button(
                                "Reset country selection",
                                id="reset-country-btn",
                                n_clicks=0,
                                className="reset-btn",
                            ),
                        ],
                        className="filters-panel",
                    ),

                    html.Div(
                        [html.Div(id="main-content")],
                        className="content-panel",
                    ),
                ],
                className="dashboard-shell",
            ),
        ],
        className="page",
    )
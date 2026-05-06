from dash import Input, Output, State, ctx, dcc, html, dash_table, ALL, no_update

from config import MAP_METRICS
from components import (
    build_active_filters_box,
    info_cards_for_df,
    overview_note,
)
from data import apply_filters, aggregate_for_map
from figures import make_country_figures, make_map


def register_callbacks(app, df, year_min: int, year_max: int):

    @app.callback(
        Output("selected-smoking", "data"),
        Input("smoking-non-btn", "n_clicks"),
        Input("smoking-current-btn", "n_clicks"),
        Input("smoking-ex-btn", "n_clicks"),
        State("selected-smoking", "data"),
        prevent_initial_call=True,
    )
    def update_selected_smoking(
        non_clicks,
        current_clicks,
        ex_clicks,
        current_smoking,
    ):
        trigger = ctx.triggered_id

        if trigger == "smoking-non-btn":
            return None if current_smoking == "Non-Smoker" else "Non-Smoker"

        if trigger == "smoking-current-btn":
            return None if current_smoking == "Current Smoker" else "Current Smoker"

        if trigger == "smoking-ex-btn":
            return None if current_smoking == "Ex-Smoker" else "Ex-Smoker"

        return current_smoking

    @app.callback(
        Output("smoking-non-btn", "className"),
        Output("smoking-current-btn", "className"),
        Output("smoking-ex-btn", "className"),
        Input("selected-smoking", "data"),
    )
    def style_smoking_buttons(selected_smoking):
        non_class = (
            "smoking-btn active"
            if selected_smoking == "Non-Smoker"
            else "smoking-btn"
        )
        current_class = (
            "smoking-btn active"
            if selected_smoking == "Current Smoker"
            else "smoking-btn"
        )
        ex_class = (
            "smoking-btn active"
            if selected_smoking == "Ex-Smoker"
            else "smoking-btn"
        )

        return non_class, current_class, ex_class

    @app.callback(
        Output("sex-male-btn", "className"),
        Output("sex-female-btn", "className"),
        Input("selected-sex", "data"),
    )
    def style_sex_buttons(selected_sex):
        male_class = "sex-btn active" if selected_sex == "Male" else "sex-btn"
        female_class = "sex-btn active" if selected_sex == "Female" else "sex-btn"

        return male_class, female_class

    @app.callback(
        Output("selected-sex", "data"),
        Input("sex-male-btn", "n_clicks"),
        Input("sex-female-btn", "n_clicks"),
        State("selected-sex", "data"),
        prevent_initial_call=True,
    )
    def update_selected_sex(male_clicks, female_clicks, current_sex):
        trigger = ctx.triggered_id

        if trigger == "sex-male-btn":
            return None if current_sex == "Male" else "Male"

        if trigger == "sex-female-btn":
            return None if current_sex == "Female" else "Female"

        return current_sex

    @app.callback(
        Output("metric-dropdown", "value"),
        Output("year-range", "value"),
        Output("selected-sex", "data", allow_duplicate=True),
        Output("age-group-dropdown", "value"),
        Output("bmi-category-dropdown", "value"),
        Output("selected-smoking", "data", allow_duplicate=True),
        Output("physical-dropdown", "value"),
        Output("salt-dropdown", "value"),
        Output("stress-dropdown", "value"),
        Output("diabetes-dropdown", "value"),
        Output("family-dropdown", "value"),
        Output("selected-country", "data", allow_duplicate=True),
        Input("remove-all-filters-btn", "n_clicks"),
        Input({"type": "remove-filter-chip", "filter": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_filters(remove_all_clicks, chip_clicks):
        trigger = ctx.triggered_id

        default_metric = "Country_HTN_Prevalence_pct"
        default_year_range = [year_min, year_max]

        no_changes = (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

        # IMPORTANT:
        # Dash may trigger this callback when chips are created/re-rendered.
        # Only continue if the actual clicked value is > 0.
        triggered_value = None
        if ctx.triggered:
            triggered_value = ctx.triggered[0].get("value")

        if not triggered_value:
            return no_changes

        # Remove all filters
        if trigger == "remove-all-filters-btn":
            return (
                default_metric,
                default_year_range,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )

        # Remove one clicked filter chip
        if isinstance(trigger, dict):
            filter_key = trigger.get("filter")

            metric_value = no_update
            year_value = no_update
            sex_value = no_update
            age_group_value = no_update
            bmi_category_value = no_update
            smoking_value = no_update
            physical_value = no_update
            salt_value = no_update
            stress_value = no_update
            diabetes_value = no_update
            family_hx_value = no_update
            country_value = no_update

            if filter_key == "metric":
                metric_value = default_metric

            elif filter_key == "year":
                year_value = default_year_range

            elif filter_key == "sex":
                sex_value = None

            elif filter_key == "age_group":
                age_group_value = None

            elif filter_key == "bmi_category":
                bmi_category_value = None

            elif filter_key == "smoking":
                smoking_value = None

            elif filter_key == "physical":
                physical_value = None

            elif filter_key == "salt":
                salt_value = None

            elif filter_key == "stress":
                stress_value = None

            elif filter_key == "diabetes":
                diabetes_value = None

            elif filter_key == "family_hx":
                family_hx_value = None

            elif filter_key == "country":
                country_value = None

            return (
                metric_value,
                year_value,
                sex_value,
                age_group_value,
                bmi_category_value,
                smoking_value,
                physical_value,
                salt_value,
                stress_value,
                diabetes_value,
                family_hx_value,
                country_value,
            )

        return no_changes

    @app.callback(
        Output("selected-country", "data"),
        Input("reset-country-btn", "n_clicks"),
        Input("metric-dropdown", "value"),
        Input("year-range", "value"),
        Input("selected-sex", "data"),
        Input("age-group-dropdown", "value"),
        Input("bmi-category-dropdown", "value"),
        Input("selected-smoking", "data"),
        Input("physical-dropdown", "value"),
        Input("salt-dropdown", "value"),
        Input("stress-dropdown", "value"),
        Input("diabetes-dropdown", "value"),
        Input("family-dropdown", "value"),
        Input({"type": "dynamic-map", "index": "main"}, "clickData"),
        State("selected-country", "data"),
        prevent_initial_call=True,
    )
    def update_selected_country(
        reset_clicks,
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
        click_data,
        current_country,
    ):
        trigger = ctx.triggered_id

        if trigger == "reset-country-btn":
            return None

        if isinstance(trigger, dict) and trigger.get("type") == "dynamic-map":
            if click_data and click_data.get("points"):
                return click_data["points"][0].get("location")

        return current_country

    @app.callback(
        Output("main-content", "children"),
        Input("selected-country", "data"),
        Input("metric-dropdown", "value"),
        Input("year-range", "value"),
        Input("selected-sex", "data"),
        Input("age-group-dropdown", "value"),
        Input("bmi-category-dropdown", "value"),
        Input("selected-smoking", "data"),
        Input("physical-dropdown", "value"),
        Input("salt-dropdown", "value"),
        Input("stress-dropdown", "value"),
        Input("diabetes-dropdown", "value"),
        Input("family-dropdown", "value"),
    )
    def render_content(
        selected_country,
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
    ):
        dff = apply_filters(
            df,
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
        )

        map_df = aggregate_for_map(dff, metric)

        if (
            not selected_country
            or selected_country not in map_df["Country"].astype(str).tolist()
        ):
            return render_overview_content(
                dff=dff,
                map_df=map_df,
                metric=metric,
                year_range=year_range,
                sex=sex,
                age_group=age_group,
                bmi_category=bmi_category,
                smoking=smoking,
                physical=physical,
                salt=salt,
                stress=stress,
                diabetes=diabetes,
                family_hx=family_hx,
                year_min=year_min,
                year_max=year_max,
            )

        return render_country_content(
            dff=dff,
            map_df=map_df,
            metric=metric,
            selected_country=selected_country,
        )


def render_overview_content(
    dff,
    map_df,
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
):
    map_fig = make_map(map_df, metric, compact=False)

    active_filters = build_active_filters_box(
        metric=metric,
        year_range=year_range,
        sex=sex,
        age_group=age_group,
        bmi_category=bmi_category,
        smoking=smoking,
        physical=physical,
        salt=salt,
        stress=stress,
        diabetes=diabetes,
        family_hx=family_hx,
        year_min=year_min,
        year_max=year_max,
    )

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Graph(
                            id={"type": "dynamic-map", "index": "main"},
                            figure=map_fig,
                            className="graph-fill",
                            style={"height": "100%", "width": "100%"},
                            config={
                                "displayModeBar": False,
                                "responsive": True,
                                "scrollZoom": True,
                                "staticPlot": False,
                            },
                        ),
                        className="overview-map-wrap",
                    ),
                    active_filters,
                ],
                className="overview-left-column",
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Overall dataset information",
                                className="panel-title",
                            ),
                            html.Div(info_cards_for_df(dff), className="stats-grid"),
                            html.Div(
                                [
                                    html.H4("Top 5 countries by selected metric"),
                                    dash_table.DataTable(
                                        data=map_df.sort_values(
                                            metric,
                                            ascending=False,
                                        )
                                        .head(5)
                                        .to_dict("records"),
                                        columns=[
                                            {"name": "Country", "id": "Country"},
                                            {
                                                "name": MAP_METRICS.get(metric, metric),
                                                "id": metric,
                                            },
                                        ],
                                        style_table={"overflowX": "auto"},
                                        style_cell={
                                            "padding": "8px",
                                            "fontFamily": "Arial",
                                            "fontSize": 13,
                                        },
                                        style_header={"fontWeight": "bold"},
                                        page_size=10,
                                    ),
                                ],
                                className="datatable-wrap",
                            ),
                        ],
                        className="overview-info-wrap",
                    ),
                    overview_note(),
                ],
                className="overview-right-column",
            ),
        ],
        className="overview-layout",
    )


def render_country_content(dff, map_df, metric, selected_country):
    country_df = dff[dff["Country"] == selected_country].copy()
    compact_map_df = map_df[map_df["Country"] == selected_country].copy()

    map_fig = make_map(
        compact_map_df,
        metric,
        selected_country=selected_country,
        compact=True,
    )

    fig_trend, fig_bp_cat, fig_diabetes = make_country_figures(country_df)

    graph_config = {
        "displayModeBar": False,
        "responsive": True,
    }

    graph_style = {
        "height": "100%",
        "width": "100%",
    }

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Graph(
                            id={"type": "dynamic-map", "index": "main"},
                            figure=map_fig,
                            config=graph_config,
                            className="graph-fill",
                            style=graph_style,
                        ),
                        className="country-map-wrap",
                    ),

                    html.Div(
                        [
                            html.H3(
                                f"{selected_country} overview",
                                className="panel-title",
                            ),
                            html.Div(
                                info_cards_for_df(country_df, selected_country),
                                className="stats-grid country-stats",
                            ),
                        ],
                        className="country-info-wrap",
                    ),
                ],
                className="country-left-column",
            ),

            html.Div(
                [
                    html.H3("Country blood pressure insights", className="panel-title"),

                    html.Div(
                        [
                            dcc.Graph(
                                figure=fig_trend,
                                config=graph_config,
                                className="plot-card plot-card-wide",
                                style=graph_style,
                            ),
                            dcc.Graph(
                                figure=fig_bp_cat,
                                config=graph_config,
                                className="plot-card",
                                style=graph_style,
                            ),
                            dcc.Graph(
                                figure=fig_diabetes,
                                config=graph_config,
                                className="plot-card",
                                style=graph_style,
                            ),
                        ],
                        className="plots-grid",
                    ),
                ],
                className="country-plots-wrap",
            ),
        ],
        className="country-layout",
    )
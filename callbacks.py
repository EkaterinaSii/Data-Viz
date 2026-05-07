from dash import Input, Output, State, ctx, dcc, html, ALL, no_update
from dash.exceptions import PreventUpdate

from config import MAP_METRICS, DEFAULT_MAP_METRIC
from components import (
    build_active_filters_box,
    info_cards_for_df,
    overview_note,
)
from data import apply_filters, aggregate_for_map
from figures import (
    make_country_figures,
    make_historical_bp_figure,
    make_map,
)


def register_callbacks(app, df, year_min: int, year_max: int):
    """
    Registers all Dash callbacks used by the dashboard.

    This includes:
    - custom sex and smoking filter buttons
    - active filter chip removal
    - clear filters button
    - country selection from the map
    - overview/country page rendering
    - BP history chart mode switching
    """

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
        """
        Updates the selected smoking status.

        Clicking an already-selected smoking status clears the selection.
        Clicking a different status replaces the old selection.
        """
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
        """
        Applies the active CSS class to the selected smoking status button.
        """
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
        """
        Applies the active CSS class to the selected sex button.
        """
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
        """
        Updates the selected sex filter.

        Clicking an already-selected sex clears the selection.
        Clicking a different sex replaces the old selection.
        """
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
        Input("clear-filters-btn", "n_clicks"),
        Input({"type": "remove-filter-chip", "filter": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_filters(clear_filters_clicks, chip_clicks):
        """
        Clears all filters or clears one filter chip.

        The sidebar "Clear filters" button clears every filter but keeps
        the selected country.

        Individual active filter chips clear only the matching filter.
        """
        trigger = ctx.triggered_id
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

        if trigger == "clear-filters-btn":
            if not clear_filters_clicks:
                return no_changes

            return (
                DEFAULT_MAP_METRIC,
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
                no_update,
            )

        if isinstance(trigger, dict):
            triggered_value = None

            if ctx.triggered:
                triggered_value = ctx.triggered[0].get("value")

            # Prevent accidental clearing when chips are created or re-rendered.
            if not triggered_value:
                return no_changes

            return clear_single_filter(
                filter_key=trigger.get("filter"),
                default_year_range=default_year_range,
            )

        return no_changes

    @app.callback(
        Output("metric-dropdown", "value", allow_duplicate=True),
        Output("year-range", "value", allow_duplicate=True),
        Output("selected-sex", "data", allow_duplicate=True),
        Output("age-group-dropdown", "value", allow_duplicate=True),
        Output("bmi-category-dropdown", "value", allow_duplicate=True),
        Output("selected-smoking", "data", allow_duplicate=True),
        Output("physical-dropdown", "value", allow_duplicate=True),
        Output("salt-dropdown", "value", allow_duplicate=True),
        Output("stress-dropdown", "value", allow_duplicate=True),
        Output("diabetes-dropdown", "value", allow_duplicate=True),
        Output("family-dropdown", "value", allow_duplicate=True),
        Input("selected-country", "data"),
        prevent_initial_call=True,
    )
    def clear_filters_when_country_selected(selected_country):
        """
        Automatically clears filters when a country is selected.

        This gives the user a clean country-specific view first.
        After the country page opens, filters can still be applied normally.
        """
        if not selected_country:
            return (
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

        return (
            DEFAULT_MAP_METRIC,
            [year_min, year_max],
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
        """
        Updates selected country from map clicks or clears it with reset.

        Normal filter changes should not rewrite selected-country. Returning
        no_update here prevents accidental country resets or repeated filter
        clearing.
        """
        trigger = ctx.triggered_id

        if trigger == "reset-country-btn":
            return None

        if isinstance(trigger, dict) and trigger.get("type") == "dynamic-map":
            if click_data and click_data.get("points"):
                return click_data["points"][0].get("location")

        return no_update

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
        """
        Renders either the overview screen or the selected country screen.

        The same selected filters are applied before rendering. If no country
        is selected, the overview screen is shown. If a valid country is
        selected, the country-specific screen is shown.
        """
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

    @app.callback(
        Output("bp-history-graph", "figure"),
        Input("bp-mode-toggle", "value"),
        Input("selected-country", "data"),
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
        prevent_initial_call=True,
    )
    def update_bp_history_graph(
        bp_mode,
        selected_country,
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
        """
        Updates the historical BP chart when the user switches chart mode.

        Modes:
        - yearly country averages
        - individual database records
        """
        if not selected_country:
            raise PreventUpdate

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

        country_df = dff[dff["Country"] == selected_country].copy()

        return make_historical_bp_figure(country_df, mode=bp_mode or "year")


def clear_single_filter(filter_key: str, default_year_range: list[int]):
    """
    Builds the callback return tuple for clearing one active filter chip.

    Only the selected filter is reset. All other filters return no_update.
    """
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
        metric_value = DEFAULT_MAP_METRIC

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
    """
    Builds the overview screen content.

    The overview contains:
    - global map
    - active filters
    - dataset information cards
    - top 5 countries by selected map metric
    - explanatory note
    """
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

    top_countries = get_top_countries(map_df, metric)

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                f"Global map: {MAP_METRICS.get(metric, metric)}",
                                className="panel-title map-panel-title",
                            ),
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
                        ],
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
                            html.Div(
                                info_cards_for_df(dff),
                                className="stats-grid",
                            ),
                            build_top_countries_card(top_countries, metric),
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


def get_top_countries(map_df, metric):
    """
    Returns the top five countries by the selected metric.

    If the data is empty or the metric is missing, returns an empty list.
    """
    if map_df.empty or metric not in map_df.columns:
        return []

    return (
        map_df.sort_values(metric, ascending=False)
        .head(5)
        .to_dict("records")
    )


def build_top_countries_card(top_countries, metric):
    """
    Builds the ranked top countries card for the overview information panel.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.H4(
                        "Top 5 countries",
                        className="top-countries-title",
                    ),
                    html.Div(
                        MAP_METRICS.get(metric, metric),
                        className="top-countries-subtitle",
                    ),
                ],
                className="top-countries-header",
            ),
            html.Div(
                [
                    build_rank_row(index, row, metric)
                    for index, row in enumerate(top_countries)
                ],
                className="rank-list",
            ),
        ],
        className="top-countries-card",
    )


def build_rank_row(index, row, metric):
    """
    Builds one row inside the top countries ranked list.
    """
    return html.Div(
        [
            html.Div(
                str(index + 1),
                className="rank-badge",
            ),
            html.Div(
                [
                    html.Div(
                        row.get("Country", "Unknown"),
                        className="rank-country",
                    ),
                    html.Div(
                        format_metric_value(row.get(metric)),
                        className="rank-value",
                    ),
                ],
                className="rank-content",
            ),
        ],
        className="rank-row",
    )


def format_metric_value(value):
    """
    Formats a numeric metric value for display in the top countries card.
    """
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "N/A"


def render_country_content(dff, map_df, metric, selected_country):
    """
    Builds the selected-country dashboard screen.

    The country screen contains:
    - focused country map
    - country summary cards
    - historical BP chart with mode toggle
    - BP category by age group chart
    - BP category by diabetes status chart
    """
    country_df = dff[dff["Country"] == selected_country].copy()
    compact_map_df = map_df[map_df["Country"] == selected_country].copy()

    map_fig = make_map(
        compact_map_df,
        metric,
        selected_country=selected_country,
        compact=True,
    )

    fig_trend, fig_bp_cat, fig_diabetes = make_country_figures(
        country_df,
        bp_mode="year",
    )

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
                        [
                            html.H3(
                                f"Focused map: {selected_country}",
                                className="panel-title map-panel-title",
                            ),
                            dcc.Graph(
                                id={"type": "dynamic-map", "index": "main"},
                                figure=map_fig,
                                config=graph_config,
                                className="graph-fill",
                                style=graph_style,
                            ),
                        ],
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
                    html.H3(
                        "Country blood pressure insights",
                        className="panel-title",
                    ),
                    html.Div(
                        [
                            build_bp_history_card(
                                fig_trend=fig_trend,
                                graph_config=graph_config,
                                graph_style=graph_style,
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


def build_bp_history_card(fig_trend, graph_config, graph_style):
    """
    Builds the wide historical BP chart card with the Yearly/By record toggle.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        "View:",
                        className="bp-mode-label",
                    ),
                    dcc.RadioItems(
                        id="bp-mode-toggle",
                        options=[
                            {
                                "label": "Yearly",
                                "value": "year",
                            },
                            {
                                "label": "By record",
                                "value": "record",
                            },
                        ],
                        value="year",
                        inline=True,
                        className="bp-mode-toggle",
                        labelClassName="bp-mode-option",
                    ),
                ],
                className="bp-mode-toolbar",
            ),
            dcc.Graph(
                id="bp-history-graph",
                figure=fig_trend,
                config=graph_config,
                className="graph-fill",
                style=graph_style,
            ),
        ],
        className="plot-card plot-card-wide bp-history-card",
    )
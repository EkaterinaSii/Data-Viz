from dash import Dash

from callbacks import register_callbacks
from config import DATA_PATH
from data import load_data
from layout import build_layout


def get_year_bounds(df):
    """
    Calculates the minimum and maximum year available in the dataset.

    If the Year column is missing or empty, default values are used.

    Parameters:
    - df: Loaded dashboard dataframe.

    Returns:
    - A tuple containing year_min and year_max.
    """
    if "Year" not in df.columns:
        return 2000, 2024

    year_values = df["Year"].dropna()

    if year_values.empty:
        return 2000, 2024

    return int(year_values.min()), int(year_values.max())


def create_app():
    """
    Creates and configures the Dash application.

    This function:
    - loads the dataset
    - calculates available year bounds
    - creates the Dash app
    - builds the layout
    - registers callbacks
    - exposes the Flask server for deployment

    Returns:
    - The configured Dash app instance.
    """
    df = load_data(DATA_PATH)
    year_min, year_max = get_year_bounds(df)

    app = Dash(
        __name__,
        suppress_callback_exceptions=True,
    )

    app.title = "Blood Pressure Dashboard"
    app.layout = build_layout(df, year_min, year_max)

    register_callbacks(app, df, year_min, year_max)

    return app


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(debug=False)
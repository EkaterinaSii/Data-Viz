from dash import Dash

from callbacks import register_callbacks
from config import DATA_PATH
from data import load_data
from layout import build_layout


df = load_data(DATA_PATH)

year_min = (
    int(df["Year"].min())
    if "Year" in df.columns and df["Year"].notna().any()
    else 2000
)

year_max = (
    int(df["Year"].max())
    if "Year" in df.columns and df["Year"].notna().any()
    else 2024
)

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.title = "Blood Pressure Dashboard"
app.layout = build_layout(df, year_min, year_max)

register_callbacks(app, df, year_min, year_max)


if __name__ == "__main__":
    app.run(debug=False)
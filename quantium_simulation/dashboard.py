"""Dash app for visualizing pink morsel sales."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

try:
    from quantium_simulation.processing import DEFAULT_OUTPUT_FILE, sales_processor
except ModuleNotFoundError:
    from processing import DEFAULT_OUTPUT_FILE, sales_processor

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = Path(DEFAULT_OUTPUT_FILE)


def load_pink_sales_data() -> pd.DataFrame:
    """Load processed pink sales data, generating it if needed."""
    if not DATA_FILE.exists():
        sales_processor()

    data_frame = pd.read_csv(DATA_FILE, parse_dates=["date"])
    data_frame["sales"] = pd.to_numeric(data_frame["sales"])
    return data_frame.sort_values("date")  # The dataset is small


data = load_pink_sales_data()
region_options = [{"label": "All regions", "value": "all"}] + [
    {"label": region.title(), "value": region}
    for region in sorted(data["region"].unique())
]
time_options = [
    {"label": "Day", "value": "day"},
    {"label": "Week", "value": "week"},
    {"label": "Month", "value": "month"},
]

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Pink Morsel Sales Dashboard"),
        html.Div(
            [
                html.P("Region affects both figures. Time grouping only affects the first figure."),
                html.Label("Region"),
                dcc.Dropdown(
                    id="region-filter",
                    options=region_options,
                    value="all",
                    clearable=False,
                    style={"width": "240px"},
                ),
            ],
            style={"marginBottom": "16px"},
        ),
        html.Div(
            [
                html.Label("Time Grouping"),
                dcc.Dropdown(
                    id="time-filter",
                    options=time_options,
                    value="day",
                    clearable=False,
                    style={"width": "240px"},
                ),
            ],
            style={"marginBottom": "24px"},
        ),
        dcc.Graph(id="daily-sales-chart"),
        dcc.Graph(id="region-sales-chart"),
    ]
)


@app.callback(
    Output("daily-sales-chart", "figure"),
    Output("region-sales-chart", "figure"),
    Input("region-filter", "value"),
    Input("time-filter", "value"),
)
def update_charts(selected_region: str, selected_time: str):
    """Update charts based on the selected region."""
    filtered = (
        data if selected_region == "all" else data[data["region"] == selected_region]
    )

    if selected_time == "week":
        trend_sales = (
            filtered.groupby(pd.Grouper(key="date", freq="W"))["sales"].sum().reset_index()
        )
        trend_label = "Weekly"
    elif selected_time == "month":
        trend_sales = (
            filtered.groupby(pd.Grouper(key="date", freq="MS"))["sales"].sum().reset_index()
        )
        trend_label = "Monthly"
    else:
        trend_sales = filtered.groupby("date", as_index=False)["sales"].sum()
        trend_label = "Daily"

    region_sales = filtered.groupby("region", as_index=False)["sales"].sum()

    daily_title = f"{trend_label} Pink Morsel Sales"
    if selected_region != "all":
        daily_title = f"{trend_label} Pink Morsel Sales: {selected_region.title()}"

    daily_figure = px.line(
        trend_sales,
        x="date",
        y="sales",
        title=daily_title,
    )

    region_figure = px.bar(
        region_sales,
        x="region",
        y="sales",
        title="Total Sales by Region",
    )

    return daily_figure, region_figure


def main() -> None:
    """Run the Dash development server."""
    app.run(debug=True)


if __name__ == "__main__":
    main()

import sys
from pathlib import Path
from typing import Iterator

from dash import dcc, html
from dash.development.base_component import Component

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantium_simulation import dashboard


def test_load_pink_sales_data_has_expected_columns():
    data_frame = dashboard.load_pink_sales_data()

    assert list(data_frame.columns) == ["date", "region", "sales"]
    assert not data_frame.empty


def iter_components(node: object) -> Iterator[Component]:
    if node is None:
        return

    if isinstance(node, Component):
        yield node
        yield from iter_components(getattr(node, "children", None))
        return

    if isinstance(node, (list, tuple)):
        for child in node:
            yield from iter_components(child)


def test_layout_contains_expected_components():
    layout = dashboard.app.layout
    components = list(iter_components(layout))
    dropdowns = [
        component for component in components if isinstance(component, dcc.Dropdown)
    ]
    graphs = [component for component in components if isinstance(component, dcc.Graph)]

    assert isinstance(layout, html.Div)
    assert len(dropdowns) >= 2
    assert len(graphs) >= 2


def test_update_charts_for_all_regions_daily():
    daily_figure, region_figure = dashboard.update_charts("all", "day")

    assert daily_figure.layout.title.text == "Daily Pink Morsel Sales"
    assert region_figure.layout.title.text == "Total Sales by Region"
    assert len(daily_figure.data) == 1
    assert len(region_figure.data) == 1


def test_update_charts_for_single_region_monthly():
    daily_figure, region_figure = dashboard.update_charts("north", "month")

    assert daily_figure.layout.title.text == "Monthly Pink Morsel Sales: North"
    assert region_figure.layout.title.text == "Total Sales by Region"
    assert len(daily_figure.data[0]["x"]) > 0
    assert set(region_figure.data[0]["x"]) == {"north"}

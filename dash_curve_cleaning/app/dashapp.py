import json
from typing import Dict, List, Optional, Tuple

import numpy as np
import redis
import woodpecker as wp
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from furl import furl
from plotly.graph_objs import Figure as PlotlyFigure, Scattergl
from pydantic import BaseModel, validator

BaseModel.Config.validate_all = True

# WIDTH = int(os.getenv("WIDTH"))
# HEIGHT = int(os.getenv("HEIGHT"))
# DEBUG = int(os.getenv("DEBUG"))

WIDTH = 1200
HEIGHT = 600
DEBUG = 1

if DEBUG:
    wp.set_level("DEBUG")
else:
    wp.set_level("INFO")

redis_cl = redis.Redis(
    # host=os.getenv('REDIS_HOST'),
    # port=int(os.getenv('REDIS_PORT')),
    # password=os.getenv('REDIS_PASSWORD'),
)

COLORS = [
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
]

LINE_COLORS = [
    "lightblue",
    "lightsalmon",
]


class LineShape(BaseModel):
    """A model representative of a Plotly line shape."""

    class Line(BaseModel):
        color: str = "LightSeaGreen"
        width: int = 4
        dash: str = "solid"

    editable: bool = True
    xref: str = "x"
    yref: str = "y"
    layer: str = "above"
    opacity: int = 1
    line: Line = Line()
    type: str = "line"
    x0: float = None
    y0: float = None
    x1: float = None
    y1: float = None

    def update(self, line: "LineShape"):
        self.x1 = line.x1
        self.y1 = line.y1


class CircleShape(BaseModel):
    """A model representative of a Plotly circle shape."""

    type: str = "circle"
    editable = False
    x0: float = 0
    y0: float = 0
    x1: float = None
    y1: float = None
    no_x: bool = False
    no_y: bool = False

    fillcolor = "PaleTurquoise"
    line = LineShape.Line()

    @validator("x1", check_fields=False)
    def validate_x0(cls, v: Optional[float], values: Dict, **kwargs):
        return values["x0"] + 1

    @validator("y1", check_fields=False)
    def validate_y1(cls, v: Optional[float], values: Dict, **kwargs):
        return values["y0"] + 1


class FigureModel(BaseModel):
    """A model representative of a Plotly figure. We usualy create an object of this class
    using the image dictionary available inside a dash app callback. Working with this
    model is easier than working with the image in dicionary format because we have at hand
    the attribute names and methods that help us perform some necessary operations on the
    figure."""

    CIRCLE_SIZE = 10

    class Data(BaseModel):
        class Marker(BaseModel):
            color: str = "#636efa"
            symbol: str = "circle"
            size: int = 5

        x: List[float] = []
        y: List[float] = []
        marker: Marker = Marker()
        xaxis: str = "x"
        yaxis: str = "y"
        type: str = "scatter"
        legendgroup: str = ""
        mode: str = "markers"
        name: str = ""
        orientation: str = "v"
        showlegend: bool = True

    class Layout(BaseModel):
        class Axis(BaseModel):
            class Title(BaseModel):
                text: str

            range: Tuple[float, float] = (0, 1)
            title: Title

        shapes: List[CircleShape] = []
        yaxis: Axis
        xaxis: Axis

    data: List[Data] = []
    layout: Layout
    point_groups: Dict[str, List[str]]
    point_names: List[str]
    assets: List[str]
    x_name: str
    y_name: str

    @property
    def x_range(self) -> float:
        return self.layout.xaxis.range[1] - self.layout.xaxis.range[0]

    @property
    def y_range(self) -> float:
        return self.layout.yaxis.range[1] - self.layout.yaxis.range[0]

    @property
    def scale_x(self) -> float:
        """Returns the size in pixels of a single unit of the X variable."""

        return self.x_range / WIDTH

    @property
    def scale_y(self) -> float:
        """Returns the size in pixels of a single unit of the y variable."""

        return self.y_range / HEIGHT

    def __iter__(self):
        return iter(self.layout.shapes)

    def set_titles(self, x_title, y_title):
        """Sets the figure titles for the x and y axis."""
        self.layout.xaxis.title = FigureModel.Layout.Axis.Title(text=x_title)
        self.layout.yaxis.title = FigureModel.Layout.Axis.Title(text=y_title)

    def set_ranges(self, min_x: float, max_x: float, min_y: float, max_y: float):
        """Sets the figure ranges for the x and y axis."""
        self.layout.xaxis.range = (
            min_x - (max_x - min_x) * 0.05,
            max_x + (max_x - min_x) * 0.05,
        )
        self.layout.yaxis.range = (
            min_y - (max_y - min_y) * 0.05,
            max_y + (max_y - min_y) * 0.05,
        )

    def populate_figure_data(self, uuid: str, plot, stages):
        """Populates the figure data based on the data saved in the redis server."""

        min_x = np.inf
        max_x = -np.inf
        min_y = np.inf
        max_y = -np.inf

        if len(self.data[0].x) == 0:

            self.data = []
            i = 0
            for stage_idx, stage in enumerate(stages):
                for _, asset in enumerate(self.assets):
                    self.data.append(FigureModel.Data())
                    x = [
                        float(v)
                        for v in redis_cl.lrange(
                            f"{uuid}:{plot}:{asset}:{self.x_name}:{stage}", 0, -1
                        )
                    ]
                    y = [
                        float(v)
                        for v in redis_cl.lrange(
                            f"{uuid}:{plot}:{asset}:{self.y_name}:{stage}", 0, -1
                        )
                    ]

                    wp.debug(len(x))
                    wp.debug(len(y))

                    self.data[i].x = x
                    self.data[i].y = y
                    self.data[i].name = f"{asset}:{stage}"
                    self.data[i].legendgroup = f"{asset}:{stage}"
                    self.data[i].marker.color = COLORS[stage_idx]

                    if len(self.data[i].x) > 0 and len(self.data[i].y) > 0:
                        min_x = min(min_x, min(self.data[i].x))
                        max_x = max(max_x, max(self.data[i].x))
                        min_y = min(min_y, min(self.data[i].y))
                        max_y = max(max_y, max(self.data[i].y))

                    i += 1

            return min_x, max_x, min_y, max_y

        return None, None, None, None

    def populate_points(self, uuid: str):
        """Populates the image points based on the data saved in the redis server."""

        self.layout.shapes = []
        for point in self.point_names:
            try:
                x = float(redis_cl.mget(f"{uuid}:{point}.x")[0])
                no_x = False
            except TypeError:
                x = np.mean(self.layout.xaxis.range)
                no_x = True

            try:
                y = float(redis_cl.mget(f"{uuid}:{point}.y")[0])
                no_y = False
            except TypeError:
                y = np.mean(self.layout.yaxis.range)
                no_y = True

            wp.debug(f"points: {y}")

            self.layout.shapes.append(
                CircleShape(
                    x0=x,
                    y0=y,
                    x1=x + self.scale_x * self.CIRCLE_SIZE,
                    y1=y + self.scale_y * self.CIRCLE_SIZE,
                    no_x=no_x,
                    no_y=no_y,
                )
            )

    def populate_lines(self):
        """Draws a set of lines connecting each points group."""

        point_idx = 0
        for i, (point_group_name, point_group) in enumerate(self.point_groups.items()):
            x, y, point_idx = self._get_line_points(point_group, point_idx)

            wp.debug(f"Adding scatter points for point_group {point_group}")
            wp.debug(f"x: {x}")
            wp.debug(f"y: {y}")

            data = FigureModel.Data()
            data.name = point_group_name
            data.x = x
            data.y = y
            data.mode = "lines"
            data.marker.color = LINE_COLORS[i]
            data.showlegend = True
            data.legendgroup = point_group_name

            self.data.append(data)

    def update_points(self, uuid: str):
        """Updates the figure points based on the data stored in the redis server."""

        for i, point in enumerate(self.layout.shapes):
            try:
                float(redis_cl.mget(f"{uuid}:{self.point_names[i]}.x")[0])
                no_x = False
            except TypeError:
                no_x = True

            try:
                float(redis_cl.mget(f"{uuid}:{self.point_names[i]}.y")[0])
                no_y = False
            except TypeError:
                no_y = True

            point.no_x = no_x
            point.no_y = no_y
            if point.no_x:
                point.x0 = np.mean(self.layout.xaxis.range)
            if point.no_y:
                point.y0 = np.mean(self.layout.yaxis.range)
            point.x1 = point.x0 + self.scale_x * self.CIRCLE_SIZE
            point.y1 = point.y0 + self.scale_y * self.CIRCLE_SIZE

    def update_lines(self):
        """Updates the drawn lines based on the new position of the points."""

        point_idx = 0
        for point_group_name, point_group in self.point_groups.items():
            x, y, point_idx = self._get_line_points(point_group, point_idx)

            wp.debug(f"Sending {x, y}")
            for data_idx in range(len(self.data)):
                if self.data[data_idx].name == point_group_name:
                    self.data[data_idx].x = x
                    self.data[data_idx].y = y

    def _get_line_points(
        self, point_group, point_idx
    ) -> Tuple[List[float], List[float], float]:
        """Iterates over all the points of a points group and returns the data necessary
        to plot a set of lines connecting each point."""

        x = []
        y = []
        if len(point_group) > 1:
            for point in point_group:
                x.append(
                    (
                        self.layout.shapes[point_idx].x0
                        + self.layout.shapes[point_idx].x1
                    )
                    / 2
                )
                y.append(
                    (
                        self.layout.shapes[point_idx].y0
                        + self.layout.shapes[point_idx].y1
                    )
                    / 2
                )

                point_idx += 1

        elif len(point_group) == 1:
            point = self.layout.shapes[point_idx]
            if point.no_x:
                x.extend([self.layout.xaxis.range[0], self.layout.xaxis.range[1]])
                value = (point.y0 + point.y1) / 2
                y.extend([value, value])

            elif point.no_y:
                value = (point.x0 + point.x1) / 2
                x.extend([value, value])
                y.extend([self.layout.yaxis.range[0], self.layout.yaxis.range[1]])

            elif not point.no_x and not point.no_y:
                value = (point.x0 + point.x1) / 2
                x.extend([value, value])
                y.extend([self.layout.yaxis.range[1], (point.y0 + point.y1) / 2])

                x.extend([(point.x0 + point.x1) / 2, self.layout.xaxis.range[1]])
                value = (point.y0 + point.y1) / 2
                y.extend([value, value])

            point_idx += 1
        return x, y, point_idx

    def save_points(self, uuid: str):
        """Saves the point parameters on the redis server."""

        for i, point in enumerate(self.point_names):
            points_dict = {}
            if not self.layout.shapes[i].no_x:
                points_dict.update({f"{uuid}:{point}.x": self.layout.shapes[i].x0})
            if not self.layout.shapes[i].no_y:
                points_dict.update({f"{uuid}:{point}.y": self.layout.shapes[i].y0})
            wp.debug(points_dict)
            redis_cl.mset(points_dict)


class Url:
    """Used to parse the url."""

    def __init__(self, url: str):
        self._url = furl(url)
        self.uuid = self._fetch_param("uuid")
        self.plot = self._fetch_param("plot")
        self.assets = self._parse_list_str(self._fetch_param("assets"))
        self.x_name = self._fetch_param("x_name")
        self.y_name = self._fetch_param("y_name")
        self.stages = self._parse_list_str(self._fetch_param("stages"))
        point_group_names = self._parse_list_str(self._fetch_param("point_group_names"))
        self.point_groups = {
            group_name: self._parse_list_str(self._fetch_param(group_name))
            for group_name in point_group_names
        }
        self.point_names = [
            line_name for group in self.point_groups.values() for line_name in group
        ]

    def _fetch_param(self, name: str):
        try:
            return self._url.args.pop(name)
        except KeyError:
            raise Exception(f"Invalid url provided. {name} not found.")

    @staticmethod
    def _parse_list_str(list_str: str) -> List[str]:
        """Parses a string list in format: a,b,c,d."""
        return list_str.split(",")


def create_empty_plotly_figure() -> PlotlyFigure:
    """Creates an empty plotly figure."""

    figure = PlotlyFigure()
    scatter = Scattergl()

    figure.add_trace(scatter)
    figure.update_layout(clickmode="event+select")
    figure.update_layout(hovermode=False)
    figure.update_traces(marker_size=1)
    figure.update_layout(
        width=WIDTH,
        height=HEIGHT,
        title="Power Curve Cleaning",
        xaxis_title="",
        yaxis_title="",
    )

    return figure


def update_figure_dct_layout(figure_dct: Dict, figure: FigureModel):
    layout_dct = figure.layout.dict()
    for shape in layout_dct["shapes"]:
        del shape["no_x"]
        del shape["no_y"]
    figure_dct["layout"].update(layout_dct)


def update_figure_dct_data(figure_dct: Dict, figure: FigureModel):
    figure_dct["data"] = [data.dict() for data in figure.data]


def create_dash_app(requests_pathname_prefix: str = None) -> Dash:
    app = Dash(
        __name__,
        requests_pathname_prefix=requests_pathname_prefix,
    )
    app.scripts.config.serve_locally = False

    empty_figure = create_empty_plotly_figure()

    # Depending on if DEBUG is active or not, create an app with a different layout.
    if DEBUG:
        styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}
        app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                dcc.Graph(
                    id="figure",
                    figure=empty_figure,
                    config=dict(editable=True),
                ),
                html.Div(
                    [
                        html.Pre(id="relayout-data", style=styles["pre"]),
                    ]
                ),
                html.Div(
                    [
                        html.Pre(id="figure_dict", style=styles["pre"]),
                    ]
                ),
            ]
        )

        callback = app.callback(
            Output("relayout-data", "children"),
            Output("figure_dict", "children"),
            Output("figure", "figure"),
            Input("url", "href"),
            Input("figure", "figure"),
            Input("figure", "relayoutData"),
        )
    else:
        app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                dcc.Graph(
                    id="figure",
                    figure=empty_figure,
                    config=dict(editable=True),
                ),
            ]
        )

        callback = app.callback(
            Output("figure", "figure"),
            Input("url", "href"),
            Input("figure", "figure"),
            Input("figure", "relayoutData"),
        )

    @callback
    def update_image(href: str, figure_dct: Dict, relayout_data: Dict):
        """Callback used to update the image. We define our own model of the figure,
        which we use to make some necessary operations, then we use this model to
        update the dictionary corresponding to the true figure that is being displayed.."""

        url = Url(href)

        # Create our own figure model based on the figure dictionary available
        # inside this callback.
        figure = FigureModel(
            assets=url.assets,
            x_name=url.x_name,
            y_name=url.y_name,
            point_names=url.point_names,
            point_groups=url.point_groups,
            **figure_dct,
        )

        figure.set_titles(url.x_name, url.y_name)

        # Fetch the axis data from redis.
        min_x, max_x, min_y, max_y = figure.populate_figure_data(
            url.uuid, url.plot, url.stages
        )

        if min_x is not None:
            figure.set_ranges(min_x, max_x, min_y, max_y)

        # If the figure doesn't yet have any points, fetch them from the redis server.
        if len(figure.layout.shapes) == 0:
            figure.populate_points(url.uuid)
            figure.populate_lines()

        figure.update_points(url.uuid)
        figure.update_lines()

        # Save the points on the redis server.
        figure.save_points(url.uuid)

        # Update the figure dictionary based on the changes made to our figure model.
        update_figure_dct_layout(figure_dct, figure)
        update_figure_dct_data(figure_dct, figure)

        if DEBUG:
            return (
                json.dumps(relayout_data, indent=2),
                json.dumps(figure_dct, indent=2),
                figure_dct,
            )
        else:
            return figure_dct

    return app

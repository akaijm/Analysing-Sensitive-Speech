# Importing modules
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

from app import app

layout = html.Div([
            "Time Series Graph"
        ], className="border", style={"display": "flex","justify-content": "center","align-items": "center", "height":"500px"})
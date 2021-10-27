# Importing modules
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

from app import app
HEADER_FONT_SIZE = 16
BODY_FONT_SIZE = 25

layout = dbc.Row([
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Posts",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'numPosts',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'avgPostLen',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Comments",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'numComments',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'avgCommentLen',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Total Users",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'numUsers',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'userDescription',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Peak Hour",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'peakHour',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'peakHourAvg',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Peak Day",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'peakDay',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'peakDayAvg',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
            dbc.Col([
                dbc.Card([
                dbc.CardHeader("Peak Month",  style={'font-size':HEADER_FONT_SIZE}),
                dbc.CardBody(
                    [html.H1(id = 'peakMonth',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                        html.P(id = 'peakMonthAvg',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ]),
        ])
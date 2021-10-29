# Importing modules
import pandas as pd

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np

import plotly.express as px
import plotly.graph_objs as go

from app import app
from apps import topic_modeling, desc_analyses, time_series, sentiment_analysis, ecdf, agg_network, post_cent_network, absa, emotion_classif

# Default dataset
# can change this dataset, just using it for the labels!
text_df = pd.read_csv("outputs/text_data.csv")
unique_labs = list(text_df['pred_label'].unique())
unique_labs.sort()
unique_labs.insert(0, "all")

app.layout = html.Div([
    dcc.Tabs(id='tabs_dashboard', value='overall', children=[
        dcc.Tab(
            html.Div([
                html.H2("Dashboard for Analyzing Sensitive Speech",
                        style={'textAlign': 'center'}),
                html.Div([html.Label("Select a Label:"),
                      dcc.Dropdown(
                    id='selected_label',
                    options=[{'label': i.capitalize(), 'value': i}
                         for i in unique_labs],
                    multi=False,
                    clearable=False,
                    value='all'
                )]),
                html.Div([desc_analyses.layout], className="mt-3"),
                html.Div([topic_modeling.layout], className="mt-2"),
                dbc.Row([
                    dbc.Col([time_series.layout]),
                    dbc.Col([sentiment_analysis.layout])
                ], className="mt-3"),
                html.Div([ecdf.layout], className="mt-3"),
                dbc.Row([
                    dbc.Col([absa.layout]),
                    dbc.Col([emotion_classif.layout])
                ], className="mt-3"),
                html.Br()
            ], style={
                "paddingLeft": '30px',
                "paddingRight": '30px',
                "paddingTop": '30px'
            }), label='Overall', value='overall'),
        dcc.Tab(
            html.Div([
                html.H2("Dashboard for Analyzing Sensitive Speech",
                        style={'textAlign': 'center'}),
                html.Div([agg_network.layout], className="mt-3"),
                html.Div([post_cent_network.layout], className="mt-3")], style={
                "paddingLeft": '30px',
                "paddingRight": '30px',
                "paddingTop": '30px'
            }), label='Network Graphs', value='network_graphs'),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)

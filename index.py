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
text_df = pd.read_csv("outputs/time_series_graphs/time_elapsed_filtered.csv")
unique_labs = list(text_df['post_text_pred'].unique())
unique_labs.sort()
unique_labs.insert(0, "all")
unique_groups = list(text_df['group'].unique())
unique_groups.sort()
unique_groups.insert(0, "all")

app.layout = html.Div([
    dcc.Tabs(id='tabs_dashboard', value='prelim_anal', children=[
        dcc.Tab(
            html.Div([
                html.H2("Dashboard for Analyzing Sensitive Speech",
                        style={'textAlign': 'center'}),
                
                html.Div([html.Label("Filter by Label:"),
                      dcc.Dropdown(
                    id='selected_label',
                    options=[{'label': i.capitalize(), 'value': i}
                         for i in unique_labs],
                    multi=False,
                    clearable=False,
                    value='all'
                )],style={'display':'inline-block', 'width': '50%','padding-right':20}),
                html.Div([html.Label("Filter by Group:"),
                      dcc.Dropdown(
                    id='selected_group',
                    options=[{'label': i.capitalize(), 'value': i}
                         for i in unique_groups],
                    multi=False,
                    clearable=False,
                    value='all'
                )],style={'display':'inline-block', 'width': '50%',}),
                html.Div([desc_analyses.layout], className="mt-3"),
                html.Div([topic_modeling.layout], className="mt-2"),
                dbc.Row([
                    dbc.Col([time_series.layout]),
                    dbc.Col([sentiment_analysis.layout])
                ], className="mt-3"),
                html.Div([ecdf.layout], className="mt-3"),
                html.Br()
            ], style={
                "paddingLeft": '30px',
                "paddingRight": '30px',
                "paddingTop": '30px'
            }), label='Preliminary Analyses', value='prelim_anal'),
        dcc.Tab(
            html.Div([
                html.H2("Dashboard for Analyzing Sensitive Speech",
                        style={'textAlign': 'center'}),
                dbc.Row([
                    dbc.Col([absa.layout]),
                    dbc.Col([emotion_classif.layout])
                ], className="mt-3"),
            ], style={
                "paddingLeft": '30px',
                "paddingRight": '30px',
                "paddingTop": '30px'
            }), label='Emotion Analyses', value='emotion_analyses'
        ),
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

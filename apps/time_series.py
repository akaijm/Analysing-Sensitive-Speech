# Importing modules
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
from pandas import Timestamp

import plotly.express as px
import plotly.graph_objs as go

from app import app

data_filtered = pd.read_csv('outputs/time_series_graphs/time_elapsed_filtered.csv',encoding="utf-8")
data_filtered['post_time'] = pd.to_datetime(data_filtered['post_time'])
data_filtered['comment_time'] = pd.to_datetime(data_filtered['comment_time'])
data_filtered['time_elapsed'] = pd.to_timedelta(data_filtered['time_elapsed'])

layout = html.Div([
            dcc.Markdown("**Post/Comment Frequency Over Time**",style={'color': 'black', 'fontSize': 25,'text-align': 'center'}),
            html.Div([
                dcc.Markdown('Aggregation Period'),
                dcc.Dropdown(
                    id='Aggregation Period',
                    options=[{'label': 'Yearly', 'value': 'Yearly'},{'label': 'Monthly', 'value': 'Monthly'},
                            {'label': 'Daily', 'value': 'Daily'}],
                    value='Monthly'
                )], style={'width':'30%', 'display':'inline-block'}),

            html.Div([
                dcc.Markdown('Content Type'),
                dcc.Dropdown(
                    id='Content Type',
                    options=[{'label': 'All', 'value': 'All'}, {'label': 'Posts', 'value': 'Posts'},{'label': 'Comments', 'value': 'Comments'}],
                    value='All'
                )], style={'width':'30%', 'padding-left':50, 'display':'inline-block'}),

                
            dcc.Graph(id = 'monthly_time_series')])

@app.callback(
    Output('monthly_time_series', 'figure'),
    [Input('Aggregation Period', 'value'),
    Input('selected_label', 'value'),
    Input('Content Type', 'value'),
    Input('selected_group', 'value')])

def update_time_series(time_frame, label, content_type, group):

    post_time = data_filtered.loc[data_filtered.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True).copy()
    post_time = post_time.rename(columns = {'post_text_pred':'label', 'post_time':'time'})
    post_time['type'] = 'post'

    #Prepare comments data
    comment_time = data_filtered[data_filtered['hashed_comment_id'] != '0'].copy()
    comment_time = comment_time.rename(columns = {'comment_text_pred':'label', 'comment_time':'time'})
    comment_time['type'] = 'comment'

    #Filter by chosen content type
    if content_type == 'Posts':
        timeSeries = post_time
    elif content_type == 'Comments':
        timeSeries = comment_time
    else:
        timeSeries = pd.concat([post_time, comment_time])

    #Filter by selected label
    if label != 'all':
        timeSeries = timeSeries[timeSeries['label'] == label]

    #Filter by selected group
    if group != 'all':
        timeSeries = timeSeries[timeSeries['group'] == group]

    #Aggregate by chosen timeframe
    if time_frame == 'Yearly':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:x.year)
    elif time_frame == 'Monthly':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, 1))
    elif time_frame == 'Daily':
        timeSeries['trunc_time'] = timeSeries['time'].apply(lambda x:Timestamp(x.year, x.month, x.day))


    graphPlot = timeSeries[['label', 'trunc_time']].groupby(['trunc_time', 'label']).size().reset_index().rename(columns = {0:'Frequency'})

    fig = px.area(graphPlot, x='trunc_time', y='Frequency', color = 'label',
        labels = {"trunc_time":"Date"})
    
    #Set yearly intervals
    if time_frame == 'Yearly':
        fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            dtick = 1
        )
    )
    return fig

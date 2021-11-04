# Importing modules
import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime 
from dateutil import parser

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq

from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app import app

########### data loading ###########
df = pd.read_csv('outputs/time_series_graphs/time_elapsed_filtered.csv',encoding="utf-8")

######### data processing functions ########################

def handletime(df):
    df['post_time'] = pd.to_datetime(df['post_time'])
    df['comment_time'] = pd.to_datetime(df['comment_time'])
    df['time_elapsed'] = pd.to_timedelta(df['time_elapsed'])
    
    df['time_elapsed_days'] = df.time_elapsed.apply(lambda x: x.days)
    df['time_elapsed_hours'] = df.time_elapsed.apply(lambda x:x.days*24 + x.seconds//3600)
    df['time_elapsed_minutes'] = df.time_elapsed.apply(lambda x:x.seconds//60)
    
    df['comment_date'] = df['comment_time'].apply(lambda x: x.date())
    df['comment_month'] = df['comment_date'].apply(lambda x: x.month )
    df['comment_year'] = df['comment_date'].apply(lambda x: x.year )
    df['post_date'] = df['post_time'].apply(lambda x: x.date())
    df['post_month'] = df['post_date'].apply(lambda x: x.month )
    df['post_year'] = df['post_date'].apply(lambda x: x.year )
    
    return df

# aggregation for time series
def sentiment_ts_df(df, label,group, porc, freq):
    if (label=='all') and (group=='all'):
        df=df
    elif label=='all':
        df = df[df.group==group]
    elif group=='all':
        df = df[df.post_text_pred==label]
    else:
        df = df[df.group==group]
        df = df[df.post_text_pred==label]
    try:
        df = df[df.include==1]
        df = handletime(df)
    except:
        return pd.DataFrame([], columns=['date', 'sentiment_score', 'count'])

    if porc=='posts':
        df = df[df.comment_text.isnull()]
        if freq=='month':
            groupbycol = ['post_year','post_month']
        else:
            groupbycol = ['post_date']
    else:
        df = df[~df.comment_text.isnull()]
        if freq=='month':
            groupbycol = ['comment_year','comment_month']
        else:
            groupbycol = ['comment_date']
    
    df_agg = df.groupby(groupbycol)[['sentiment','hashed_comment_id']] \
                           .agg(sentiment_score=('sentiment','mean'),
                                count = ('hashed_comment_id','count')
                                ).sort_values(groupbycol).reset_index()
    if freq=='month':
        df_agg['day'] = 1
        groupbycol.append('day')
        df_agg['date']=pd.to_datetime(dict(year=df_agg[groupbycol[0]], month=df_agg[groupbycol[1]], day=df_agg[groupbycol[2]]))
    else:
        df_agg.rename(columns={groupbycol[0]: 'date'}, inplace=True)
    return df_agg

# aggregation for time elapsed
def sentiment_te_df(df, label,group, freq):
    # if label=='all':
    #     df = df
    # else:
    #     df = df[df.post_text_pred==label]
    # df = df[df.include==1]
    # df = handletime(df)
        
    if freq == 'days':
        colname = 'time_elapsed_days'
    elif freq == 'hours':
        colname = 'time_elapsed_hours'
    elif freq == 'minutes':
        colname = 'time_elapsed_minutes'
        
    if (label=='all') and (group=='all'):
        df=df
    elif label=='all':
        df = df[df.group==group]
    elif group=='all':
        df = df[df.post_text_pred==label]
    else:
        df = df[df.group==group]
        df = df[df.post_text_pred==label]
    try:
        df = df[df.include==1]
        df = handletime(df)
        if freq=='minutes':

            df = df[df.time_elapsed_hours==0]
    except:
        return pd.DataFrame([], columns=[colname, 'sentiment_score', 'count'])

    df_agg = df.groupby([colname])[['sentiment','hashed_comment_id']] \
                           .agg(sentiment_score=('sentiment','mean'),
                                count = ('hashed_comment_id','count')
                                ).sort_values([colname]).reset_index()
    return df_agg


######### plotting functions ################
def sentiment_ts_plot(df=df,label='all',group='all', porc='comments', freq = 'day'):
    data = sentiment_ts_df(df, label,group, porc, freq)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    try:
        miny = min(data['sentiment_score'])
        miny = str(round(miny, 2))
        maxy = max(data['sentiment_score'])
        maxy = str(round(maxy, 2))
    except:
        miny = '0.0'
        maxy = '0.0'
    
    fig.add_trace(go.Scatter(
                                x=data['date'], y=data["sentiment_score"],
                                mode='lines',
                                hoverinfo='none',
                                name='line'
    ),
                         secondary_y=False
                         )
    fig.add_trace(go.Scatter(name='point',
                                 x=data['date'], 
                                 y=data["sentiment_score"],
                                 mode='markers',
                                 customdata = data['count'],
                                 hovertemplate =
                                '<b>Date</b>: %{x}<br>'+
                                '<b>Sentiment Score</b>: %{y}<br>'+
                                "<b>#comments: %{customdata}"+
                                '<extra></extra>',
                                 ),
                          secondary_y=True,
                         )
    fig.update_layout(
                title={
                    'text':'Sentiment score of '+porc+ ' under label - '+label+'<br>Ranges from '+str(miny)+' to '+str(maxy),
                   'y':0.9,
                   'x':0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'
                },
                xaxis={'title': "Date",

                      },

            )
    fig.update_yaxes(title_text="Mean Sentiment score", secondary_y=False)
    fig.update_layout(hovermode="x unified",showlegend=False)
    return fig



def sentiment_te_plot(df=df,label='tyrannical',group='all', freq='days'):
    data = sentiment_te_df(df, label,group, freq)
    colname = 'time_elapsed_'+freq
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    try:
        miny = min(data['sentiment_score'])
        miny = str(round(miny, 2))
        maxy = max(data['sentiment_score'])
        maxy = str(round(maxy, 2))
    except:
        miny = '0.0'
        maxy = '0.0'
    
    fig.add_trace(go.Scatter(
                                x=data[colname], y=data['sentiment_score'],
                                mode='lines',
                                hoverinfo='none',
                                name='line'),
                         secondary_y=False
                         )
    fig.add_trace(go.Scatter(name='point',
                                     x=data[colname], 
                                     y=data["sentiment_score"],
                                     mode='markers',
                                     customdata = data['count'],
                                     hovertemplate =
                                    '<b>Date</b>: %{x}<br>'+
                                    '<b>Sentiment Score</b>: %{y}<br>'+
                                    "<b>#comments: %{customdata}"+
                                    '<extra></extra>',
                                     ),
                              secondary_y=True,
                             )
    fig.update_layout(
                title={
                    'text':'Sentiment score of comments under posts with label - '+label+'<br>Ranges from '+str(miny)+' to '+str(maxy),
                   'y':0.9,
                   'x':0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'
                },
                xaxis={'title': "Time elapsed in "+ freq,

                      },

            )
    fig.update_yaxes(title_text="Mean Sentiment score", secondary_y=False)
    fig.update_layout(hovermode="x unified",showlegend=False)
    return fig


######### layout ##########

sentiment_ts_tab_card = dcc.Loading(id = "loading-sentiment-ts",
children=[
    dbc.Card(
        dbc.CardBody(
            [dbc.Row([
                dbc.Col(
                        [
                            html.Div("Text Type"),
                            dcc.Dropdown(
                                id='porc-dropdown', placeholder="Comments", multi=False,
                                options=[
                                        {'label': 'Comments', 'value': 'comments'},
                                        {'label': 'Posts', 'value': 'posts'},
                                    ],
                                value='comments',
                            )
                        ] , width = 3, style = {"marginLeft" : "7%","marginRight" : "13%"}
                    ),

                dbc.Col(
                        [
                            html.Div("Aggregation level"),
                            dcc.Dropdown(
                                id='agg-dropdown', placeholder="By Day", multi=False,
                                options=[
                                        {'label': 'By Month', 'value': 'month'},
                                        {'label': 'By Day', 'value': 'day'},
                                    ],
                                value='day',
                            )
                        ], width = 3, style = {"marginLeft" : "7%","marginRight" : "13%"}
                    ),
            ]),
            dbc.Row(
                [
                    dbc.Col(
                            [
                                dcc.Graph(
                                id= "sentiment_ts_fig",
                                figure= sentiment_ts_plot(),
                                )
                            ]#, width = 12
                        )
                ]
            ),
            html.Div("*Sentiment score equals to -1 indicates the most negative sentiment while 1 indicates the most positive sentiment.", style={'textAlign':'center'})
            ]
        ),
        #className="mt-3",
        #style= {"marginLeft": "10%",  "width": "80%"}
    )])


sentiment_te_tab_card = dcc.Loading(id = "loading-sentiment-te",
children=[dbc.Card(
    dbc.CardBody(
        [dbc.Row([
            dbc.Col(
                    [
                        html.Div("Frequency"),
                        dcc.Dropdown(
                            id='sentiment-freq-dropdown', placeholder="Days", multi=False,
                            options=[
                                    {'label': 'Days', 'value': 'days'},
                                    {'label': 'Hours', 'value': 'hours'},
                                    {'label': 'Minutes', 'value': 'minutes'},
                                ],
                            value='days',
                        )
                    ], width = 3, style = {"marginLeft" : "7%","marginRight" : "13%"}
                ),
        ]),
        dbc.Row(
            [
                dbc.Col(
                        [
                            dcc.Graph(
                            id= "sentiment_te_fig",
                            figure= sentiment_te_plot(),
                            )
                        ]#, width = 12
                    )
            ]
        )
        ]
    ),
    #className="mt-3",
    #style= {"marginLeft": "10%",  "width": "80%"}
)])

sentiment_tabs = dcc.Tabs([
    dcc.Tab(label='Time Series plot', children=[
            sentiment_ts_tab_card
        ]),
    dcc.Tab(label='Time Elapsed plot', children=[
            sentiment_te_tab_card
        ]),
    ]  
)



layout = html.Div([
            html.Div (html.Div([sentiment_tabs],style={"width":"100%"}))
        ], 
        #className="border", style={"display": "flex","justify-content": "center","align-items": "center", "height":"500px"}
        )


############ callbacks ###############
# label update 2 graphs
@app.callback(
    Output('sentiment_ts_fig', 'figure'),
    [Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    Input('porc-dropdown', 'value'),
    Input('agg-dropdown', 'value'),
    ])
def update_sentiment_ts_fig(label,group, porc, freq):
    if porc==None:
        porc='comments'
    if freq==None:
        freq='day'
    # print(label)
    plot = sentiment_ts_plot(label=label, group=group, porc = porc, freq=freq)
    return plot

@app.callback(
    Output('sentiment_te_fig', 'figure'),
    [Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    Input('sentiment-freq-dropdown', 'value'),
    ])
def update_sentiment_te_fig(label,group, freq):
    if freq==None:
        freq='days'
    plot = sentiment_te_plot(label=label,group=group, freq=freq)
    return plot

# Importing modules
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn', this is to suppress false positive warnings in the filtertime function.
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

def datepickervariables(df, label,group):
    df['post_time'] = pd.to_datetime(df['post_time'])
    df['comment_time'] = pd.to_datetime(df['comment_time'])
    
    df['comment_date'] = df['comment_time'].apply(lambda x: x.date())
    df = df[~df.comment_date.isnull()]
    df1 = df.copy()

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
        earliest = min(df['comment_date'])
        latest = max(df['comment_date'])
    except:
        earliest = min(df1['comment_date'])
        latest = max(df1['comment_date'])
#     earliest_arr = (earliest.year, earliest.month, earliest.day)
#     latest_arr = (latest.year, latest.month, latest.day)
    return (df, earliest, latest)


def filtertime(df, start_date, end_date, label,group):
    df = datepickervariables(df, label,group)[0]
    df['time_elapsed'] = pd.to_timedelta(df['time_elapsed'])
    
    df['time_elapsed_days'] = df.time_elapsed.apply(lambda x: x.days)
    df['time_elapsed_hours'] = df.time_elapsed.apply(lambda x:x.days*24 + x.seconds//3600)
    df['time_elapsed_minutes'] = df.time_elapsed.apply(lambda x:x.seconds//60)
    # df['timestamp'] = df.comment_time.astype('int64') // 10**6
    
    timestamp_start = pd.Timestamp(start_date)#.value/10**6
    # print('start: ')
    # print(timestamp_start)
#     timestamp_stop = (pd.to_datetime(end_date)+pd.DateOffset(1)).value/10**6
    timestamp_stop = pd.Timestamp(end_date)
    # print(timestamp_stop)
    try:
        df = df[(df['comment_date']>=timestamp_start)
            &(df['comment_date']<=timestamp_stop)]
        return df
    except:
        return None


    
# individualpost should be changed to 6 options (-1, 0 to 4)
def contagion_te_df(df,label,group, start_date, end_date, freq, individualpost):
    # df = df[df.post_text_pred==label]
    df = filtertime(df, start_date, end_date, label,group)
    
    
    if freq == 'days':
        colname = 'time_elapsed_days'
    elif freq == 'hours':
        colname = 'time_elapsed_hours'
    elif freq == 'minutes':
#         df = df[df.time_elapsed_hours==0]
        colname = 'time_elapsed_minutes'

    if df.empty:
        return pd.DataFrame([], columns=[colname, 'cumsum', 'percentile'])
        
    # for individual post
    df_agg = df.groupby(['hashed_post_id','post_text', colname])[['hashed_comment_id']] \
                           .agg(num_comments=('hashed_comment_id','count'),
                                ).sort_values([colname]).reset_index()
    df_agg['cumsum'] = df_agg.groupby(['hashed_post_id'])['num_comments'].cumsum(axis=0)
    
    
    top_5 = df_agg.groupby(['hashed_post_id'])[['num_comments']]\
                                 .agg(num_comments=('num_comments','sum'))\
                                 .sort_values(by=['num_comments'], ascending=False)\
                                 .reset_index()[:5]
    top_5_post_ids = list(top_5.hashed_post_id.values)

    # individualpost = int(individualpost)
    if individualpost==-1:
        # for all posts
        totalcount = sum(df_agg['num_comments'])
        if freq=='minutes':
            df_agg = df_agg[df_agg.time_elapsed_minutes<=60]
        df_agg_all = df_agg.groupby([colname])[['num_comments']] \
                               .agg(num_comments=('num_comments','sum'),
                                    ).sort_values([colname]).reset_index()
        df_agg_all['cumsum'] = df_agg_all['num_comments'].cumsum(axis=0)
        #print(totalcount)
        df_agg_all['percentile'] = df_agg_all['cumsum']/totalcount *100
        return df_agg_all
        
    else:
        try:
            postid = top_5_post_ids[individualpost]
        except IndexError:
            tempdf = pd.DataFrame([], columns=[colname, 'cumsum', 'percentile'])
            return tempdf
        tempdf = df_agg[df_agg.hashed_post_id==postid].reset_index()
        totalcount = sum(tempdf.num_comments)
        tempdf['percentile'] = tempdf['cumsum']/totalcount *100
        if freq=='minutes':
            tempdf = tempdf[tempdf.time_elapsed_minutes<=60]
        return tempdf
        


def contagion_ts_df(df,label,group, start_date, end_date):
    # if label == 'all':
    #     df = df
    # else:
    #     df = df[df.post_text_pred==label]
    df = filtertime(df, start_date, end_date, label,group)
    if df.empty:
        return pd.DataFrame([], columns=['comment_date', 'cumsum', 'percentile'])
    
    df_agg = df.groupby(['hashed_post_id','post_text', 'comment_date'])[['hashed_comment_id']] \
                           .agg(num_comments=('hashed_comment_id','count'),
                                ).sort_values(['comment_date']).reset_index()
    df_agg['cumsum'] = df_agg.groupby(['hashed_post_id'])['num_comments'].cumsum(axis=0)
    
    totalcount = sum(df_agg['num_comments'])
    
    df_agg_all = df_agg.groupby(['comment_date'])[['num_comments']] \
                               .agg(num_comments=('num_comments','sum'),
                                    ).sort_values(['comment_date']).reset_index()
    df_agg_all['cumsum'] = df_agg_all['num_comments'].cumsum(axis=0)
    #print(totalcount)
    df_agg_all['percentile'] = df_agg_all['cumsum']/totalcount *100
    return df_agg_all


def contagion_te_df_all(df,group, start_date, end_date, freq):
    dfdict = {}

    df = filtertime(df, start_date, end_date, label='all', group=group)
    
    
    if freq == 'days':
        colname = 'time_elapsed_days'
    elif freq == 'hours':
        colname = 'time_elapsed_hours'
    elif freq == 'minutes':
        df = df[df.time_elapsed_hours==0]
        colname = 'time_elapsed_minutes'

    if df.empty:
        return {'':pd.DataFrame([], columns=[colname, 'cumsum', 'percentile'])}
        
    dfall = df.groupby(['hashed_post_id','post_text', colname])[['hashed_comment_id']] \
                           .agg(num_comments=('hashed_comment_id','count'),
                                ).sort_values([colname]).reset_index()
    dfall = dfall.groupby([colname])[['num_comments']] \
                               .agg(num_comments=('num_comments','sum'),
                                    ).sort_values([colname]).reset_index()
    dfall['cumsum'] = dfall['num_comments'].cumsum(axis=0)
    dfdict['all'] = dfall
    
    labellist = list(df.post_text_pred.unique())
    for label in labellist:
        tempdf = df[df.post_text_pred==label]
        tempdf = tempdf.groupby(['hashed_post_id','post_text', colname])[['hashed_comment_id']] \
                           .agg(num_comments=('hashed_comment_id','count'),
                                ).sort_values([colname]).reset_index()
        tempdf = tempdf.groupby([colname])[['num_comments']] \
                                   .agg(num_comments=('num_comments','sum'),
                                        ).sort_values([colname]).reset_index()
        tempdf['cumsum'] = tempdf['num_comments'].cumsum(axis=0)
        dfdict[label] = tempdf
        
    return dfdict


############ plotting functions ###############
def contagion_te_plot(df=df, label='all',group='all', start_date='2018-01-03', end_date='2021-05-31', freq='days', individualpost=-1):
    colname = 'time_elapsed_'+freq
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    coltoplot = 'cumsum'
    
    if label=='all':
        individualpost=False
        data = contagion_te_df_all(df,group, start_date, end_date, freq)
        
        for label in data.keys():
            df = data[label]
            if len(df)==1:
                fig.add_trace(go.Scatter(name=label, 
                                         x=df[colname], y=df[coltoplot],
                                         mode='markers',
                                         hovertemplate =
                                        '<b>Time elapsed</b>: %{x}<br>'+
                                        '<b># Comments</b>: %{y}<br>'+
                                        '<extra></extra>',
                                         ),
                                  secondary_y=False,
                                 )
            else:
                fig.add_trace(go.Scatter(
                                    x=df[colname], y=df[coltoplot],
                                    mode='lines',
                                    hovertemplate =
                                            '<b>Time elapsed</b>: %{x}<br>'+
                                            '<b># Comments</b>: %{y}<br>'+
                                            '<extra></extra>',
                                    name=label),
                             secondary_y=False
                             )

        label='all'
        
    else:
        data = contagion_te_df(df, label, group, start_date, end_date, freq, individualpost)
        fig.add_trace(go.Scatter(
                            x=data[colname], y=data[coltoplot],
                            mode='lines',
                            hoverinfo='none',
                            name='line'),
                     secondary_y=False
                     )
        fig.add_trace(go.Scatter(name='point', 
                                     x=data[colname], 
                                     y=data[coltoplot],
                                     customdata = data['percentile'],
                                     mode='markers',
                                     hovertemplate =
                                    '<b>Time elapsed</b>: %{x}<br>'+
                                    '<b># Comments</b>: %{y}<br>'+
                                    '<b>% Comments</b>: %{customdata:.3f}<br>'+
                                    '<extra></extra>',
                                     ),
                              secondary_y=True,
                             )
    fig.update_layout(
                title={
                    'text': 'Number of comments under posts with label - '+label,
                   'y':0.9,
                   'x':0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'
                },
                xaxis={'title': "Time elapsed in "+ freq,

                      },

            )
    fig.update_yaxes(title_text="Total number of comments", secondary_y=False)
    # fig.update_yaxes(title_text="%(comments)", secondary_y=True)
    fig.update_layout(hovermode="x unified")
    return fig


def contagion_ts_plot(df=df, label='all',group='all', start_date='2018-01-03', end_date='2021-05-31'):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    coltoplot = 'cumsum'
    data = contagion_ts_df(df,label,group, start_date, end_date)
    
    fig.add_trace(go.Scatter(
                            x=data['comment_date'], y=data[coltoplot],
                            mode='lines',
                            hoverinfo='none',
                            name='line'),
                     secondary_y=False
                     )
    fig.add_trace(go.Scatter(name='point', 
                                 x=data['comment_date'], 
                                 y=data[coltoplot],
                                 customdata = data['percentile'],
                                 mode='markers',
                                 hovertemplate =
                                '<b>Date</b>: %{x}<br>'+
                                '<b># Comments</b>: %{y}<br>'+
                                '<b>% Comments</b>: %{customdata:.3f}<br>'+
                                '<extra></extra>',
                                 ),
                          secondary_y=True,
                         )
    fig.update_layout(
                title={
                    'text': 'Number of comments under posts with label - '+label,
                   'y':0.9,
                   'x':0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'
                },
                xaxis={'title': "Date",

                      },

            )
    fig.update_yaxes(title_text="Total number of comments", secondary_y=False)
#     fig.update_yaxes(title_text="%(comments)", secondary_y=True)
    fig.update_layout(hovermode="x unified",showlegend=False)
    return fig



########## layout ##############
ecdf_ts_tab_card = dcc.Loading(id = "loading-ecdf-ts",
    children=[
        dbc.Card(
        dbc.CardBody(
            [
            dbc.Row(
                [
                    dbc.Col(
                            [
                                dcc.Graph(
                                id= "contagion_ts_fig",
                                figure= contagion_ts_plot(),
                                )
                            ] #, width = 12
                        )
                ]
            )
            ]
        ),
        # className="mt-3",
        #style= {"marginLeft": "10%",  "width": "80%"}
)])

posttexttable = html.Div(id="toggle_post", children=[dash_table.DataTable(
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            id='post_texts',
                            columns=[{"name": "Post Text", "id": "post_text"},],
                            data=[{}],
                            style_table={'height': '150px', 'overflowY': 'auto'},
                            style_cell={
                                'text_align': 'left',
                                'max-width': '400px',
                                'min-width': '400px',
                                'width': '400px',
                                'font_family': '"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
                            },
                            fill_width = True, # cannot change this
                        )], style={'display': 'none'})


ecdf_te_tab_card = dcc.Loading(id = "loading-ecdf-te",
    children=[
    dbc.Card(
        dbc.CardBody(
            [dbc.Row([

                dbc.Col(
                        [
                            html.Div("Display comments under posts"),
                            dcc.Dropdown(
                                id='contagion-post-dropdown', placeholder="All", multi=False,
                                options=[
                                        {'label': 'All', 'value': -1},
                                        {'label': 'Top 1', 'value': 0},
                                        {'label': 'Top 2', 'value': 1},
                                        {'label': 'Top 3', 'value': 2},
                                        {'label': 'Top 4', 'value': 3},
                                        {'label': 'Top 5', 'value': 4},
                                    ],
                                value=-1,
                                clearable=False
                            )
                        ] #, width = 3, style = {"marginLeft" : "7%","marginRight" : "13%"}
                        , width="auto"
                    ),
                
                    dbc.Col(
                        [
                            html.Div("Frequency"),
                            dcc.Dropdown(
                                id='contagion-freq-dropdown', placeholder="Days", multi=False,
                                options=[
                                        {'label': 'Days', 'value': 'days'},
                                        {'label': 'Hours', 'value': 'hours'},
                                        {'label': 'Minutes', 'value': 'minutes'},
                                    ],
                                value='days',
                                clearable=False
                            )
                        ]#, width = 3, style = {"marginLeft" : "7%","marginRight" : "13%"}
                        , width=2
                    )
            ]),
            dbc.Row(
                [
                    dbc.Col(
                            [
                                dcc.Graph(
                                id= "contagion_te_fig",
                                figure= contagion_te_plot(),
                                )
                            ] #, width = 12
                        )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                            [
                                html.Div(posttexttable)
                            ] , width={"size": 8, "offset": 2},
                        )
                ]
            ),
            ]
        ),
        # className="mt-3",
        #style= {"marginLeft": "10%",  "width": "80%"}
)])

contagion_tabs = dcc.Tabs([
    dcc.Tab(label='Time Series plot', children=[
            ecdf_ts_tab_card
        ]),
    dcc.Tab(label='Time Elapsed plot', children=[
            ecdf_te_tab_card
        ]),
    ]  
)

dates = datepickervariables(df,'all','all')

layout = html.Div(
    [
        dbc.Row([
            dbc.Col( dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dates[1],
                max_date_allowed=dates[2],
                start_date=dates[1],
                end_date=dates[2],
                display_format='DD MMM YYYY',
                with_portal= True
            )),
        ]),
        html.Div([html.P()]),
        dbc.Row(
            [html.Div([contagion_tabs],style={"width":"100%"})]
        )
    ],
    style= {"marginLeft": "10%",  "width": "80%"}
)

# layout = html.Div([
#             "ECDF Graph"
#         ], className="border", style={"display": "flex","justify-content": "center","align-items": "center", "height":"500px"})

############## callbacks ##############
# label update datepicker start and end
@app.callback(
    [Output('my-date-picker-range', 'start_date'),
    Output('my-date-picker-range', 'end_date'),],
    [
    Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    ])
def update_datepicker(label,group):
    
    dates = datepickervariables(df,label,group)
    return dates[1], dates[2]

# update te graph
@app.callback(
    Output('contagion_te_fig', 'figure'),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    Input('contagion-post-dropdown', 'value'),
    Input('contagion-freq-dropdown', 'value'),
    ])
def update_contagion_te_fig(start_date, end_date,label,group, individual, freq):
    if freq==None:
        freq='days'
    plot = contagion_te_plot(start_date=start_date, end_date=end_date, label = label,group=group, freq=freq, individualpost=individual)
    return plot

# update ts graph
@app.callback(
    Output('contagion_ts_fig', 'figure'),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    ])
def update_contagion_ts_fig(start_date, end_date,label,group):
    
    plot = contagion_ts_plot(start_date=start_date, end_date=end_date, label = label,group=group)
    return plot

@app.callback(
    [Output('post_texts', 'data'),
     Output('toggle_post', 'style')],
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    Input('contagion-post-dropdown', 'value'),
    Input('contagion-freq-dropdown', 'value'),
    ])
def update_posttext_fig(start_date, end_date,label,group, individual, freq):
    if freq==None:
        freq='days'
    if individual!= None:
        if individual >=0:
            # print(freq)
            tempdf = contagion_te_df(df = df, label= label,group=group, start_date=start_date,end_date=end_date,freq=freq,individualpost=individual)
            if len(tempdf)==0:
                return [{'post_text': 'No datapoint for the post selected.'}], {'display': 'block'}
            else:
                tempdf.reset_index(inplace=True)
                text = tempdf[['post_text']][:1]
                res = text.to_dict('records')
                # print(res)
                return res, {'display': 'block'}

    return [{}], {'display': 'none'}
# Importing modules
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from pandas import Timestamp

import plotly.express as px
import plotly.graph_objs as go

from app import app
HEADER_FONT_SIZE = 20
BODY_FONT_SIZE = 25

#Read in the processed data with post_dates set prior to the earliest comment_date
data = pd.read_csv('outputs/data/time_elapsed.csv',encoding="utf-8")
data['post_time'] = pd.to_datetime(data['post_time'])
data['comment_time'] = pd.to_datetime(data['comment_time'])
data['time_elapsed'] = pd.to_timedelta(data['time_elapsed'])

all_labels = ['all']
all_labels = data['post_text_pred'].unique()
#Sort in descending order
all_labels[::-1].sort()
all_labels = np.append(['all'], all_labels)

layout = html.Div([
            html.Div([
                dcc.Dropdown(
                        id='filter_time',
                        options=[{'label': 'Peak Hour', 'value': 'Hourly'},{'label': 'Peak Day', 'value': 'Daily'},
                                    {'label': 'Peak Month', 'value': 'Monthly'}],
                        placeholder="Peak Time Period",
                        style={'width': '100%'}
                    )
                    ], style={'width':'15%', 'padding-bottom':10,
                                'display':'flex','align-items':'left',
                                'text-align':'left', 'padding-left':10}),
            dbc.Row([
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
                    dbc.CardHeader("Likes (Median)",  style={'font-size':HEADER_FONT_SIZE}),
                    dbc.CardBody(
                        [html.H1(id = 'numLikes',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                            html.P(id = 'avgLikes',className="card-text"
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
                    dbc.CardHeader("Peak Hour", id = 'peakTitle',  style={'font-size':HEADER_FONT_SIZE}),
                    
                    dbc.CardBody(
                        [
                            html.H1(id = 'peakHour',className="lead",  style={'font-size':BODY_FONT_SIZE}),
                            html.P(id = 'peakHourAvg',className="card-text"
                            )
                        ])
                    ], className="card border-dark mb-3")
                ])
            ])], style={'text-align':'center', 'padding-bottom':10, 'padding-left':10, 'padding-right':10})

#Update card data
@app.callback(
Output("numPosts", "children"),
Output("avgPostLen", "children"),
Output("numLikes", "children"),
Output("avgLikes", "children"),
Output("numComments", "children"),
Output("avgCommentLen", "children"),
Output("numUsers", "children"),
Output("userDescription", "children"),
Output("peakTitle", "children"),
Output("peakHour", "children"),
Output("peakHourAvg", "children"),
Output("avgPostLen", "style"),
Output("avgCommentLen", "style"),
Input('selected_label', 'value'),
Input('filter_time', 'value'))

def helper(label, time_period):
    #Prepare post data
    posts = data.loc[data.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True).copy()
    posts = posts.dropna(subset=['post_text'])
    #Prepare comments data
    comments = data[data['hashed_comment_id'] != '0'].copy()
    #Filter by label
    if label and (label != 'all'):
        posts = posts[posts['post_text_pred'] == label]
        comments = comments[comments['comment_text_pred'] == label]
    post_lengths = posts['post_text'].str.split("\\s+")
    #Number of posts
    num_posts = f'{posts["hashed_post_id"].nunique():,}'
    #Average length of each post
    avg_post_length = round(post_lengths.str.len().median())

    #Sentiment score of each post
    #post_score = posts[posts["post_sentiment"] != 0]['post_sentiment']

    post_filtered = posts[posts['include'] == 1]['sentiment']
    post_sentiment = round(post_filtered.mean(), 2)
    #Fix floating point issue where negative numbers are rounded to -0
    if post_sentiment == 0:
        post_sentiment = 0
    post_length_text = f'Length: {avg_post_length:,} words, Sentiment: {post_sentiment:.2f}'

    
    #Number of comments
    num_comments = f'{len(comments):,}'
    #Average length of each comment
    avg_comment_length = round(comments['comment_text'].str.len().median())
    #Sentiment score of each comment
    #comment_score = comments[comments["comment_sentiment"] != 0]['comment_sentiment']

    #Experiment with filtering by word length
    comment_filtered = comments[comments['include'] == 1]['sentiment']
    comment_sentiment = round(comment_filtered.mean(), 2)
    #Fix floating point issue where negative numbers are rounded to -0
    if comment_sentiment == 0:
        comment_sentiment = 0
    comment_length_text = f'Length: {avg_comment_length:,} words, Sentiment: {comment_sentiment:.2f}'

    #Number of people who made posts
    posters = posts['hashed_username']
    commenters = comments['hashed_commenter_name']
    all_users = f'{pd.Series(np.concatenate((posters, commenters))).nunique():,}'
    user_description = f'{commenters.nunique():,} Commenters, {posters.nunique():,} Posters'

    #Filter by chosen peak time period
    #Filter by label
    cardTitle = 'Peak Hour'
    period = 'hour'
    if time_period:
        if time_period == 'Daily':
            #Peak weekday
            period = 'weekday'
            comments['weekday'] = comments['comment_time'].apply(lambda x:x.strftime("%A"))
            #Get total number of comments made each weekday
            agg_freq = comments[['hashed_comment_id', 'weekday']].groupby(['weekday']).size()
            #Find how many unique occurrences of each weekday 
            comments['full_date'] = comments['comment_time'].apply(lambda x:Timestamp(x.year, x.month, x.day))
            num_periods = comments[['full_date', 'weekday']].groupby(['weekday']).nunique()
            cardTitle = 'Peak Day'
        elif time_period == 'Monthly':
            #Peak month
            period = 'month'
            #Extract the month from comment_time
            comments['month'] = comments['comment_time'].apply(lambda x:x.strftime("%B"))
            #Get total number of comments made each month
            agg_freq = comments[['hashed_comment_id', 'month']].groupby(['month']).size()
            #Find how many unique occurrences of each month, after combining it with year
            comments['month_year'] = comments['comment_time'].apply(lambda x:Timestamp(x.year, x.month, 1))
            num_periods = comments[['month', 'month_year']].groupby(['month']).nunique()
            cardTitle = 'Peak Month'
    if period == 'hour':
        #Peak hour
        comments['hour'] = comments['comment_time'].apply(lambda x:x.strftime('%H'))
        #Get total number of comments made each hour
        agg_freq  = comments[['hashed_comment_id', 'hour']].groupby(['hour']).size()
        #Find how many unique occurrences of each hour
        comments['datehour'] = comments['comment_time'].apply(lambda x:Timestamp(x.year, x.month, x.day, x.hour))
        num_periods = comments[['datehour', 'hour']].groupby(['hour']).nunique()

    #Find which period has the highest average number of comments
    highest = {'period':'', 'val':0}
    for periods in num_periods.index:
        ave_freq = int(agg_freq.loc[periods]/num_periods.loc[periods].values[0])
        if ave_freq >= highest['val']:
            highest['period'] = periods
            highest['val'] = ave_freq
    if period == 'hour':
        peak_period = format_time(highest['period'])
    else:
        peak_period = highest['period']
    periodic_text = f'Comment Frequency: {highest["val"]}'

    #Adjust text color based on sentiment
    post_color = {}
    comment_color = {}
    if round(post_filtered.mean(), 2) > 0:
        post_color = {'color':'green'}
    elif round(post_filtered.mean(), 2) < 0:
        post_color = {'color':'red'}
    if round(comment_filtered.mean(), 2) > 0:
        comment_color = {'color':'green'}
    elif round(comment_filtered.mean(), 2) < 0:
        comment_color = {'color':'red'}

    #Average number of likes
    num_likes = posts['likes'].median()
    posts_with_likes = round(((len(posts[posts['likes'] > 0])*100)/len(posts)), 2)
    likes_text = f'Posts with >0 likes: {posts_with_likes}%'

    return [num_posts, post_length_text, num_likes, likes_text, num_comments,
                comment_length_text, all_users, user_description, cardTitle,
                 peak_period, periodic_text, post_color, comment_color]

def format_time(time):
    time = int(time)
    if time == 0:
        return '12 AM'
    elif time < 12:
        return f'{time} AM'
    elif time == 12:
        return '12 PM'
    else:
        return f'{time%12} PM'
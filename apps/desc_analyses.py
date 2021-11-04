# Importing modules
import pandas as pd
import numpy as np
from pandas import Timestamp

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

from app import app
HEADER_FONT_SIZE = 20
BODY_FONT_SIZE = 25
FOOTER_FONT_SIZE = 19

# Read in the processed data with post_dates set prior to the earliest comment_date
data = pd.read_csv('outputs/time_series_graphs/time_elapsed_filtered.csv', encoding="utf-8")
data['post_time'] = pd.to_datetime(data['post_time'])
data['comment_time'] = pd.to_datetime(data['comment_time'])
data['time_elapsed'] = pd.to_timedelta(data['time_elapsed'])

layout = html.Div([
    dcc.Loading(
    html.Div([
    dbc.Row([
        dbc.Col([
            html.Div(children=[
                "Posts"], className="lead card-header", style={'font-size': HEADER_FONT_SIZE}),
            html.Div([
                html.H1(id='numPosts', className="lead",  style={'font-size': BODY_FONT_SIZE}),
                html.P(id='avgPostLen', className="card-text",  style={'font-size': FOOTER_FONT_SIZE})
            ], className="card-body flex-fill")
        ], className="card border-dark mb-3", style={"padding": 0}),
        dbc.Col([
            html.Div(children=[
                "Comments"], className="lead card-header", style={'font-size': HEADER_FONT_SIZE}),
            html.Div([
                html.H1(id='numComments', className="lead",  style={'font-size': BODY_FONT_SIZE}),
                html.P(id='avgCommentLen', className="card-text",  style={'font-size': FOOTER_FONT_SIZE})
            ], className="card-body flex-fill")
        ], className="card border-dark mb-3", style={"padding": 0}),
        dbc.Col([
            html.Div(children=[
                "Total Users"], className="lead card-header", style={'font-size': HEADER_FONT_SIZE}),
            html.Div([
                html.H1(id='numUsers', className="lead",  style={'font-size': BODY_FONT_SIZE}),
                html.P(id='userDescription', className="card-text",  style={'font-size': FOOTER_FONT_SIZE})
            ], className="card-body flex-fill")
        ], className="card border-dark mb-3", style={"padding": 0}),
        dbc.Col([
            html.Div(children=[
                dcc.Dropdown(
                    id='filter_likes',
                    options=[{'label': 'Post Likes (Median)', 'value': 'Likes (Median)'}, {'label': 'Post Likes (Mode)', 'value': 'Likes (Mode)'},
                             {'label': 'Post Likes (Mean)', 'value': 'Likes (Mean)'}],
                    value='Likes (Median)',
                    clearable=False,
                    style={'width': '100%'}
                )], className="lead card-header", style={'font-size': HEADER_FONT_SIZE}),
            html.Div([
                html.H1(id='numLikes', className="lead",  style={'font-size': BODY_FONT_SIZE}),
                html.P(id='avgLikes', className="card-text",  style={'font-size': FOOTER_FONT_SIZE})
            ], className="card-body flex-fill")
        ], className="card border-dark mb-3", style={"padding": 0}),
        dbc.Col([
            html.Div(children=[
                dcc.Dropdown(
                    id='filter_time',
                    options=[{'label': 'Peak Hour', 'value': 'Hourly'}, {'label': 'Peak Day', 'value': 'Daily'},
                             {'label': 'Peak Month', 'value': 'Monthly'}],
                    value='Hourly',
                    clearable=False,
                    style={'width': '100%'}
                )
            ], className="lead card-header", style={'font-size': HEADER_FONT_SIZE}),
            html.Div([
                html.H1(id='peakHour', className="lead",  style={'font-size': BODY_FONT_SIZE}),
                html.P(id='peakHourAvg', className="card-text",  style={'font-size': FOOTER_FONT_SIZE})
            ], className="card-body flex-fill")
        ], className="card border-dark mb-3", style={"padding": 0})
    ])], style={'text-align': 'center', 'padding-bottom': 10, 'padding-left': 10, 'padding-right': 10}))])

# Update card data


@app.callback(
    Output("numPosts", "children"),
    Output("avgPostLen", "children"),
    Output("numLikes", "children"),
    Output("avgLikes", "children"),
    Output("numComments", "children"),
    Output("avgCommentLen", "children"),
    Output("numUsers", "children"),
    Output("userDescription", "children"),
    Output("peakHour", "children"),
    Output("peakHourAvg", "children"),
    Output("avgPostLen", "style"),
    Output("avgCommentLen", "style"),
    Input('selected_label', 'value'),
    Input('selected_group', 'value'),
    Input('filter_time', 'value'),
    Input('filter_likes', 'value'))
def helper(label, group, time_period, filter_likes):
    # Prepare post data
    posts = data.loc[data.groupby('hashed_post_id')[
        'post_time'].idxmin()].reset_index(drop=True).copy()
    posts = posts.dropna(subset=['post_text'])
    # Prepare comments data
    comments = data[data['hashed_comment_id'] != '0'].copy()
    # Filter by label
    if label != 'all':
        posts = posts[posts['post_text_pred'] == label]
        comments = comments[comments['comment_text_pred'] == label]
    
    # Filter by group
    if group != 'all':
        posts = posts[posts['group'] == group]
        comments = comments[comments['group'] == group]

    post_lengths = posts['post_text'].str.split("\\s+")
    # Number of posts
    num_posts = f'{posts["hashed_post_id"].nunique():,}'
    # Average length of each post
    avg_post_length = post_lengths.str.len().median()
    if avg_post_length == avg_post_length:
        avg_post_length = round(avg_post_length)
    else:
        avg_post_length = 0
    # Sentiment score of each post

    post_filtered = posts[posts['include'] == 1]['sentiment']
    post_sentiment = round(post_filtered.mean(), 2)
    # Fix floating point issue where negative numbers are rounded to -0
    if post_sentiment == 0:
        post_sentiment = 0
    post_length_text = f'Length: {avg_post_length:,} words, Sentiment: {post_sentiment:.2f}'

    # Number of comments
    num_comments = f'{len(comments):,}'
    # Average length of each comment
    avg_comment_length = comments['comment_text'].str.len().median()
    if avg_comment_length == avg_comment_length:
        avg_comment_length = round(avg_comment_length)
    else:
        avg_comment_length = 0

    # Sentiment score of each comment

    # Experiment with filtering by word length
    comment_filtered = comments[comments['include'] == 1]['sentiment']
    comment_sentiment = round(comment_filtered.mean(), 2)
    # Fix floating point issue where negative numbers are rounded to -0
    if comment_sentiment == 0:
        comment_sentiment = 0
    comment_length_text = f'Length: {avg_comment_length:,} words, Sentiment: {comment_sentiment:.2f}'

    # Number of people who made posts
    posters = posts['hashed_username']
    commenters = comments['hashed_commenter_name']
    all_users = f'{pd.Series(np.concatenate((posters, commenters))).nunique():,}'
    user_description = f'{commenters.nunique():,} Commenters, {posters.nunique():,} Posters'

    # Filter by chosen peak time period
    # Filter by label
    period = 'hour'
    if time_period:
        if time_period == 'Daily':
            # Peak weekday
            period = 'weekday'
            comments['weekday'] = comments['comment_time'].apply(
                lambda x: x.strftime("%A"))
            # Get total number of comments made each weekday
            agg_freq = comments[['hashed_comment_id', 'weekday']].groupby([
                                                                          'weekday']).size()
            # Find how many unique occurrences of each weekday
            comments['full_date'] = comments['comment_time'].apply(
                lambda x: Timestamp(x.year, x.month, x.day))
            num_periods = comments[['full_date', 'weekday']].groupby(
                ['weekday']).nunique()
        elif time_period == 'Monthly':
            # Peak month
            period = 'month'
            # Extract the month from comment_time
            comments['month'] = comments['comment_time'].apply(
                lambda x: x.strftime("%B"))
            # Get total number of comments made each month
            agg_freq = comments[['hashed_comment_id', 'month']].groupby([
                                                                        'month']).size()
            # Find how many unique occurrences of each month, after combining it with year
            comments['month_year'] = comments['comment_time'].apply(
                lambda x: Timestamp(x.year, x.month, 1))
            num_periods = comments[['month', 'month_year']].groupby(
                ['month']).nunique()
    if period == 'hour':
        # Peak hour
        comments['hour'] = comments['comment_time'].apply(
            lambda x: x.strftime('%H'))
        # Get total number of comments made each hour
        agg_freq = comments[['hashed_comment_id', 'hour']].groupby([
                                                                   'hour']).size()
        # Find how many unique occurrences of each hour
        comments['datehour'] = comments['comment_time'].apply(
            lambda x: Timestamp(x.year, x.month, x.day, x.hour))
        num_periods = comments[['datehour', 'hour']
                               ].groupby(['hour']).nunique()

    # Find which period has the highest average number of comments
    highest = {'period': '', 'val': 0}
    for periods in num_periods.index:
        ave_freq = int(agg_freq.loc[periods] /
                       num_periods.loc[periods].values[0])
        if ave_freq >= highest['val']:
            highest['period'] = periods
            highest['val'] = ave_freq
    if period == 'hour':
        peak_period = format_time(highest['period'])
    else:
        peak_period = highest['period']
    periodic_text = f'Comment Frequency: {highest["val"]}'

    # Adjust text color based on sentiment
    post_color = {}
    comment_color = {}
    if round(post_filtered.mean(), 2) > 0:
        post_color = {'color': 'green'}
    elif round(post_filtered.mean(), 2) < 0:
        post_color = {'color': 'red'}
    if round(comment_filtered.mean(), 2) > 0:
        comment_color = {'color': 'green'}
    elif round(comment_filtered.mean(), 2) < 0:
        comment_color = {'color': 'red'}

    post_color['font-size']= FOOTER_FONT_SIZE
    comment_color['font-size'] = FOOTER_FONT_SIZE

    # Average number of likes
    if filter_likes == 'Likes (Median)':
        likes = posts['likes'].median()
    elif filter_likes == 'Likes (Mean)':
        likes = round(posts['likes'].mean(), 2)
    elif filter_likes == 'Likes (Mode)':
        if posts['likes'].mode().values == posts['likes'].mode().values:
            likes = posts['likes'].mode().values[0]
        else:
            likes = 0
    num_likes = f'{likes:,}'
    if len(posts) != 0:
        posts_with_likes = round(((len(posts[posts['likes'] > 0])*100)/len(posts)), 2)
    else:
        posts_with_likes = 0
    likes_text = f'Posts with >0 likes: {posts_with_likes}%'

    return [num_posts, post_length_text, num_likes, likes_text, num_comments,
            comment_length_text, all_users, user_description,
            peak_period, periodic_text, post_color, comment_color]


def format_time(time):
    if time != time:
        return "NAN"
    time = int(time)
    if time == 0:
        return '12 AM'
    elif time < 12:
        return f'{time} AM'
    elif time == 12:
        return '12 PM'
    else:
        return f'{time%12} PM'

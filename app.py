import json
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from pandas import Timestamp
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import ast
import datetime
import math
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'height':'200px'
    }
}

#Read in data
data = pd.read_csv('data/time_elapsed.csv',encoding="utf-8")
data['post_time'] = pd.to_datetime(data['post_time'])
data['comment_time'] = pd.to_datetime(data['comment_time'])
data['time_elapsed'] = pd.to_timedelta(data['time_elapsed'])
all_labels = data['post_text_pred'].unique()
#Sort in descending order
all_labels[::-1].sort()
all_labels = np.append(all_labels, 'All')

all_groups = ['All']
all_groups = np.append(all_groups, data['group'].unique())


#Import CSS styles
file = open('assets/styles.txt', "r")
contents = file.read()
graph_styles = ast.literal_eval(contents)
file.close()


app.layout = html.Div([
    #Cards
    html.Div([
        #First card
         html.Div([
            dbc.Card([
                dbc.CardHeader("Posts",  style={'font-size':30}),
                dbc.CardBody(
                    [html.H1("text", id = 'numPosts',className="lead",  style={'font-size':30}),
                        html.P("text",id = 'avgPostLen',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ], style = {'float':'left','width':'20%'}),
        #Second card
        html.Div([
            dbc.Card([
                dbc.CardHeader("Comments",  style={'font-size':30}),
                dbc.CardBody(
                    [html.H1("text", id = 'numComments',className="lead",  style={'font-size':30}),
                        html.P("text",id = 'avgCommentLen',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ], style = {'float':'left','width':'20%', 'padding-left':20}),
        #Third card
        html.Div([
            dbc.Card([
                dbc.CardHeader("Total Users",  style={'font-size':30}),
                dbc.CardBody(
                    [html.H1("text", id = 'numUsers',className="lead",  style={'font-size':30}),
                        html.P("text",id = 'userDescription',className="card-text"
                        )
                    ])
                ], className="card border-dark mb-3")
            ], style = {'float':'left','width':'20%', 'padding-left':20}),
        ], style={'text-align':'center', 'padding-bottom':250}),
    #2nd row in dashboard
    html.Div([
        #Placeholder for another graph
        #html.Div([dcc.Graph(id = 'daily_time_series')], style={'display':'inline-block','float':'left', 'width':'47%'}),
        
        #Time series graph on post/comment frequency
        html.Div([
            html.Div([
                dcc.Markdown('Aggregation Period'),
                dcc.Dropdown(
                    id='Aggregation Period',
                    options=[{'label': 'Yearly', 'value': 'Yearly'},{'label': 'Monthly', 'value': 'Monthly'},
                            {'label': 'Daily', 'value': 'Daily'}],
                    value='Yearly'
                )], style={'width':'30%', 'padding-left':50, 'display':'inline-block'}),

            html.Div([
                dcc.Markdown('Content Type'),
                dcc.Dropdown(
                    id='Content Type',
                    options=[{'label': 'All', 'value': 'All'}, {'label': 'Posts', 'value': 'Posts'},{'label': 'Comments', 'value': 'Comments'}],
                    value='All'
                )], style={'width':'30%', 'padding-left':50, 'display':'inline-block'}),

                
            dcc.Graph(id = 'monthly_time_series')], style={'display':'inline-block', 'width':'47%'})]),
    #Post-centric Network Graph
    html.Div([
        html.Div([dcc.Markdown("**Post-centric Network Graph**",style={'color': 'black', 'fontSize': 25,'text-align': 'center'})]),
        html.Div([
            dcc.Markdown('Filter by Class'),
            dcc.Dropdown(
                id='filter_labels',
                options=[{'label': i, 'value': i} for i in all_labels],
                value=all_labels[1]
            )], style={'display':'inline-block', 'width':'15%'}),
        html.Div([
            dcc.Markdown('Filter by Group'),
            dcc.Dropdown(
                id='filter_group',
                options=[{'label': i, 'value': i} for i in all_groups],
                value=all_groups[0]
            )], style={'display':'inline-block', 'width':'15%', 'padding-left':30}),
        html.Div([
            dcc.Markdown('Top **N** Posts by Reaction Count'),
            dcc.Dropdown(
                id='top_n_clusters',
                options=[{'label': i, 'value': i} for i in range(1, 10)],
                value=1
                )], style={'display':'inline-block', 'width':'15%', 'padding-left':30}),
        html.Div([
            dcc.Markdown('Search for a Post'),
            dcc.Input(
            id = "search_box",
            type = "text",
            placeholder = "Input search term",
            debounce=True,
            )],style={'display':'inline-block', 'width':'20%',  'float':'right'})]),
    
        cyto.Cytoscape(
            id='cytoscape-graph',
            style={'width': '100%', 'height': '500px'},
            layout={'name': 'cose','animate':True, 'fit':True
                    , 'numIter':75, 'gravity': 100, 'nodeRepulsion': 500000000, 
                    'boundingBox':{'x1':0, 'x2':7000, 'y1':0, 'y2':5000}},
            responsive = True,
            maxZoom = 0.2,
            minZoom = 0.08,
            stylesheet=graph_styles
        ),
        html.Div([
            dcc.Markdown("**Time Elapsed (Click on post node to filter)**",
                style={'color': 'black', 'fontSize': 15,
                        'text-align': 'center', 'float':'middle'}),
            dcc.Slider(
                id = 'time_slider'
        )],style={'width':'100%', 'float':'middle'}),
        html.Pre(id='cytoscape-tapNodeData-json', style=styles['pre'])
], style={'width': '100%', 'float':'middle'})

#TIME SERIES GRAPH
@app.callback(
    Output('monthly_time_series', 'figure'),
    Input('Aggregation Period', 'value'),
    Input('Content Type', 'value'))

def update_time_series(time_frame, content_type):
    post = data.loc[data.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True)[['post_time', 'post_text_pred']]
    post = post.rename(columns = {'post_text_pred':'label', 'post_time':'time'})
    post['type'] = 'post'

    comments=data[['comment_time', 'comment_text_pred']]
    comments = comments.rename(columns = {'comment_text_pred':'label', 'comment_time':'time'})
    comments['type'] = 'comment'

    #Filter by chosen content type
    if content_type == 'Posts':
        timeSeries = post
    elif content_type == 'Comments':
        timeSeries = comments
    else:
        timeSeries = pd.concat([post, comments])

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

#Function to create a node
def make_node(input, node_type, cluster_size = 1):
    if node_type == 'post':
        hashed_id = input['hashed_post_id']
        group = input['group']
        label = input['post_text_pred']
        time = input['post_time'].strftime('%d-%m-%Y %X')
        username = input['hashed_username']
        text = input['post_text'].replace('\n','')
        likes = input['likes']
        reactions = input['reactions']

        element = {'data': {'label': label, 'text': text, 'cluster_size':cluster_size,'id': hashed_id, 'time': time, 'username': username,
                            'group':group,'likes': likes, 'size': min(400, max(200,likes/5)), 'reactions':reactions},'classes':'post'}

    elif node_type == 'comment':
        #comment
        hashed_id = input['hashed_comment_id']
        group = input['group']
        label = input['comment_text_pred']
        time = input['comment_time'].strftime('%d-%m-%Y %X')
        username = input['hashed_commenter_name']
        text = input['comment_text'].replace('\n','')
        likes = input['likes']
        #Convert time elapsed to minutes
        elapsed = input['time_elapsed'].days*1440 + round(input['time_elapsed'].seconds/60,2)
        element = {'data': {'label': label, 'text': text, 'num_comments':cluster_size,'id': hashed_id, 'group': group, 'time': time, 'username': username,
                            'likes':likes, 'time_elapsed':str(elapsed) + ' minutes'}}
        
    return element

 #Post-centric network graph
@app.callback(
    Output('cytoscape-graph', 'elements'),
    Input('search_box', 'value'),
    Input('filter_labels', 'value'),
    Input('filter_group', 'value'),
    Input('top_n_clusters', 'value'),
    Input('time_slider', 'value'),
    Input("time_slider", "max"))

def update_graph(search, label_name, group_name, num_clusters, time_elapsed, time_limit):
    graph_edges = []
    nodes = []
    
    #Create a copy of the input data
    post_df = data.copy()
    post_df = post_df.dropna(subset = ['post_text', 'post_time'])
    #Filter by label dropdown
    if label_name != 'All':
        post_df = post_df[post_df['post_text_pred'] == label_name]
    #Filter by groups
    if group_name != 'All':
        post_df = post_df[post_df['group'] == group_name]
    #Filter by search entry
    if search:
        post_df = post_df[post_df['post_text'].str.contains(search, case = False)]
    
    #Get top n posts in terms of number of reactions
    posts=post_df[['group','likes','comments','shares','reactions',
               'reaction_count','hashed_post_id',
               'hashed_username','post_text','post_time','post_text_pred', 'time_elapsed']].reset_index(drop = True)
    posts = posts.loc[posts.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True)
    posts = posts.sort_values(by = 'reaction_count', ascending = False).iloc[0:num_clusters].reset_index(drop = True)
    #Filter comments based on time elapsed
    if time_elapsed < time_limit:
        post_filtered = post_df[post_df['time_elapsed'] < datetime.timedelta(minutes = time_elapsed)].copy()
    else:
        post_filtered = post_df.copy()
    #Iterate through unique post_ids
    for count, post_id in enumerate(posts['hashed_post_id'].unique()):
        comment_df = post_filtered[post_filtered['hashed_post_id'] == post_id]
        comment_df = comment_df.dropna(subset = ['comment_text', 'comment_time'])
        comment_df=comment_df[['group','likes','comments','shares','reactions','reaction_count','hashed_post_id', 
                        'hashed_comment_id','hashed_commenter_name','comment_text','comment_time','comment_text_pred',
                        'comment_text_pred_prob', 'time_elapsed']]
        
        #Add comment edges and nodes
        for row in comment_df.index:
            #Add edge
            target = comment_df.loc[row, 'hashed_comment_id']
            edge_id = post_id + ',' + target
            element = {'data': {'id': edge_id, 'source':comment_df.loc[row, 'comment_text_pred'] + str(count), 'target':target}, 
            'classes':comment_df.loc[row, 'comment_text_pred']}
            graph_edges.append(element)
            #Add node
            comment_row = comment_df.loc[row]
            label = comment_df.loc[row, 'comment_text_pred']
            comment_cluster = len(comment_df[comment_df['comment_text_pred'] == label])
            nodes.append(make_node(comment_row, 'comment', cluster_size=comment_cluster))
        #Add post node
        cluster_size = len(comment_df)
        post_row = posts.loc[count]
        nodes.append(make_node(post_row, 'post', cluster_size = cluster_size))

        #Group together all comments with the same label
        for label in comment_df['comment_text_pred'].unique():
            filtered_comments = comment_df[comment_df['comment_text_pred'] == label]
            nodes.append({'data':{'id':label + str(count), 'label':label, 'num_comments':len(filtered_comments)},'classes':'comment'})
            target = label + str(count)
            edge_id = post_id + ',' + target
            element = {'data': {'id': edge_id, 'source':post_id, 'target':target}}
            graph_edges.append(element)

    all_elements = nodes + graph_edges
    return all_elements

#Display node data when hovering
@app.callback(Output('cytoscape-tapNodeData-json', 'children'),
              Input('cytoscape-graph', 'mouseoverNodeData'))
              
def displayTapNodeData(data):
    if data:
        #return json.dumps(data, indent=2, ensure_ascii=False)
        if 'text' in data:
            data_copy = data.copy()
            for key in data.keys():
                if key in ['username', 'id']:
                    data_copy.pop(key)
            return json.dumps(data_copy, indent=2, ensure_ascii=False)
        else:
            return_dict = {'label':data['label'], 'num_comments':data['num_comments']}
            return json.dumps(return_dict, indent=2, ensure_ascii=False)

#Filter time slider by clicked post
@app.callback(
    [Output("time_slider", "min"),
    Output("time_slider", "max"),
    Output("time_slider", "marks"),
    Output("time_slider", "value")],
    Input('cytoscape-graph', 'tapNodeData'))
def display_click_data(clickData):
    marks_dict = {}
    for i in range(0, 101, 10):
        marks_dict[i] = {'label': str(i) + ' min'}
    if clickData and 'size' in clickData:
        post = clickData['id']
        elapsed_time = data[data['hashed_post_id'] == post]['time_elapsed']
        
        #Get min number of minutes elapsed
        lower = elapsed_time.min().days*1440 + math.floor(elapsed_time.min().seconds/60)
        
        #Get max number of minutes elapsed
        upper = elapsed_time.max().days*1440 + math.ceil(elapsed_time.max().seconds/60)
        #Set the minimum to be 1
        if lower == 0:
            lower += 1
            upper += 1
        #Set the range to be 99 minutes, or up until the upper limit
        upper_limit = min(upper, lower + 99)
        #Slider markings
        markings = max(1, math.ceil((upper_limit - lower)/5))
        marks_dict = {}
        for i in range(lower, upper_limit + 1, markings):
            unit = ' min'
            if i == upper_limit and upper_limit < upper:
                unit = '+' + unit
            marks_dict[i] = {'label': str(i) + unit}
        return [lower, upper_limit, marks_dict, upper_limit]
    #Placeholder
    return [1,100, marks_dict, 100]

#Update card data
@app.callback(
Output("numPosts", "children"),
Output("avgPostLen", "children"),
Output("numComments", "children"),
Output("avgCommentLen", "children"),
Output("numUsers", "children"),
Output("userDescription", "children"),
Input('cytoscape-graph', 'tapNodeData'))

def helper(clickData):
    posts = data.loc[data.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True)
    post_lengths = posts['post_text'].str.split("\\s+")
    #Number of posts
    num_posts = f'{data["hashed_post_id"].nunique():,} rows'
    #Average length of each post
    avg_post_length = round(post_lengths.str.len().mean())
    post_length_text = f'Average post length: {avg_post_length:,} words'
    #Number of comments
    num_comments = f'{len(data):,} rows'
    #Average length of each comment
    avg_comment_length = round(data['comment_text'].str.len().mean())
    comment_length_text = f'Average comment length: {avg_comment_length:,} words'

    #Number of people who made posts
    posters = data['hashed_username']
    commenters = data['hashed_commenter_name']
    all_users = f'{pd.Series(np.concatenate((posters, commenters))).nunique():,} people'
    user_description = f'{commenters.nunique():,} commenters, {posters.nunique():,} posters'

    return [num_posts, post_length_text, num_comments,
                comment_length_text, all_users, user_description]


if __name__ == '__main__':
    app.run_server(debug=True)

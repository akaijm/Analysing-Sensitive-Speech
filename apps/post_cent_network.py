
# Importing modules
import json
import dash_cytoscape as cyto
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import datetime
import math
from app import app


#Read in the processed data with post_dates set prior to the earliest comment_date
data = pd.read_csv('outputs/overview_cards post-centric_graph/time_elapsed.csv',encoding="utf-8")
data['post_time'] = pd.to_datetime(data['post_time'])
data['comment_time'] = pd.to_datetime(data['comment_time'])
data['time_elapsed'] = pd.to_timedelta(data['time_elapsed'])

all_labels = ['All']
all_labels = data['post_text_pred'].unique()
#Sort in descending order
all_labels[::-1].sort()
all_labels = np.append(['All'], all_labels)

#Prepare dropdown for group filter
all_groups = ['All']
all_groups = np.append(all_groups, data['group'].unique())

layout = html.Div([
        html.Div([
            html.Div([dcc.Markdown("**Post-centric Network Graph**",style={'color': 'black', 'fontSize': 25,'text-align': 'center'})]),
            html.Div([
                dcc.Markdown('Filter by Class'),
                dcc.Dropdown(
                    id='filter_label',
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
                    )], style={'display':'inline-block', 'width':'20%', 'padding-left':30}),
            html.Div([
                dcc.Markdown('Search for a Post'),
                dcc.Input(
                id = "search_box",
                type = "text",
                placeholder = "Input search term",
                debounce=True,
                value = ' ',
                )],style={'display':'inline-block', 'width':'20%',  'float':'right'})]),
        
            cyto.Cytoscape(
                id='cytoscape-graph',
                style={'width': '100%', 'height': 750},
                layout={'name': 'cose','animate':True, 'fit':True
                        , 'numIter':100, 'gravity': 100, 'nodeRepulsion': 500000000, 
                        'boundingBox':{'x1':0, 'x2':7000, 'y1':0, 'y2':5000}},
                responsive = True,
                maxZoom = 0.2,
                minZoom = 0.08,
                stylesheet=[
                            {
                                "selector": "node",
                                "style": {
                                    "font-size": "100px",
                                    "text-valign": "center",
                                    "text-halign": "center",
                                    'width':50,
                                    'height':50

                            },
                                },
                            {
                                'selector' :'[label ^= "tyrannical"]',
                                'style': {
                                    'background-color': '#0459eb' #dark blue
                            }
                                },
                            {
                                'selector' :'[label ^= "vto pap"]',
                                'style': {
                                    'background-color': '#B6D0E2' #light blue
                            }
                                },
                            {
                                'selector' :'[label ^= "dehuman"]',
                                'style': {
                                    'background-color': '#f0063e' #red
                            }
                                },
                            {
                                'selector' :'[label ^= "ingroup"]',
                                'style': {
                                    'background-color': '#f0d137' #yellow
                            }
                                },
                            {
                                'selector' :'[label ^= "culture"]',
                                'style': {
                                    'background-color': '#cfa502' #light brown
                            }
                                },
                            {
                                'selector' :'[label ^= "import"]',
                                'style': {
                                    'background-color': '#eb8bbe' #pink
                            }
                                },
                            {
                                'selector' :'[label ^= "racist"]',
                                'style': {
                                    'background-color': '#551f02' #dark brown
                            }
                                },
                            {
                                'selector' :'[label ^= "agreement"]',
                                'style': {
                                    'background-color': '#316102' #dark green
                            }
                                },
                            {
                                'selector' :'[label ^= "opp"]',
                                'style': {
                                    'background-color': '#7cf605' #light green
                            }
                                },
                            {
                                'selector' :'[label ^= "others"]',
                                'style': {
                                    'background-color': '#cacdc7' #grey
                            }
                                },
                            {
                                'selector' :'[label ^= "insult"]',
                                'style': {
                                    'background-color': '#8105c0' #purple
                            }
                                },
                            {
                                'selector': '.comment',
                                'style': {
                                    'content': 'data(label)',
                                    "background-color":"white",
                                    "width": "250",
                                    "height": "100",
                                    "font-size": "100px",
                                    "text-valign": "center",
                                    "text-halign": "center"
                                }
                            },
                            
                            {
                                'selector': '.post',
                                'style': {
                                    "width": "data(size)",
                                    "height": "data(size)",
                                    "shape": "triangle"
                                }
                            },
                            {
                                'selector': 'edge',
                                'style': {

                                    'curve-style': 'bezier',
                                    "opacity": 1,
                                    'width':"1.5",
                                }
                            },
                            {
                                'selector' :".tyrannical",
                                'style': {
                                    'line-color':'#0459eb',
                                    'background-color': '#0459eb' #dark blue
                            }
                                },
                            {
                                'selector' :'.vto pap',
                                'style': {
                                    'line-color':'#B6D0E2',
                                    'background-color': '#B6D0E2' #light blue
                            }
                                },
                            {
                                'selector' :'.dehuman',
                                'style': {
                                    'line-color':'#f0063e',
                                    'background-color': '#f0063e' #red
                            }
                                },
                            {
                                'selector' :'.ingroup',
                                'style': {
                                    'line-color':'#f0d137',
                                    'background-color': '#f0d137' #yellow
                            }
                                },
                            {
                                'selector' :'.culture',
                                'style': {
                                    'line-color':'#cfa502',
                                    'background-color': '#cfa502' #light brown
                            }
                                },
                            {
                                'selector' :'.import',
                                'style': {
                                    'line-color':'#eb8bbe',
                                    'background-color': '#eb8bbe' #pink
                            }
                                },
                            {
                                'selector' :'.racist',
                                'style': {
                                    'line-color':'#551f02',
                                    'background-color': '#551f02'#dark brown
                            }
                                },
                            {
                                'selector' :'.agreement',
                                'style': {
                                    'line-color':'#316102',
                                    'background-color': '#316102' #dark green
                            }
                                },
                            {
                                'selector' :'.opp',
                                'style': {
                                    'line-color':'#7cf605',
                                    'background-color': '#7cf605' #light green
                            }
                                },
                            {
                                'selector' :'.others',
                                'style': {
                                    'line-color':'#cacdc7',
                                    'background-color': '#cacdc7' #grey
                            }
                                },
                            {
                                'selector' :'.insult',
                                'style': {
                                    'line-color':'#8105c0',
                                    'background-color': '#8105c0' #purple
                            }
                                }
                            
                        ]
                ),
            html.Div([
                dcc.Markdown("**Time Elapsed (Click on triangle node to filter)**",
                    style={'color': 'black', 'fontSize': 15,
                            'text-align': 'center', 'float':'middle'}),
                dcc.Slider(
                    id = 'time_slider'
            ),
            html.Div([
                html.Div([  
                    html.H5("Details on Source Post",
                    style={'color': 'black', 'fontSize': 15,
                            'text-align': 'center', 'float':'middle'}), 
                    html.Pre(id='cytoscape-postNodeData-json')
                ], style={'border': 'thin lightgrey solid','overflowX': 'auto','height':'320px',
                             'width':'55%', 'display':'inline-block'
                            }),
                html.Div([  
                    html.H5("Details on Hovered Node",
                    style={'color': 'black', 'fontSize': 15,
                            'text-align': 'center', 'float':'middle'}), 
                    html.Pre(id='cytoscape-tapNodeData-json')
                ], style={'border': 'thin lightgrey solid','overflowX': 'auto','height':'320px',
                             'width':'45%', 'display':'inline-block'
                })
            ])
    ],style={'width':'100%', 'float':'middle','padding-left':100, 'padding-right':100})])

#Function to create a node
def make_node(input, node_type, cluster_size = 1):
    if node_type == 'post':
        hashed_id = input['hashed_post_id']
        group = input['group']
        label = input['post_text_pred']
        time = input['post_time'].strftime('%d-%m-%Y %X')
        username = input['hashed_username']
        #Check for NaN
        if input['post_text'] == input['post_text']:
            #Remove next line characters
            text = input['post_text'].replace('\n','')
        else:
            text = ' '
        likes = input['likes']
        reactions = input['reactions']
        sentiment = round(input['sentiment'], 2)

        element = {'data': {'label': label, 'text': text, 'cluster_size':cluster_size,'id': hashed_id, 'post_id': hashed_id, 'time': time, 'username': username,
                             'sentiment': sentiment, 'group': group,'likes': likes, 'size': min(400, max(200,likes/5)), 'reactions':reactions},'classes':'post'}

    elif node_type == 'comment':
        #comment
        hashed_id = input['hashed_comment_id']
        post_id = input['hashed_post_id']
        group = input['group']
        label = input['comment_text_pred']
        time = input['comment_time'].strftime('%d-%m-%Y %X')
        username = input['hashed_commenter_name']
        if input['comment_text'] == input['comment_text']:
            text = input['comment_text'].replace('\n','')
        else:
            text = ' '
        likes = input['likes']
        sentiment = round(input['sentiment'], 2)
        #Convert time elapsed to minutes
        elapsed = input['time_elapsed'].days*1440 + round(input['time_elapsed'].seconds/60,2)
        element = {'data': {'label': label, 'text': text, 'num_comments':cluster_size,'id': hashed_id, 'post_id':post_id,
                             'group': group, 'time': time, 'username': username,'sentiment': sentiment,'likes':likes, 
                             'time_elapsed':f'{elapsed:.2f} minutes'}}
        
    return element

 #Post-centric network graph
@app.callback(
    Output('cytoscape-graph', 'elements'),
    Input('search_box', 'value'),
    Input('filter_label', 'value'),
    Input('filter_group', 'value'),
    Input('top_n_clusters', 'value'),
    Input('time_slider', 'value'),
    Input("time_slider", "max"))

def update_graph(search, label_name, group_name, num_clusters, time_elapsed, time_limit):

    #Prepare post data
    post_df = data.loc[data.groupby('hashed_post_id')['post_time'].idxmin()].reset_index(drop = True).copy()

    #Prepare comments data
    comments = data[data['hashed_comment_id'] != '0'].copy()

    graph_edges = []
    nodes = []

    #Filter by label dropdown
    if label_name != 'All':
        post_df = post_df[post_df['post_text_pred'] == label_name]
    #Filter by groups
    if group_name != 'All':
        post_df= post_df[post_df['group'] == group_name]
    #Filter by search entry
    if search:
        post_df = post_df[post_df['post_text'].str.contains(search, case = False, na=False)]
    
    #Get top n posts in terms of number of reactions
    posts=post_df[['group','likes','comments','shares','reactions', 'sentiment',
               'reaction_count','hashed_post_id',
               'hashed_username','post_text','post_time','post_text_pred']].reset_index(drop = True)
    posts = posts.sort_values(by = 'reaction_count', ascending = False).iloc[0:num_clusters].reset_index(drop = True)
    
    #Filter comments based on time elapsed
    if time_elapsed < time_limit:
        comments = comments[comments['time_elapsed'] < datetime.timedelta(minutes = time_elapsed)].copy()
    else:
        comments = comments.copy()
    #Iterate through unique post_ids
    for count, post_id in enumerate(posts['hashed_post_id'].unique()):
        comment_df = comments[comments['hashed_post_id'] == post_id]
        comment_df = comment_df.dropna(subset = ['comment_text', 'comment_time'])
        comment_df=comment_df[['group','likes','comments','shares','reactions','reaction_count','hashed_post_id', 'sentiment',
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
            nodes.append({'data':{'id':label + str(count), 'label':label, 'num_comments':len(filtered_comments), 
                                'post_id':post_id},'classes':'comment'})
            target = label + str(count)
            edge_id = post_id + ',' + target
            element = {'data': {'id': edge_id, 'source':post_id, 'target':target}}
            graph_edges.append(element)

    all_elements = nodes + graph_edges
    return all_elements

#Display node data when hovering
@app.callback(
Output('cytoscape-tapNodeData-json', 'children'),
Output('cytoscape-postNodeData-json', 'children'),
Input('cytoscape-graph', 'mouseoverNodeData'),
Input('time_slider', 'value'),
Input("time_slider", "max"))
              
def displayTapNodeData(node, time_elapsed, time_limit):
    data_copy = {}
    source_post = {}
    output = []
    if node:
        post_id = node['post_id']
        #Check if it is a post
        if 'cluster_size' in node:
            data_copy['Label'] = node['label']
            data_copy['Post Text'] = node['text']
            data_copy['No. of Comments for This Post'] = node['cluster_size']
            data_copy['Post Sentiment'] = node['sentiment']
            data_copy['Date Posted'] = node['time']
            data_copy['Group'] = node['group']
            data_copy['Reactions'] = node['reactions']
            output.append(json.dumps(data_copy, indent=2, ensure_ascii=False,sort_keys=False))
        
        #Check if it is a comment
        elif 'time_elapsed' in node:
            data_copy['Label'] = node['label']
            data_copy['Comment Text'] = node['text']
            data_copy['Comment Sentiment'] = node['sentiment']
            data_copy['Time Elapsed Before Comment Was Made'] = node['time_elapsed']
            data_copy['Comment Time'] = node['time']
            data_copy['No. of Comments with the Same Label'] = node['num_comments']
            output.append(json.dumps(data_copy, indent=2, ensure_ascii=False,sort_keys=False))
        else:
            output.append('')

        #Generate post details from post_id
        post_df = data.loc[data.groupby('hashed_post_id')['post_time'].idxmin()]
        post_df = post_df.loc[post_df['hashed_post_id'] == post_id].reset_index(drop = True).iloc[0]

        #Get cluster size
        comments = data[data['hashed_comment_id'] != '0'].copy()

        if time_elapsed < time_limit:
            comments = comments[comments['time_elapsed'] < datetime.timedelta(minutes = time_elapsed)].copy()

        comment_df = comments[comments['hashed_post_id'] == post_id]
        comment_df = comment_df.dropna(subset = ['comment_text', 'comment_time'])

        source_post['Label'] = post_df['post_text_pred']
        source_post['Post Text'] = post_df['post_text']
        source_post['No. of Comments for This Post'] = len(comment_df)
        source_post['Post Sentiment'] = round(post_df['sentiment'], 2)
        source_post['Date Posted'] = post_df['post_time'].strftime('%d-%m-%Y %X')
        source_post['Group'] = post_df['group']
        source_post['Reactions'] = post_df['reactions']
        
        output.append(json.dumps(source_post, indent=2, ensure_ascii=False,sort_keys=False))
    else:
        output = ['', '']
    return output

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
        #Get the clicked post id
        post = clickData['id']
        #Filter the data to retrieve comments corresponding to this post
        filtered_by_time = data[data['hashed_post_id'] == post]
        #If no comments are found, set elapsed time to be 1
        elapsed_time = 1
        if len(filtered_by_time) > 0:
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

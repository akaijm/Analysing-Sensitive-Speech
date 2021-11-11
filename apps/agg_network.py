# Importing modules
import pandas as pd
import numpy as np
import networkx as nx
import re

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.offline as py
import plotly.graph_objs as go

from app import app

# load nodes infoamation
nodesdf = pd.read_csv("outputs/agg_network/nodes.csv")
nodesdfpost = nodesdf[nodesdf['type'] == 'post']
nodesdfresponse = nodesdf[nodesdf['type'] == 'comment']
nodesdf2 = nodesdf[['topic', 'centrality']].sort_values(
    by=['centrality'], ascending=False)
nodesdfpostfrequency = nodesdfpost[['topic', 'freq']].sort_values(
    by=['freq'], ascending=False)
nodesdfresponsefrequency = nodesdfresponse[[
    'topic', 'freq']].sort_values(by=['freq'], ascending=False)


nodes = {}
names = nodesdf.topic.tolist()
freq = nodesdf.freq.tolist()
types = nodesdf.type.tolist()
centralities = nodesdf.centrality.tolist()

for i in range(len(names)):
    name = names[i]
    topic = name.split('_')[0]
    typee = types[i]
    centrality = centralities[i]
    if typee == 'post':
        if name == 'tyrannical':
            nodes[names[i]] = [freq[i]*20, "#0459eb",
                               "triangle-up", freq[i], centrality]
        else:
            nodes[names[i]] = [freq[i]*20, "blue",
                               "triangle-up", freq[i], centrality]
    else:
        nodes[names[i]] = [freq[i], "blue", "circle", freq[i], centrality]


network = nx.Graph()
# Add node for each character

for p_label in nodes.keys():
    if nodes[p_label][0] > 0:
        network.add_node(p_label, size=nodes[p_label][0]/1000+1, node_color=nodes[p_label][1],
                         symbol=nodes[p_label][2], freq=nodes[p_label][3], centrality=nodes[p_label][4])
#print(network.nodes())

# load edge information
edges = pd.read_csv('outputs/agg_network/edges.csv')
edgedf2 = edges[['source', 'target', 'weight']].sort_values(
    by=['weight'], ascending=False).head(10)
#print(edgedf2.head()) # prints to terminal
#get median of the edge weight to be set as default value for slider filter
medianweight=edges['weight'].median()
maxweight=edges['weight'].max()
maxweightthreshold=maxweight-1

comments_to_posts = {'agreement_post': {}, 'culture_post': {}, 'dehuman_post': {}, 'import_post': {}, 'ingroup_post': {
}, 'insult_post': {}, 'opp_post': {}, 'others_post': {}, 'racist_post': {}, 'tyrannical_post': {}, 'vto pap_post': {}}
for index, row in edges.iterrows():
    source = row['source']
    target = row['target']
    weight = row['weight']
    comments_to_posts[source][target] = weight/1000+1

# For each co-appearance between two characters, add an edge
for p_label in comments_to_posts.keys():
    for c_label in comments_to_posts[p_label].keys():

        # Only add edge if the count is positive
        if comments_to_posts[p_label][c_label] > 0:
            network.add_edge(p_label, c_label,
                             weight=comments_to_posts[p_label][c_label])

pos_ = nx.spring_layout(network)


def make_edge(x, y, text, width):
    '''Creates a scatter trace for the edge between x's and y's with given width

    Parameters
    ----------
    x    : a tuple of the endpoints' x-coordinates in the form, tuple([x0, x1, None])

    y    : a tuple of the endpoints' y-coordinates in the form, tuple([y0, y1, None])

    width: the width of the line

    Returns
    -------
    An edge trace that goes between x0 and x1 with specified width.
    '''
    return go.Scatter(x=x,
                      y=y,
                      line=dict(width=width,
                                color='cornflowerblue'),
                      hoverinfo='text',
                      text=([text]),
                      mode='lines')


# For each edge, make an edge_trace, append to list
edge_trace = []

for edge in network.edges():

    if network.edges()[edge]['weight'] > 0:
        # weights.append((network.edges()[edge]['weight']-1)*1000)
        char_1 = edge[0]
        char_2 = edge[1]

        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]

        text = char_1 + '--' + char_2 + ': ' + \
            str(network.edges()[edge]['weight'])

        trace = make_edge([x0, x1, None], [y0, y1, None], text,
                          0.3*network.edges()[edge]['weight']**1.75)

        edge_trace.append(trace)

# Make a node trace
node_trace = go.Scatter(x=[],
                        y=[],
                        text=[],
                        textposition="top center",
                        textfont_size=10,
                        mode='markers+text',
                        hoverinfo='none',
                        marker=dict(color=[],
                                     size=[],
                                     symbol=[],
                                     line=None))
# For each node in midsummer, get the position and size and add to the node_trace

#print(network.nodes())
for node in network.nodes():
    x, y = pos_[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    #node_trace['freq'] +=tuple([network.nodes()[node]['freq']])
    #print(node)
    node_trace['marker']['color'] += tuple(
        [network.nodes()[node]['node_color']])
    node_trace['marker']['size'] += tuple([7.5*network.nodes()[node]['size']])
    node_trace['marker']['symbol'] += tuple([network.nodes()[node]['symbol']])
    # node_trace['hovertemplate']='Frequency:'+str(network.nodes()[node]['freq'])
    node_trace['text'] += tuple(['<b>' + node + '</b>'])
    #node_trace['text'] += tuple(['Type: '+'<b>'+node+'</b>'+'      \nFrequency: '+'<b>' + str(network.nodes()[node]['freq']) + '</b>'+'\n     Centrality:'+'<b>'+str(network.nodes()[node]['centrality'])+ '</b>'])

textsall = list(node_trace['text'])

fig_layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig = go.Figure(layout=fig_layout)
'''
for trace in edge_trace:
    fig.add_trace(trace)

fig.add_trace(node_trace)

fig.update_layout(showlegend = False)

fig.update_xaxes(showticklabels = False)

fig.update_yaxes(showticklabels = False)
'''

# fig.show()
#py.plot(fig, filename='network.html')
labels = ['import', 'agreement', 'racist', 'culture', 'dehuman',
          'ingroup', 'insult', 'opp', 'others', 'tyrannical', 'vto pap']

layout = html.Div([
    html.Div([
        dbc.Row(
            [
                dbc.Col([
                    html.P(
                        'Choose the post topic of your interest:', style={'font-weight': 'bold'}),
                    dcc.Checklist(
                        id='checkbox',
                        options=[
                            {'label': 'dehuman   ',
                             'value': 'dehuman'},
                            {'label': 'tyrannical   ',
                             'value': 'tyrannical'},
                            {'label': 'vto pap   ',
                             'value': 'vto pap'},
                            {'label': 'ingroup   ',
                             'value': 'ingroup'},
                            {'label': 'culture   ',
                             'value': 'culture'},
                            {'label': 'import   ', 'value': 'import'},
                            {'label': 'others   ', 'value': 'others'},
                            {'label': 'insult   ', 'value': 'insult'},
                            {'label': 'opp   ', 'value': 'opp'},
                            {'label': 'agreement   ',
                             'value': 'agreement'},
                            {'label': 'racist', 'value': 'racist'},
                        ],
                        value=['dehuman', 'tyrannical', 'vto pap', 'ingroup', 'culture',
                               'import', 'others', 'insult', 'opp', 'agreement', 'racist'],
                        inputStyle={"marginLeft": "20px",
                                    "marginRight": "5px"}
                    ),
                    html.P(
                        'Please drag the slider to set a threshold for edge weight:', style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id='my-slider',
                        min=0,
                        max=maxweight,
                        step=10,
                        value=medianweight,
                    ),
                    html.P(
                        'Please key in a threshold for edge weight between 0 and {} and press enter:'.format(maxweightthreshold), style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id = "my-slider2",
                        type = "number",
                        placeholder = 0,
                        debounce=True,
                        value = medianweight,
                        ),
                    dcc.Graph(id='network', figure=fig, style={
                              'width': '100%', 'height': '70vh', 'display': 'inline-block'})
                ], width=8),
                dbc.Col([
                    dcc.Tabs(id="tabs", value='centrality', children=[
                        dcc.Tab(label='centrality', value='centrality'),
                        dcc.Tab(label='post frequency', value='pfrequency'),
                        dcc.Tab(label='comment frequency',
                                value='rfrequency'),
                        dcc.Tab(label='weight', value='weight')
                    ]),
                    html.Div(id='table', style={'textAlign': 'center'})
                ], width=4)
            ]
        )
    ], style={'width': '100%', 'display': 'inline-block'})
])

@app.callback(
    [Output('my-slider', 'value'),
    Output('my-slider2', 'value')],
    [Input('my-slider', 'value'),
    Input('my-slider2', 'value')])
def update_graph(slider_val, input_val):
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == 'my-slider.value':
        return [slider_val, slider_val]
    return [input_val, input_val]


@app.callback(
    Output('network', 'figure'),
    Input('checkbox','value'),
    Input('my-slider', 'value'))
def update_graph(boxval, syncval):
    labels = ""
    node_trace2 = node_trace
    postname = labels+'_post'
    responsename = labels+'_comment'
    cnt = 0
    colors = list(node_trace['marker']['color'])
    texts = textsall
    # print(network.nodes().keys())
    # print(boxval)
    for i in network.nodes().keys():
        topici = i.split('_')[0]
        typei = i.split('_')[1]

        if topici not in boxval and typei == 'post':
            colors[cnt] = 'white'
            texts[cnt] = ""
        else:
            texts[cnt] = i
            if topici == 'dehuman':
                colors[cnt] = '#f0063e'
            elif topici == 'tyrannical':
                colors[cnt] = '#0495eb'
            elif topici == 'vto pap':
                colors[cnt] = "#B6D0E2"
            elif topici == 'ingroup':
                colors[cnt] = "#f0d137"
            elif topici == 'culture':
                colors[cnt] = "#cfa502"
            elif topici == 'import':
                colors[cnt] = "#eb8bbe"
            elif topici == 'others':
                colors[cnt] = "#cacdc7"
            elif topici == 'insult':
                colors[cnt] = "#8105c0"
            elif topici == 'opp':
                colors[cnt] = '#7cf605'
            elif topici == 'agreement':
                colors[cnt] = '#316102'
            elif topici == 'racist':
                colors[cnt] = '#551f02'
        cnt += 1
    node_trace2['marker']['color'] = tuple(colors)
    node_trace2['text'] = tuple(texts)
    fig = go.Figure(layout=fig_layout)
    #print(node_trace2['text'])
    fig.add_trace(node_trace2)
    # For each edge, make an edge_trace, append to list
    edge_trace = []

    fig = go.Figure(layout=fig_layout)
    fig.add_trace(node_trace2)
    for edge in network.edges():
        # print(edge)
        if (network.edges()[edge]['weight']-1)*1000 > int(syncval) and edge[0].split('_')[0] in boxval:
            # weights.append((network.edges()[edge]['weight']-1)*1000)
            char_1 = edge[0]
            char_2 = edge[1]

            x0, y0 = pos_[char_1]
            x1, y1 = pos_[char_2]

            text = char_1 + '--' + char_2 + ': ' + \
                str(network.edges()[edge]['weight'])

            trace = make_edge([x0, x1, None], [y0, y1, None], text,
                            0.3*network.edges()[edge]['weight']**1.75)

            edge_trace.append(trace)

    for trace in edge_trace:
        fig.add_trace(trace)

    fig.update_layout(
        title_text='Showing edges with weight >{}.'.format(
            syncval)
    )
    fig.update_layout(showlegend=False)

    fig.update_xaxes(showticklabels=False)

    fig.update_yaxes(showticklabels=False)
    return fig


@app.callback(
    Output('table', 'children'),
    #Input('labelss', 'value'),
    Input('tabs', 'value'))
def update_graph(choice):
    if choice == 'centrality':
        return html.Div([dash_table.DataTable(id='tbl', data=nodesdf2.to_dict('records'), columns=[{"name": i, "id": i} for i in nodesdf2.columns],style_cell={'textAlign': 'center', 'paddingLeft': '10px', 'paddingRight': '10px'},style_header={'backgroundColor': 'white','fontWeight': 'bold'})], style={'display': 'inline-block', 'textAlign': 'center'})
    if choice == 'pfrequency':
        return html.Div([dash_table.DataTable(id='tbl2', data=nodesdfpostfrequency.to_dict('records'), columns=[{"name": i, "id": i} for i in nodesdfpostfrequency.columns],style_cell={'textAlign': 'center','paddingLeft': '10px', 'paddingRight': '10px'},style_header={'backgroundColor': 'white','fontWeight': 'bold'})], style={'display': 'inline-block', 'textAlign': 'center'})
    if choice == 'rfrequency':
        return html.Div([dash_table.DataTable(id='tbl4', data=nodesdfresponsefrequency.to_dict('records'), columns=[{"name": i, "id": i} for i in nodesdfresponsefrequency.columns],style_cell={'textAlign': 'center','paddingLeft': '10px', 'paddingRight': '10px'},style_header={'backgroundColor': 'white','fontWeight': 'bold'})], style={'display': 'inline-block', 'textAlign': 'center'})
    if choice == 'weight':
        return html.Div([dash_table.DataTable(id='tbl3', data=edgedf2.to_dict('records'), columns=[{"name": i, "id": i} for i in edgedf2.columns],style_cell={'textAlign': 'center','paddingLeft': '10px', 'paddingRight': '10px'},style_header={'backgroundColor': 'white','fontWeight': 'bold'})], style={'display': 'inline-block', 'textAlign': 'center'})

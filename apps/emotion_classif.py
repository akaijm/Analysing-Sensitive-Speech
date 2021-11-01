# Importing modules
import pandas as pd

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

from app import app

df = pd.read_csv("outputs\distilbert_emotion\emotion_data.csv")

labels = sorted(set(df.label))
lab_options = [{'label': lab.capitalize(), 'value': lab} for lab in labels]

layout = html.Div([
    html.Div
    ([
        dcc.Dropdown(
            id='labels-dropdown',
            options = lab_options,
            multi=True,
            value = [lab_options[0]['value']]
        )], style={'width': '100%', 'display':'inline-block'}
    ), 
    dcc.Graph(id = 'distilbert-emotion')
    
])

@app.callback(
    Output('distilbert-emotion', 'figure'), 
    Input('labels-dropdown', 'value')
)
def emotion_barchart(labels):
    EMOTIONS = sorted(['anger', 'disgust', 'fear', 'surprise', 'sad', 'neutral', 'happy'])
    #COLORS = {'sad': '#0494EC', 'anger': '#B32408', 'fear': '#BC84DC', 'disgust': '#74BB43', 'happy': '#FFEE15', 'neutral': '#040404', 'surprise': '#EB8B25'}
    
    data = []
    for emotion in EMOTIONS:
        df_cnt = df[(df['label'].isin(labels)) & (df['emotion'] == emotion)]
        df_cnt = df_cnt.label.value_counts().to_dict()
        x_value = labels
        y_value = [df_cnt.get(lab, 0) for lab in labels]
        data.append(go.Bar(name = emotion, x=x_value, y=y_value))#, marker_color = hex_to_rgb(COLORS[emotion])))

    fig = go.Figure(data=data)
    fig.update_layout(barmode='group')
    return fig
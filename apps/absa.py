# Importing modules
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go
from plotly.colors import hex_to_rgb

import pandas as pd

from app import app

FILE_DIR = 'outputs/absa_emotions/labelled_texts_absa_emotions.csv'
df = pd.read_csv(FILE_DIR)

df.entities = df.entities.apply(eval)
df.entities = [entity[0] if len(entity[0]) < 4 and entity[0].isupper() else entity[0].title() for entity in df.entities]
entities = sorted(set(df.entities))
ent_options = [{'label': entity, 'value': entity} for entity in entities]

layout = html.Div([
    html.Div
    ([
        dcc.Dropdown(
            id='entity-dropdown',
            options = ent_options,
            multi=True,
            value = [ent_options[0]['value']]
        )], style={'width': '100%', 'display':'inline-block'}
    ), 
    dcc.Graph(id = 'emotion-bar-chart')
    
])

@app.callback(
    Output('emotion-bar-chart', 'figure'), 
    Input('entity-dropdown', 'value')
)
def emotion_barchart(entity_chosen):
    EMOTIONS = sorted(['anger', 'disgust', 'fear', 'surprise', 'sad', 'neutral', 'happy'])
    #COLORS = {'sad': '#0494EC', 'anger': '#B32408', 'fear': '#BC84DC', 'disgust': '#74BB43', 'happy': '#FFEE15', 'neutral': '#040404', 'surprise': '#EB8B25'}
    df = pd.read_csv(FILE_DIR)
    df.entities = df.entities.apply(eval)
    df.entities = [entity[0] if len(entity[0]) < 4 and entity[0].isupper() else entity[0].title() for entity in df.entities]
    
    data = []
    for emotion in EMOTIONS:
        df_perc = df[df.entities.isin(entity_chosen) & (df['emotion_label'] == emotion)]
        df_cnt = df_perc['entities'].value_counts().to_dict()
        df_perc = {k:v/len(df[df['entities'].isin([k])]) for k,v in df_perc['entities'].value_counts().to_dict().items()}
        x_value = entity_chosen #[eval(entity)[0] for entity in entity_chosen]
        y_value = [df_perc.get(entity, 0) for entity in entity_chosen]
        count = [df_cnt.get(entity, 0) for entity in entity_chosen]
        data.append(go.Bar(name = emotion, meta=count, x=x_value, y=y_value, hovertemplate="Proportion of <b>" + emotion + "</b> in <b>%{label}</b>: %{value}<br>Count: %{meta}<extra></extra>"))#, marker_color = hex_to_rgb(COLORS[emotion])))

    fig = go.Figure(data=data)
    fig.update_layout(barmode='group')
    return fig

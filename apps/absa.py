# Importing modules
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go
from plotly.colors import hex_to_rgb

import pandas as pd

from app import app

FILE_DIR = 'outputs/absa_emotions/labelled_texts_absa_emotions.csv'
df = pd.read_csv(FILE_DIR)

df.entities = df.entities.apply(eval)
df.entities = [entity[0].upper() if len(entity[0]) < 4 else entity[0].title()
               for entity in df.entities]
entities = list(df.groupby('entities').size(
).sort_values(ascending=False).index)
ent_options = [{'label': entity, 'value': entity} for entity in entities]

emotion_scores = [i[2:-2].split(' ') for i in df['emotion']]
emotion_scores = [[float(j.strip()) for j in i if j] for i in emotion_scores]
emotion_scores = [max(i) for i in emotion_scores]
df['emotion_score'] = emotion_scores

layout = html.Div([
    dcc.Markdown("**Aspect Based Emotion Classification**",
                 style={'color': 'black', 'fontSize': 25, 'textAlign': 'center'}),
    html.Div
    ([
        dcc.Dropdown(
            id='entity-dropdown',
            options=ent_options,
            multi=True,
            value=[ent_options[0]['value']]
        ),
        dcc.Graph(id = 'emotion-bar-chart'),
        html.Div(id='toggle_absa_container', children=[
            dash_table.DataTable(
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                # style_as_list_view=True,
                id='absa_sample_texts',
                columns=[{"name": "Sample Text", "id": "text"}, {
                    "name": "Emotion Proportion", "id": "emotion_score"}],
                data=[{}],
                page_current=0,
                page_size=1,
                page_action='custom',
                style_cell={
                    'font_family': '"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
                },
                style_cell_conditional=[{
                    'if': {'column_id': 'text'},
                    'textAlign': 'left',
                    'maxWidth': '70%',
                                'minWidth': '70%',
                                'width': '70%'
                }, {
                    'if': {'column_id': 'emotion_score'},
                    'textAlign': 'center'
                }],
                css=[{
                    'selector': '.dash-spreadsheet td div',
                                'rule': '''
                                    max-height: 120px; min-height: 120px; height: 120px;
                                    display: block;
                                    overflow-y: auto;
                                    overflow-wrap: anywhere;
                                '''
                }]
            )], style={'display': 'none'})
    ], className='justify-content-center', style={'maxWidth': '95%', 'display': 'block'}),
])


@app.callback(
    Output('emotion-bar-chart', 'figure'),
    Input('entity-dropdown', 'value')
)
def emotion_barchart(entity_chosen):
    EMOTIONS = sorted(['anger', 'disgust', 'fear',
                      'surprise', 'sad', 'neutral', 'happy'])
    # COLORS = {'sad': '#0494EC', 'anger': '#B32408', 'fear': '#BC84DC', 'disgust': '#74BB43', 'happy': '#FFEE15', 'neutral': '#040404', 'surprise': '#EB8B25'}
    df = pd.read_csv(FILE_DIR)
    df.entities = df.entities.apply(eval)
    df.entities = [entity[0] if len(entity[0]) < 4 and entity[0].isupper(
    ) else entity[0].title() for entity in df.entities]

    data = []
    for emotion in EMOTIONS:
        df_perc = df[df.entities.isin(entity_chosen) & (
            df['emotion_label'] == emotion)]
        df_cnt = df_perc['entities'].value_counts().to_dict()
        df_perc = {k: v/len(df[df['entities'].isin([k])])
                   for k, v in df_perc['entities'].value_counts().to_dict().items()}
        # [eval(entity)[0] for entity in entity_chosen]
        x_value = entity_chosen
        y_value = [df_perc.get(entity, 0) for entity in entity_chosen]
        count = [df_cnt.get(entity, 0) for entity in entity_chosen]
        data.append(go.Bar(name=emotion, meta=count, x=x_value, y=y_value, hovertemplate="Proportion of <b>" + emotion +
                    "</b> in <b>%{label}</b>: %{value}<br>Count: %{meta}<extra></extra>"))  # , marker_color = hex_to_rgb(COLORS[emotion])))

    fig = go.Figure(data=data)
    fig.update_layout(title="Click on a bar to see a table of sample texts below.", font_family='"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',title_font=dict(size=15), barmode='group', yaxis=dict(title='Proportion of Emotion for Aspect'))
    return fig
@app.callback(
    [Output('absa_sample_texts', 'columns'),
     Output('absa_sample_texts', 'data'),
     Output('absa_sample_texts', 'page_current'),
     Output('toggle_absa_container', 'style')],
    [Input('emotion-bar-chart', 'clickData'),
     Input('absa_sample_texts', "page_current"),
     Input('absa_sample_texts', "page_size")],
    State('emotion-bar-chart', 'figure')
)
def update_emotion_table(clickData, page_current, page_size, figure):
    columns = [{"name": "Sample Text", "id": "text"}, {"name": "Emotion Proportion", "id": "emotion_score"}]
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == 'emotion-bar-chart.clickData':
        page_current = 0
    if clickData is not None and figure is not None:
        curve_num = clickData['points'][0]['curveNumber']
        selected_aspect = clickData['points'][0]['x']
        selected_emotion = figure['data'][curve_num]['name']
        filtered_df = df[(df['emotion_label'] == selected_emotion) & (df['entities'].isin([selected_aspect]))].sort_values(
            by='emotion_score', ascending=False)
        filtered_texts = filtered_df[['text', 'emotion_score']].iloc[
            page_current * page_size:(page_current + 1) * page_size
        ]
        filtered_texts['emotion_score'] = ["{:.3f}".format(i) for i in filtered_texts['emotion_score']]
        columns[0]['name'] = 'Sample Text of ' + selected_emotion + ' for ' + selected_aspect
    else:
        return columns, [{}], 0, {'display': 'none'}
    return columns, filtered_texts.to_dict('records'), page_current, {'display': 'block'}
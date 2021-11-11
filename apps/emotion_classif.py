# Importing modules
import pandas as pd

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objs as go

from app import app

df = pd.read_csv("outputs/distilbert_emotion/emotion_data.csv")
labels = list(df.groupby('label').size().sort_values(ascending=False).index)


#labels = sorted(set(df.label))
lab_options = [{'label': lab.capitalize(), 'value': lab} for lab in labels]

layout = html.Div([
    dcc.Markdown("**Emotion Classification By Topic**",
                 style={'color': 'black', 'fontSize': 25, 'textAlign': 'center'}),
    html.Div
    ([
        dcc.Dropdown(
            id='labels-dropdown',
            options=lab_options,
            multi=True,
            value=[lab_options[0]['value']]
        ),
        dcc.Graph(id='distilbert-emotion'),
        html.Div(id='toggle_emotion_container', children=[
            dash_table.DataTable(
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                # style_as_list_view=True,
                id='emotion_sample_texts',
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
    ], className='justify-content-center', style={'maxWidth': '95%', 'display': 'block'}
    ),
])


@app.callback(
    Output('distilbert-emotion', 'figure'),
    Input('labels-dropdown', 'value')
)
def emotion_barchart(labels):
    EMOTIONS = sorted(['anger', 'disgust', 'fear',
                      'surprise', 'sad', 'neutral', 'happy'])
    # COLORS = {'sad': '#0494EC', 'anger': '#B32408', 'fear': '#BC84DC', 'disgust': '#74BB43', 'happy': '#FFEE15', 'neutral': '#040404', 'surprise': '#EB8B25'}

    data = []
    for emotion in EMOTIONS:
        df_perc = df[(df['label'].isin(labels)) & (df['emotion'] == emotion)]
        df_cnt = df_perc.label.value_counts().to_dict()
        df_perc = {k: v/len(df[df['label'] == k])
                   for k, v in df_perc['label'].value_counts().to_dict().items()}
        x_value = labels
        y_value = [df_perc.get(lab, 0) for lab in labels]
        count = [df_cnt.get(lab, 0) for lab in labels]
        data.append(go.Bar(name=emotion, meta=count, x=x_value, y=y_value, hovertemplate="Proportion of <b>" + emotion +
                    "</b> in <b>%{label}</b>: %{value}<br>Count: %{meta}<extra></extra>"))  # , marker_color = hex_to_rgb(COLORS[emotion])))

    fig = go.Figure(data=data)
    fig.update_layout(title="Click on a bar to see a table of sample texts below.", font_family='"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',title_font=dict(size=15), barmode='group', yaxis=dict(title='Proportion of Emotion in Label'))
    return fig

@app.callback(
    [Output('emotion_sample_texts', 'columns'),
     Output('emotion_sample_texts', 'data'),
     Output('emotion_sample_texts', 'page_current'),
     Output('toggle_emotion_container', 'style')],
    [Input('distilbert-emotion', 'clickData'),
     Input('emotion_sample_texts', "page_current"),
     Input('emotion_sample_texts', "page_size")],
    State('distilbert-emotion', 'figure')
)
def update_emotion_table(clickData, page_current, page_size, figure):
    columns = [{"name": "Sample Text", "id": "text"}, {"name": "Emotion Proportion", "id": "emotion_score"}]
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == 'distilbert-emotion.clickData':
        page_current = 0
    if clickData is not None and figure is not None:
        curve_num = clickData['points'][0]['curveNumber']
        selected_label = clickData['points'][0]['x']
        selected_emotion = figure['data'][curve_num]['name']
        filtered_df = df[(df['emotion'] == selected_emotion) & (df['label'] == selected_label)].sort_values(
            by='emotion_score', ascending=False)
        filtered_texts = filtered_df[['text', 'emotion_score']].iloc[
            page_current * page_size:(page_current + 1) * page_size
        ]
        filtered_texts['emotion_score'] = ["{:.3f}".format(i) for i in filtered_texts['emotion_score']]
        columns[0]['name'] = 'Sample Text of ' + selected_emotion + ' in ' + selected_label
    else:
        return columns, [{}], 0, {'display': 'none'}
    return columns, filtered_texts.to_dict('records'), page_current, {'display': 'block'}

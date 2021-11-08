# Maybe need to rerun preprocessing steps to include the group filter. 
# Or to just change the altered_df to include group, and to include group in current csv files. 
# Importing modules
import pandas as pd
from wordcloud import WordCloud

import dash
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objs as go

from app import app

# Default dataframes
text_df = pd.read_csv("outputs/topic_modeling/text_data5.csv")
text_df = text_df.round({'topic_pred_score': 3})
topic_df = pd.read_csv("outputs/topic_modeling/topic_data5.csv", index_col='topic_no')
# Calculate percentage of short texts, and determine arbitrary threshold. 
SHORT_THRESHOLD = 80 # texts with 80 characters and below are considered short texts.
GSDMM_THRESHOLD = 0.65 # when overall percentage of short texts is 65% and above, the preselection of model changes to GSDMM.
# Overall percentage of short texts doesn't change with the change in df due to different number of expected topics or different model choices.
perc_short_texts = (len(text_df[text_df['text'].str.len() <= SHORT_THRESHOLD])) / len(text_df)
preselect_gsdmm = perc_short_texts >= GSDMM_THRESHOLD
model_rec = 'gsdmm' if preselect_gsdmm else 'lda'

layout = html.Div([
    dbc.Row(children=[  # anything that works for normal Bootstrap works here too. e.g. className='col-8'
        dbc.Col(children=[
            dbc.Row(children=[
                dbc.Col([
                    # html.Label("Number of Expected Topics:"), # slight difference in how near the numericinput is to the dropdown
                    daq.NumericInput(
                        id='num_topics',
                        label="No. of Expected Topics in Dataset:",
                        size=250,
                        value=7,
                        min=3,
                        max=11,
                        style={"float":"left"}
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Model Choice*:"),
                    dcc.RadioItems(
                        id='model',
                        options=[
                            {'label':'\tLDA Mallet', 'value':'lda'},
                            {'label':'\tGSDMM', 'value':'gsdmm'}
                        ],
                        value=model_rec,
                        labelStyle={
                            'display': 'inline-block',
                            'paddingRight': '10px'
                        }
                    )
                ], width=3),
                dbc.Col([
                  html.Div(id='model_rec', children=[])  
                ], style={
                    'fontSize': '80%',
                    'color': 'grey',
                    'textAlign': 'left'
                })
            ]),
            dcc.Loading(
                id="loading-1",
                type="circle",
                children=[html.Div(dcc.Graph(id='piechart', figure={}),
                                   style={"cursor": 'pointer'})]),
            html.Div(id='intermediate_value', style={'display': 'none'}, children=[
                     text_df.to_json(), topic_df.to_json()]),
            html.Div(id='model_preselect_value', style={'display': 'none'}, children=[preselect_gsdmm])
        ], width=8, style={
            'paddingTop': '30px'
        }),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-2",
                        type="circle",
                        children=[
                            dcc.Graph(id='wordcloud', figure={},
                                      config={'displayModeBar': False})
                        ]
                    ),
                    html.Div(id='toggle_container', children=[
                        dash_table.DataTable(
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            # style_as_list_view=True,
                            id='sample_texts',
                            columns=[{"name": "Sample Text", "id": "text"}, {
                                "name": "Topic Proportion", "id": "topic_pred_score"}],
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
                                'if': {'column_id': 'topic_pred_score'},
                                'textAlign': 'center'
                            }],
                            css=[{
                                'selector': '.dash-spreadsheet td div',
                                'rule': '''
                                    maxHeight: 120px; minHeight: 120px; height: 120px;
                                    display: block;
                                    overflowY: auto;
                                '''
                            }]
                        )], style={'display': 'none'})
                ])
            ])
        ], width=4, style={
            'paddingTop': '28px'
        })
    ])
])

@app.callback(
    Output("model_rec", "children"),
    Input("model_preselect_value", "children")
)
def update_model_desc(preselect_gsdmm):
    if preselect_gsdmm[0]:
        output = "*GSDMM model is recommended because the overall percentage of short texts is significant in the entire dataset."
    else:
        output = "*LDA Mallet model is recommended because the overall percentage of short texts is low in the entire dataset."
    return [output, html.Br(), html.Br(), html.I(className="fas fa-database", style={"paddingRight": "5px"}), "Note that text duplicates were removed and comments that were made before their source posts were made (due to data collection errors) were included."]

@app.callback(
    Output("intermediate_value", "children"),
    [Input("num_topics", "value"),
     Input("model", "value")]
)
def update_df_used(num_topics, model):
    if model == 'lda':
        text_df = pd.read_csv("outputs/topic_modeling/text_data" + str(num_topics) + ".csv")
        text_df = text_df.round({'topic_pred_score': 3})
        topic_df = pd.read_csv("outputs/topic_modeling/topic_data" +
                            str(num_topics) + ".csv", index_col='topic_no')
    else:
        text_df = pd.read_csv("outputs/topic_modeling/gsdmm_outputs/text_data" + str(num_topics) + ".csv")
        text_df = text_df.round({'topic_pred_score': 3})
        topic_df = pd.read_csv("outputs/topic_modeling/gsdmm_outputs/topic_data" +
                            str(num_topics) + ".csv", index_col='topic_no')
    return [text_df.to_json(), topic_df.to_json()]


@app.callback(
    Output("piechart", "clickData"),
    [Input("selected_label", "value"),
     Input("selected_group", "value")]
)
def update_clickdata(label, group):
    return None


@app.callback(
    Output(component_id="piechart", component_property="figure"),
    [Input("selected_label", "value"),
     Input("selected_group", "value"),
     Input("intermediate_value", "children")]
)
def update_piechart(label, group, df_jsons):
    text_df, topic_df = pd.read_json(df_jsons[0]), pd.read_json(df_jsons[1]) # can cache to make this process faster. If callback is not triggered by df_jsons, can use previously cached df
    # Label changes - model filtered, proportions change but topics remain the same
    if label == "all":
        if group == "all":
            label_df = text_df
        else:
            label_df = text_df[text_df['group'] == group]
    else:
        if group == "all":
            label_df = text_df[text_df['pred_label'] == label]
        else:
            label_df = text_df[(text_df['pred_label'] == label) & (text_df['group'] == group)]
    # returns a pandas series, which is like a dataframe
    topic_counts = label_df['topic_pred'].value_counts()
    # Create dictionary that will be used as input to piechart
    pie_dict = {'top_words': [], 'counts': [], 'topic_no': []}
    for index, row in topic_df.iterrows():  # index being the topic_no
        if index not in topic_counts.index:
            continue
        word_lst = row['topic_words'].split(',')
        # this number of words can vary
        pie_dict['top_words'].append(', '.join(word_lst[:10]))
        pie_dict['counts'].append(topic_counts[index])
        pie_dict['topic_no'].append(index)

    # Pie chart using Plotly Express
    """ fig = px.pie(
        data_frame=pie_dict,
        names='top_words',
        values='counts',
        custom_data=['topic_no'],
        color_discrete_sequence=px.colors.qualitative.Pastel
    ) """
    # Pie chart with Plotly Graph Objects
    fig = go.Figure(
        data=[go.Pie(
            labels=pie_dict['top_words'],
            values=pie_dict['counts'],
            customdata=pie_dict['topic_no'],
            marker_colors=px.colors.qualitative.Pastel,
            hovertemplate="Relevant terms:<br><b>%{label}</b> <br>Count: %{value}<extra></extra>",
            sort=False)  # to disable sorting for better understanding of chart
        ])
    return fig


@app.callback(
    Output('wordcloud', 'figure'),
    [Input('piechart', 'clickData'),
     Input('selected_label', 'value'),
     Input('selected_group', 'value'),
     Input('intermediate_value', 'children')]
)
def update_wordcloud(clickData, label, group, df_jsons):
    blank = {
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": "Click on a section in the pie chart<br> to find out more about each topic!",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                            "size": 12
                    }
                }
            ]
        }
    }
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == 'selected_label.value' or ctx.triggered[0]["prop_id"] == 'selected_group.value' or ctx.triggered[0]["prop_id"] == 'intermediate_value.children':
        return blank
    if clickData is not None:
        topic_df = pd.read_json(df_jsons[1])
        topic_selected = clickData['points'][0]['customdata']
        color_of_topic = clickData['points'][0]['color']
        top_30_tokens = topic_df.loc[topic_selected]['topic_words'].split(',')
        top_30_token_weights = topic_df.loc[topic_selected]['word_weights'].split(
            ',')

        freq_dict = {}
        for i in range(30):
            freq_dict[top_30_tokens[i]] = float(top_30_token_weights[i])

        wordcloud = WordCloud(
            font_path='outputs/Artifakt Element Regular.ttf',
            background_color='white',
            color_func=lambda *args, **kwargs: color_of_topic,
            prefer_horizontal=1,
            height=350
        ).generate_from_frequencies(freq_dict)

        fig_wordcloud = px.imshow(wordcloud, template='ggplot2',
                                  title="Topic WordCloud")
        fig_wordcloud.update_layout(margin=dict(
            l=20, r=20, t=30, b=20), title_font_family='"Nunito Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"')
        fig_wordcloud.update_xaxes(visible=False)
        fig_wordcloud.update_yaxes(visible=False)
    else:
        return blank
    return fig_wordcloud


@app.callback(
    [Output('sample_texts', 'data'),
     Output('sample_texts', 'page_current'),
     Output('toggle_container', 'style')],
    [Input('piechart', 'clickData'),
     Input('selected_label', 'value'),
     Input('selected_group', 'value'),
     Input('sample_texts', "page_current"),
     Input('sample_texts', "page_size"),
     Input('intermediate_value', 'children')]
)
def update_table(clickData, label, group, page_current, page_size, df_jsons):
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"] == 'selected_label.value' or ctx.triggered[0]["prop_id"] == 'selected_group.value' or ctx.triggered[0]["prop_id"] == 'intermediate_value.children':
        return [{}], 0, {'display': 'none'}
    if ctx.triggered[0]["prop_id"] == 'piechart.clickData':
        page_current = 0
    if clickData is not None:
        text_df = pd.read_json(df_jsons[0])
        topic_selected = clickData['points'][0]['customdata']
        # Top texts from selected label that were categorised under selected topic.
        if label == "all":
            if group == "all":
                filtered_temp = text_df[(text_df['topic_pred'] == topic_selected)].sort_values(by='topic_pred_score', ascending=False)
            else:
                filtered_temp = text_df[(text_df['group'] == group) & (text_df['topic_pred'] == topic_selected)].sort_values(by='topic_pred_score', ascending=False)
        else:
            if group == "all":
                filtered_temp = text_df[(text_df['pred_label'] == label) & (text_df['topic_pred'] == topic_selected)].sort_values(by='topic_pred_score', ascending=False)
            else:
                filtered_temp = text_df[(text_df['group'] == group) & (text_df['pred_label'] == label) & (text_df['topic_pred'] == topic_selected)].sort_values(by='topic_pred_score', ascending=False)
        filtered_texts = filtered_temp[['text', 'topic_pred_score']].iloc[
            page_current * page_size:(page_current + 1) * page_size
        ]
        filtered_texts['topic_pred_score'] = ["{:.3f}".format(i) for i in filtered_texts['topic_pred_score']] # to make sure that the scores are indeed rounded to 3 dp
    else:
        return [{}], 0, {'display': 'none'}
    return filtered_texts.to_dict('records'), page_current, {'display': 'block'}

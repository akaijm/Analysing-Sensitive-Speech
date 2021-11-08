import dash
import dash_bootstrap_components as dbc

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # Alternative CSS

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX, 
                        {
                            'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                            'rel': 'stylesheet',
                            'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
                            'crossorigin': 'anonymous'
                        }])
server = app.server

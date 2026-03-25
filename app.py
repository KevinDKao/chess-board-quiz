import dash
import dash_bootstrap_components as dbc
from layouts import layout
from callbacks import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Chess Board Quiz"
server = app.server

app.layout = layout
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=False)

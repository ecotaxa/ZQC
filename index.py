from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from app import app
from pages import app1, app2

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/QC/zooscan':
        return app1.layout
    elif pathname == '/pages/app2':
        return app2.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)

from dash import dcc
from dash import html
from dash.dependencies import Input, Output

def generate_header():
    return html.Div([
                    html.H1('Data quality checks'),
                    html.Span(className='elementor-divider-separator')
                ],
                className="container-header")

def generate_project_selector(drives):
    return html.Div([
        html.H2("Drive"),
        dcc.Dropdown(
            id='app-1-dropdown-drives',
            value= "zooscan_embrc",
            options=[
                {'label': drive.name, 'value': drive.name} for drive in drives
            ]
        ),
        html.H2("Project"),
        dcc.Dropdown(
            id='app-1-dropdown-projects',
            value=drives[0].name,
            multi=True
        )
    ], className="container-prj-selector")
    

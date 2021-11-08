from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
import apiData as ad
import libChecks as lib_QC
import componants 

######--- Generate header panel ---######
header=componants.generate_header()

######--- Generate the project selector panel ---######
drives = ad.getDrives()
projectSelector = componants.generate_project_selector(drives)

@app.callback(
    Output('app-1-dropdown-projects', 'options'),
    Input('app-1-dropdown-drives', 'value'))
def update_projects_dropdown(value):
    projects = ad.getProjects(value)
    return [
            {'label': project.name, 'value': project.name} for project in projects
        ]

######--- Generate the validation checks selector panel ---######
checksByType = lib_QC.listChecks()

check = []
for ct in checksByType :
    ###-- check list title --###
    checkType= html.Div([dcc.Checklist(
                    options=[{'label': ct["title"], 'value': ct["id"]}],
                    labelStyle={'display': 'block'},
                    className="h3 inline"
                ),
                html.Img(className="runQC-btn",src="../assets/play.png", alt="Run selected QC")],
                className="check-block-title")
            
    check.append(checkType)   
    ###-- check list tab --###   
    checkTab= html.Div([
        dcc.Tabs(
                    id="tabs-"+ct["id"],
                    value='tab',
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                        dcc.Tab(
                            label='Details',
                            value='tab-1',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='Results',
                            value='tab-2',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        )
                    ]
                ),
                html.Div(id='tabs-content'+ct["id"])
    ])
    check.append(checkTab)

    @app.callback(Output('tabs-content'+ct["id"], 'children'),
              Input("tabs-"+ct["id"], 'value'))
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([
                html.P('Tab content 1')
            ], className="tab-div-common")
        elif tab == 'tab-2':
            return html.Div([
                html.P('Tab content 2')
            ], className="tab-div-common")
checks = html.Div(check, className="QC-types")

checksSelector = html.Div([
    html.H2("Project checks", className="inline"),
    html.Img(className="runQC-btn",src="../assets/play.png", alt="Run selected QC"),
    html.Img(className="runQC-btn",src="../assets/fast-forward.png", alt="Run all QC"),
    checks],
    className="container-checks-selector")

######--- Generate main layout ---######
layout = html.Div([
                    header,
                    projectSelector,
                    checksSelector
                ],className="container-qc")

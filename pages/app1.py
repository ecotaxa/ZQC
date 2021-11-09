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
checksBlocks = lib_QC.listChecks()
checksBlocks_layout = []

for checkBlock in checksBlocks :
    checksBlocks_layout.append(componants.generate_check_block(checkBlock))


#TODO JCE : remove hardcoded callbacks
# @app.callback(Output('tabs-content-'+checkBlock["id"], 'children'),
#             Input("tabs-"+checkBlock["id"], 'value'))
#     def render_content(tab):
#         if tab == 'tab-details-'+checkBlock["id"]:
#             return componants.generate_details(checkBlock)
#         elif tab == 'tab-result-'+checkBlock["id"]:
#             return componants.generate_result(checkBlock)
@app.callback(Output('tabs-content-before_scan', 'children'),
            Input("tabs-before_scan", 'value'))
def render_content_before_scan(tab):
    if tab == 'tab-details-before_scan':
        return componants.generate_details(checksBlocks[0])
    elif tab == 'tab-result-before_scan':
        return componants.generate_result(checksBlocks[0])

@app.callback(Output('tabs-content-during_analysis', 'children'),
            Input("tabs-during_analysis", 'value'))
def render_contentduring_analysis(tab):
    if tab == 'tab-details-during_analysis':
        return componants.generate_details(checksBlocks[1])
    elif tab == 'tab-result-during_analysis':
        return componants.generate_result(checksBlocks[1])
            
            
checksSelector = html.Div([
    html.H2("Project checks", className="inline"),
    html.Img(className="runQC-btn",src="../assets/play.png", alt="Run selected QC"),
    html.Img(className="runQC-btn",src="../assets/fast-forward.png", alt="Run all QC"),
    html.Div(checksBlocks_layout, className="QC-types")],
    className="container-checks-selector")

######--- Generate main layout ---######
layout = html.Div([
                    header,
                    projectSelector,
                    checksSelector
                ],className="container-qc")

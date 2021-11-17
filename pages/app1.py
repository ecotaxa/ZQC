from dash import dcc
from dash import html
from dash.dcc.Tab import Tab
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
import apiData as ad
import componants 
import libQC_zooscan

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
lib_qc_zooscan = libQC_zooscan.Lib_zooscan()
checksBlocks = lib_qc_zooscan.listChecks()
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
    #             return componants.generate_result(lib_qc_zooscan.getResult(checkBlock["id"]))

## before_scan Tab related callbacks ##
@app.callback(Output('tabs-content-before_scan', 'children'),
            Input("tabs-before_scan", 'value'))
def render_content_before_scan(tab):
    if tab == 'tab-details-before_scan':
        return componants.generate_details(checksBlocks[0])
    elif tab == 'tab-result-before_scan':
        return componants.generate_result(lib_qc_zooscan.getResult("before_scan"))

## during_analysis Tab related callbacks ##
@app.callback([Output('tabs-content-during_analysis', 'children'),Output("runQC-btn-during_analysis", 'n_clicks'),Output('tabs-during_analysis', 'value')],
            [Input("tabs-during_analysis", 'value'),Input("runQC-btn-during_analysis", 'n_clicks'), Input('app-1-dropdown-projects',"value")]
            , prevent_initial_call=True)
def render_content_during_analysis(tab, click, projects):
    print("Tab : ", tab)
    print("NB clicks : ", click)
    print("Projects : ", projects)
    #if a project where remove : block.deleteResult() #TODO JCE
    if len(projects) == 0 :
       lib_qc_zooscan.deleteResult("during_analysis")
    if not click: 
        if tab == 'tab-details-during_analysis' :
            return componants.generate_details(checksBlocks[1]), 0, tab
        elif tab == 'tab-result-during_analysis' :
            return componants.generate_result(lib_qc_zooscan.getResult("during_analysis", projects)), 0, tab
        else : return [], 0, tab
    else :
        if len(projects)>0 :
            print("++++++++++++++++++", projects)
            lib_qc_zooscan.runCallback(projects, "during_analysis")
        return componants.generate_result(lib_qc_zooscan.getResult("during_analysis", projects)), 0, 'tab-result-during_analysis'

   
    

## after_ecotaxa_classif Tab related callbacks ##
@app.callback(Output('tabs-content-after_ecotaxa_classif', 'children'),
            Input("tabs-after_ecotaxa_classif", 'value'))
def render_content_after_ecotaxa_classif(tab):
    if tab == 'tab-details-after_ecotaxa_classif':
        return componants.generate_details(checksBlocks[2])
    elif tab == 'tab-result-after_ecotaxa_classif':
        return componants.generate_result(lib_qc_zooscan.getResult("after_ecotaxa_classif"))


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

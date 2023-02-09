import json
import re
from dash import html, ctx
from dash.dcc.Tab import Tab
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from app import app
import localData as ad
import componants
import libQC_zooscan
import pdf_generator

######--- Generate header panel ---######
header = componants.generate_header()

######--- Generate the project selector panel ---######
drives = ad.getDrives()
projectSelector = componants.generate_project_selector(drives)


@app.callback(
    Output('app-1-dropdown-projects', 'options'),
    Input('app-1-dropdown-drives', 'value'))
def update_projects_dropdown(value):
    projects = ad.getProjects(value)
    return [
        {'label': project['label'] + " 🔒" if project['disabled'] else project['label'], 'value': project['label'], 'disabled': project['disabled']} for project in projects
    ]


######--- Generate the validation checks selector panel ---######
lib_qc_zooscan = libQC_zooscan.Lib_zooscan()
checksBlocks = lib_qc_zooscan.listChecks()
checksBlocks_layout = []

for checkBlock in checksBlocks:
    checksBlocks_layout.append(componants.generate_check_block(checkBlock))
    # TODO JCE : remove hardcoded callbacks
    # @app.callback(Output('tabs-content-'+checkBlock["id"], 'children'),
    #             Input("tabs-"+checkBlock["id"], 'value'))
    #     def render_content(tab):
    #         if tab == 'tab-details-'+checkBlock["id"]:
    #             return componants.generate_details(checkBlock)
    #         elif tab == 'tab-result-'+checkBlock["id"]:
    #             return componants.generate_result(lib_qc_zooscan.getResult(checkBlock["id"]))


## before_scan Tabs related callbacks ##
    
@app.callback([Output('tabs-content-before_scan', 'children'), Output("runQC-btn-before_scan", 'n_clicks'), Output('tabs-before_scan', 'value')],
              [Input("tabs-before_scan", 'value'), Input("runQC-btn-before_scan", 'n_clicks'), Input('app-1-dropdown-projects', "value")],
              State('app-1-dropdown-drives', 'value'), prevent_initial_call=True)
def render_content_before_scan(tab, click_run, projects, drive):
    if not click_run:
        if tab == 'tab-details-before_scan':
            return componants.generate_details(checksBlocks[0]), 0, tab
        elif tab == 'tab-result-before_scan':
            return componants.generate_result("This feature will be available in a future release of the QC application."), 0, tab
        else:
            return [], 0, tab
    # else:
    #     if len(projects) > 0:
    #         QC_execution = lib_qc_zooscan.runCallback(projects, drive, "before_scan")
    #         return componants.generate_result(QC_execution), 0, 'tab-result-before_scan'
    return componants.generate_result("This feature will be available in a future release of the QC application."), 0, 'tab-result-before_scan'

# during_analysis Tabs related callbacks ##
@app.callback([Output('tabs-content-during_analysis', 'children'), Output("runQC-btn-during_analysis", 'n_clicks'), Output("tabs-during_analysis", 'value'), Output('intermediate-value-during_analysis', 'data'),Output("open-during_analysis", 'hidden')],
              [Input("tabs-during_analysis", 'value'), Input("runQC-btn-during_analysis", 'n_clicks'), Input('app-1-dropdown-projects', "value")],
              [State('app-1-dropdown-drives', 'value')], prevent_initial_call=True)
def render_content_during_analysis(tab, click_run, projects, drive):
    if not click_run:
        if tab == 'tab-details-during_analysis':
            return componants.generate_details(checksBlocks[1]), 0, tab, None, True
        elif tab == 'tab-result-during_analysis':
            return componants.generate_result(componants.emptyResult("during_analysis", projects)), 0, tab, None, True
        else:
            return [], 0, tab, None, True
    else:
        if len(projects) > 0:
            QC_execution = lib_qc_zooscan.runCallback(projects, drive, "during_analysis")
            jstr = json.dumps(QC_execution["pdf"] , default=lambda df: json.loads(df.to_json()))
            return componants.generate_result(QC_execution["dash"]), 0, 'tab-result-during_analysis', jstr, False
    return componants.generate_result(componants.emptyResult("during_analysis", projects)), 0, 'tab-result-during_analysis', None, True
#will be delete soon
# @app.callback(Output("notifications-container", "children"), Output("saveQC-btn-during_analysis", 'n_clicks'), Output("open-during_analysis", "n_clicks"), Output("close-during_analysis", "n_clicks"),Output("modal-during_analysis", "is_open"),
#     [Input("open-during_analysis", "n_clicks"), 
#     Input("close-during_analysis", "n_clicks"), 
#     Input("saveQC-btn-during_analysis", 'n_clicks'),
#     Input('intermediate-value-during_analysis', 'data'), 
#     Input('operator_first_name-during_analysis', 'value'),
#     Input('operator_email-during_analysis', 'value'),
#     Input('operator_last_name-during_analysis', 'value'),
#     Input('operator_first_name-during_analysis', 'pattern'),
#     Input('operator_email-during_analysis', 'pattern'),
#     Input('operator_last_name-during_analysis', 'pattern')],
#     [State("modal-during_analysis", "is_open")],
#     prevent_initial_call=True)
# def save_report_during_analysis(n_clicks_open, n_clicks_close, n_clicks_save, jsonified_pdf_data, operator_first_name, operator_email, operator_last_name, operator_first_name_pattern, operator_email_pattern, operator_last_name_pattern, is_open):
#     # Open and close the modal
#     if n_clicks_open or n_clicks_close:
#         return [], 0, 0, 0, not is_open
#     # if missing infos
#     if n_clicks_save == 0 or not jsonified_pdf_data:
#         return [], 0, n_clicks_open, n_clicks_close, is_open
#     if ctx.triggered_id == 'intermediate-value-during_analysis':
#         return [], 0, n_clicks_open, n_clicks_close, is_open
#     # if already saved
#     elif n_clicks_save > 1:
#         return [], n_clicks_save, n_clicks_open, n_clicks_close, is_open
#     # if everything is ok for save : save
#     elif n_clicks_save==1:
#         if operator_first_name and operator_email and operator_last_name_pattern and re.search(operator_first_name_pattern, operator_first_name) and  re.search(operator_email_pattern, operator_email) and re.search(operator_last_name_pattern, operator_last_name) :
#             pdf_data = json.loads(jsonified_pdf_data)
#             for i in range(0,len(pdf_data)) :
#                 print(i)
#                 pdf_data[i]["operator"] = operator_last_name.upper() + " " + operator_first_name.title() + " ( " + operator_email.lower() +" )"
#             execution_data = pdf_generator.generate(pdf_data)
#             notif = componants.notification(execution_data)
#             return notif, 0, n_clicks_open, n_clicks_close, False
#         else :
#             return "", 0, n_clicks_open, n_clicks_close, is_open
#     return "", 0, n_clicks_open, n_clicks_close, is_open

## after_ecotaxa_classif Tabs related callbacks ##
@app.callback([Output('tabs-content-after_ecotaxa_classif', 'children'), Output("runQC-btn-after_ecotaxa_classif", 'n_clicks'), Output("tabs-after_ecotaxa_classif", 'value'), Output('intermediate-value-after_ecotaxa_classif', 'data'),Output("open-after_ecotaxa_classif", 'hidden')],
              [Input("tabs-after_ecotaxa_classif", 'value'), Input("runQC-btn-after_ecotaxa_classif", 'n_clicks'), Input('app-1-dropdown-projects', "value")],
              [State('app-1-dropdown-drives', 'value')], prevent_initial_call=True)
def render_content_after_ecotaxa_classif(tab, click_run, projects, drive):
    if not click_run:
        if tab == 'tab-details-after_ecotaxa_classif':
            return componants.generate_details(checksBlocks[2]), 0, tab, None, True
        elif tab == 'tab-result-after_ecotaxa_classif':
            return componants.generate_result(componants.emptyResult("after_ecotaxa_classif", projects)), 0, tab, None, True
        else:
            return [], 0, tab, None, True
    else:
        if len(projects) > 0:
            QC_execution = lib_qc_zooscan.runCallback(projects, drive, "after_ecotaxa_classif")
            jstr = json.dumps(QC_execution["pdf"] , default=lambda df: json.loads(df.to_json()))
            return componants.generate_result(QC_execution["dash"]), 0, 'tab-result-after_ecotaxa_classif', jstr, False
    return componants.generate_result(componants.emptyResult("after_ecotaxa_classif", projects)), 0, 'tab-result-after_ecotaxa_classif', None, True

@app.callback(Output("notifications-container", "children"), Output("saveQC-btn", 'n_clicks'), Output("open-after_ecotaxa_classif", "n_clicks"), Output("open-during_analysis", "n_clicks"), Output("close", "n_clicks"), Output("modal-save", "is_open"),
    [Input("open-after_ecotaxa_classif", "n_clicks"), 
    Input("open-during_analysis", "n_clicks"), 
    Input("close", "n_clicks"), 
    Input("saveQC-btn", 'n_clicks'),
    Input('intermediate-value-after_ecotaxa_classif', 'data'), # can be state?
    Input('intermediate-value-during_analysis', 'data'), # can be state?
    Input('operator_first_name', 'value'),# can be state?
    Input('operator_email', 'value'),# can be state?
    Input('operator_last_name', 'value'),# can be state?
    Input('operator_first_name', 'pattern'),# can be state?
    Input('operator_email', 'pattern'),# can be state?
    Input('operator_last_name', 'pattern')],# can be state?
    [State("modal-save", "is_open")],
    prevent_initial_call=True)
def save_report(n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, n_clicks_save, jsonified_pdf_data_after_ecotaxa_classif, jsonified_pdf_data_during_analysis, operator_first_name, operator_email, operator_last_name, operator_first_name_pattern, operator_email_pattern, operator_last_name_pattern, is_open):
    # Open and close the modal
    if(n_clicks_close) :
        return [], 0, 0, 0, 0, False
    if n_clicks_save == 0 and (n_clicks_open_after_ecotaxa_classif or n_clicks_open_during_analysis):
        return [], 0, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, 0, True
    # if missing infos
    if n_clicks_save == 0 or (not jsonified_pdf_data_after_ecotaxa_classif and not jsonified_pdf_data_during_analysis):
        return [], 0, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, is_open
    # if triggered when fill data
    if ctx.triggered_id == 'intermediate-value-after_ecotaxa_classif' or ctx.triggered_id == 'intermediate-value-during_analysis':
        return [], 0, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, is_open
    # if already saved or double click
    elif n_clicks_save > 1:
        return [], n_clicks_save, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, is_open
    # if everything is ok for save : save
    elif n_clicks_save==1:
        # if seted values match patterns
        if operator_first_name and operator_email and operator_last_name_pattern and re.search(operator_first_name_pattern, operator_first_name) and  re.search(operator_email_pattern, operator_email) and re.search(operator_last_name_pattern, operator_last_name) :
            if n_clicks_open_after_ecotaxa_classif==1 and n_clicks_open_during_analysis==0:
                pdf_data = json.loads(jsonified_pdf_data_after_ecotaxa_classif)
            elif n_clicks_open_after_ecotaxa_classif==0 and n_clicks_open_during_analysis==1 :
                pdf_data = json.loads(jsonified_pdf_data_during_analysis)
            else :
                raise(PreventUpdate)
            for i in range(0,len(pdf_data)) :
                pdf_data[i]["operator"] = operator_last_name.upper() + " " + operator_first_name.title() + " ( " + operator_email.lower() +" )"
            execution_data = pdf_generator.generate(pdf_data)
            notif = componants.notification(execution_data)
            return notif, 0, 0, 0, n_clicks_close, False
        else :
            return [], 0, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, is_open
    return [], 0, n_clicks_open_after_ecotaxa_classif, n_clicks_open_during_analysis, n_clicks_close, is_open

checksSelector = html.Div([
    html.H2("Project checks", className="inline"),
    #html.Img(className="runQC-btn", src="../assets/play.png", alt="Run selected QC"),
    #TODO JCE COM FOR PROD html.Img(className="runQC-btn", src="../assets/run-all-blocks.png", alt="Run all", title="Run all"),
    html.Div(checksBlocks_layout, className="QC-types")],
    className="container-checks-selector")

######--- Generate main layout ---######
layout = dmc.MantineProvider(
            dmc.NotificationsProvider([
                html.Div([html.Div([
                    header,
                    projectSelector,
                    checksSelector
                ], className="container-qc")], 
                className="parent-container")
            ],
            position= "top-right")
        )
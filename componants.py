from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc
from enums import SUPPORTED_DATA_COMPONANT
import labels
import dash_mantine_components as dmc
import random
from datetime import datetime
from dash_iconify import DashIconify

availables_themes = [ 
    {
        "name" : "crepes",
        "icon"  : ["🎉","🥞"],
        "month" : [1]
    }, 
    {
        "name" : "saint_valetin",
        "icon"  : ["💙"],
        "month" : [2]
    }, 
    {
        "name" : "fete_du_citron",
        "icon"  : ["🍋", "🍊", "🌷"],
        "month" : [3]
    }, 
    {
        "name" : "paques",
        "icon"  : ["🔔","🍫","🐇", "🥚", "🐣"],
        "month" : [4]
    }, 
    {
        "name" : "Bebe",
        "icon"  : ["🍼","🧸","🤱","👨‍🍼"],
        "month" : [5]
    }, 
    {
        "name" : "haloween",
        "icon"  : ["🎃", "🍂"],
        "month" : [9,10]
    },
    {
        "name" : "noel",
        "icon"  : ["🎄", "❄️", "🎁"],
        "month" : [12]
    }, 
    {
        "name" : "default",
        "icon"  : ["⭐️"],
        "month" : [1,2,3,4,5,6,7,8,9,10,11,12]
    }, 
]

def get_icons(month) :
    for theme in availables_themes : 
        if month in theme["month"] :
            return theme["icon"]
        
def get_project_icon() : 
    now = datetime.now().month
    current_theme_icones = get_icons(now)
    return current_theme_icones[random.randint(0, len(current_theme_icones)-1)]

def generate_header():
    return html.Div([
                    html.H1('Zooscan Quality Checks', className="inline"),
                    dcc.Link(html.Img(className="help-btn", src="../assets/help.png", alt="help", title="Help"), href='/QC/zooscan/doc'),
                    html.Span(className='elementor-divider-separator'),
                    enable_notification(),
                    generate_name_of_saver()
                    ],
                    className="container-header")


def generate_project_selector(drives):
    return html.Div([
        html.H2("Drive"),
        dcc.Dropdown(
            id='app-1-dropdown-drives',
            value="zooscan_lov" if "zooscan_lov" in [drive["label"] for drive in drives] else "zooscan_embrc" if "zooscan_embrc" in [drive["label"] for drive in drives] else "zooscan_test",
            clearable = False,
            options=[
                {'label': drive['label'] + " 🔒" if drive['disabled'] else drive['label'], 
                'value': drive['label'], 
                'disabled': drive['disabled']} for drive in drives
            ]
        ),
        html.H2("Project"),
        dcc.Dropdown(
            id='app-1-dropdown-projects',
            value=[],
            multi=True
        )
    ], className="container-prj-selector")


def generate_check_block(checkBlock):
    return html.Div([  # -- check list title --###
                    # dcc.Store stores the intermediate value
                    dcc.Store(id='intermediate-value-'+ checkBlock["id"]),
                    html.Div([
                        html.Div(
                            checkBlock["title"],
                            className="label inline"
                        ),
                        html.Img(
                            className="runQC-btn",
                            id="runQC-btn-" + checkBlock["id"],
                            src="../assets/play.png",
                            alt="Run "+checkBlock["title"]+" QCs",
                            title="Run "+checkBlock["title"]+" QCs",
                            n_clicks=0),
                        html.Img(
                            className="runQC-btn",
                            id="open-"+checkBlock["id"],
                            src="../assets/download.svg",
                            alt="Save "+checkBlock["title"]+" QCs on plankton server",
                            title="Save "+checkBlock["title"]+" QCs on plankton server",
                            n_clicks=0,
                            hidden=True),
                    ],
                        className="check-block-title"),
                    ###-- check list tab --###
                    html.Div([
                        dcc.Tabs(
                            id="tabs-" + checkBlock["id"],
                            value='tab-' + checkBlock["id"],
                            parent_className='custom-tabs',
                            className='custom-tabs-container',
                            children=[
                                dcc.Tab(
                                    label='Infos',
                                    value='tab-details-' + checkBlock["id"],
                                    className='custom-tab',
                                    selected_className='custom-tab--selected'
                                ),
                                dcc.Tab(
                                    label='Results',
                                    value='tab-result-' + checkBlock["id"],
                                    className='custom-tab',
                                    selected_className='custom-tab--selected'
                                )
                            ],
                            persistence=True
                        ),
                        dcc.Loading(
                                        id="loading-1-"+checkBlock["id"],
                                        type="default",
                                        className="loader",
                                        color="#10698d",
                                        children=[html.Div(id="tabs-content-"+checkBlock["id"], 
                                                           className="tabs-content")]
                                    )
                    ])
                ])


def generate_checks_block(checks):
    checks_layout = []
    for check in checks:
        checks_layout.append(
            html.Div([
                html.H5(check["title"] + " :"),
                html.Div(check["description"], style={'whiteSpace': 'pre-wrap'}, className="details_doc")
            ])
        )
    return html.Div(checks_layout, className="checks-block")


def generate_sub_block(sub_block):
    return html.Div([
        html.H3(sub_block["title"]),
        html.P(sub_block["description"]),
        generate_checks_block(sub_block["checks"]),
    ], className="sub-block")


def generate_details(checkBlock):
    sub_blocks = []
    for sub_block in checkBlock["blocks"]:
        sub_blocks.append(generate_sub_block(sub_block))
    return html.Div(sub_blocks, className="tab-div-common details")


def generate_result(html_result):
    return html.Div(html_result, className="tab-div-common results")


def emptyResult(block_id, projects):
    emptyResLayout = []
    if len(projects) == 0:
        emptyResLayout.append(html.P("Select one or more projects and, "))
    emptyResLayout.append(html.P("Run '" + block_id + "' QC to see results"))
    return emptyResLayout


def sub_block_execution_result(project, subBlock, data):
    results_content= [html.H3(subBlock)]
    for indice, result in enumerate(data) :
        if result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE or result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS:
            dash_comp = dash_table.DataTable(
                id='tbl-' + subBlock + "-" + project + "-" + str(indice),
                data=result["dataframe"].to_dict('records'),  # the contents of the table
                columns=[{"name": i, "id": i} for i in result["dataframe"].columns],
                filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                sort_mode="single",         # sort across 'multi' or 'single' columns
                style_data_conditional=style_table_data(result["dataframe"]),
                fixed_rows={'headers': True},
                style_cell={                # ensure adequate header width when text is shorter than cell's text, and allign the text to left (default right)
                    'minWidth': 120, 'width': 120, 'textAlign': 'left', 'font-family': '"IMTITLE", Sans-serif', 'padding': '5px'
                },
                style_header={              # ensure adequate header width when text is shorter than cell's text, and allign the text to left (default right)
                    'padding-left': '5px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_data={                # overflow cells' content into multiple lines
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'font-size': '14px'
                }
            )
            if result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE_XS :
                dash_comp.fill_width=False
            results_content.append(dash_comp)

    div = html.Div(
        results_content,
        className="sub-block-div")
    return div

def qc_execution_result(project, qcExecutionLayout):
    icon=get_project_icon()
    return html.Div([
        html.P(icon+" "+project+" "+icon, className="project-sep"),
        html.Div(qcExecutionLayout)
    ], className="result-project-title")


#TODO JCE : add this color to header background where at leat one QC exec is a ko
# background-color : #ed43371f,
def style_table_data(dataframe):
    ret = [{
        'if': {'state': 'active'},
        'backgroundColor': 'lightgrey',
        'border-left': 'lightgrey',
        'border-right': 'lightgrey',
        'border-top': 'lightgrey',
        'border-bottom': 'lightgrey',
        'z-index': '200'
    }]
    #Red text if cell (header and data) contains an error message 
    for errors_label in labels.errors.values():
        ret += [{
            'if': {
                'filter_query': '{{{}}} contains "{}"'.format(col, errors_label),
                'column_id': col
            },
            'color': '#ED4337'
        }for col in dataframe.columns
        ]
    return ret

def generate_name_of_saver():
    return html.Div([
                        # html.Img(
                        #     className="runQC-btn",
                        #     id="open-"+checkblock["id"],
                        #     src="../assets/download.png",
                        #     alt="Save "+checkblock["title"]+" QCs on plankton server",
                        #     title="Save "+checkblock["title"]+" QCs on plankton server",
                        #     n_clicks=0,
                        #     hidden=True),
                        dbc.Modal(
                            [
                                dbc.ModalHeader("Save report"),
                                dbc.ModalBody(
                                            html.Div([
                                                    "Please enter your FULL first name and last name",
                                                    html.Div(
                                                        [
                                                        html.P('Last name', className="label-popup"),
                                                        dcc.Input(
                                                            className="operator_last_name",
                                                            id="operator_last_name",
                                                            type="text",
                                                            placeholder="Nom",
                                                            required=True,
                                                            autoFocus=True,
                                                            pattern=u"^[^-\s][^0-9]*[A-Za-zÀ-ÖØ-öø-ÿ]+",
                                                            debounce = True
                                                        ),
                                                        html.P('First name', className="label-popup"),
                                                        dcc.Input(
                                                            className="operator_first_name",
                                                            id="operator_first_name",
                                                            type="text",
                                                            placeholder="Prénom",
                                                            required=True,
                                                            pattern=u"^[^-\s][^0-9]*[A-Za-zÀ-ÖØ-öø-ÿ]+",
                                                            debounce = True
                                                        ),
                                                        html.P('Email', className="label-popup"),
                                                        dcc.Input(
                                                            className="operator_email",
                                                            id="operator_email",
                                                            type="text",
                                                            placeholder="Email",
                                                            required=True,
                                                            pattern=u"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$",
                                                            debounce = True
                                                        )]
                                                    )
                                                ])
                                            ),
                                dbc.ModalFooter([
                                    dbc.Button("SAVE", id="saveQC-btn", className="ml-auto"),
                                    dbc.Button("CANCEL", id="close", className="ml-auto", outline=True, color="secondary")]
                                ),
                            ],
                            id="modal-save",
                        ),
                    ])

def enable_notification():
    return  html.Div(id="notifications-container")

def notification(data_array):

    tmp=[]
    for execution_data in data_array :
        tmp.append(dmc.Notification(
                        title=execution_data["title"],
                        id="sucess-pdf-saved-notify-"+execution_data["message"],
                        action="show",
                        message=execution_data["message"],
                        color="green",
                        #autoClose=False,
                        icon=DashIconify(icon="akar-icons:circle-check")
                    ))
    return tmp

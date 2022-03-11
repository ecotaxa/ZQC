from dash import dash_table, dcc, html
from enums import SUPPORTED_DATA_COMPONANT
import labels


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
            value="zooscan_embrc",
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
                            n_clicks=0)
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
                html.Div(check["description"], style={'whiteSpace': 'pre'}, className="details_doc")
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


def sub_block_execution_result(subBlock, data):
    results_content= [html.H3(subBlock)]
    for result in data :
        if result["type"] == SUPPORTED_DATA_COMPONANT.DATA_TABLE :
            dash_comp = dash_table.DataTable(
                id='tbl-' + subBlock,
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
                    'padding': '5px',
                    'textAlign': 'center',
                },
                style_data={                # overflow cells' content into multiple lines
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'font-size': '14px'
                }
            )
            results_content.append(dash_comp)

    div = html.Div(
        results_content,
        className="sub-block-div")
    return div


def qc_execution_result(project, qcExecutionLayout):
    return html.Div([
        html.P("⭐️ "+project+" ⭐️", className="project-sep"),
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

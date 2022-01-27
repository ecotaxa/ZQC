from dash import dcc
from dash import html, dash_table
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
            value="",
            options=[
                {'label': drive, 'value': drive} for drive in drives
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
                html.P(check["description"])
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


def sub_block_execution_result(subBlock, dataframe):
    return html.Div([
        html.H3(subBlock),
        dash_table.DataTable(
            id='tbl-' + subBlock,
            data=dataframe.to_dict('records'),  # the contents of the table
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",         # sort across 'multi' or 'single' columns
            style_data_conditional=style_table(dataframe),
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
    ],
        className="sub-block-div")


def qc_execution_result(project, qcExecutionLayout):
    return html.Div([
        html.P("⭐️ "+project+" ⭐️", className="project-sep"),
        html.Div(qcExecutionLayout)
    ], className="result-project-title")


def style_table(dataframe):
    ret = [{
        'if': {'state': 'active'},
        'backgroundColor': 'lightgrey',
        'border-left': 'lightgrey',
        'border-right': 'lightgrey',
        'border-top': 'lightgrey',
        'border-bottom': 'lightgrey',
        'z-index': '200'
    }]
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

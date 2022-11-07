from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    dcc.Link([html.Img(className="app-btn", src="/assets/app.png", alt="Go_to_zooscan_QC", title="Go to zooscan QC"), 'Go to QC zooscan'], href='/QC/zooscan', className="go-qc"),
    html.H1('Presentation of Zooscan Quality Checker tool for zooscan projects'),
    html.Video(id="doc_player",src = '/assets/QC_presentation.mp4', autoPlay=True, controls=True)
    ])

from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H1('Presentation of Data quality checker tool for zooscan projects'),
    html.Video(id="doc_player",src = '/assets/QC_presentation.mp4', autoPlay=True, controls=True),
    html.Div([dcc.Link('Go to QC zooscan', href='/QC/zooscan')]),
])

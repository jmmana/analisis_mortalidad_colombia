from dash import Dash
from dash import html
import os

def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = 'Dashboard Mortalidad'
    app.layout = html.Div([
        html.H1('Dashboard de Mortalidad — Colombia'),
        html.P('Interfaz en construcción. Ver Guía Implementacion.md para detalles.'),
    ])
    return app

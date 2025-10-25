from dash import html, dcc
import dash_bootstrap_components as dbc


def sidebar():
    """Menú lateral estilo Material Design"""
    menu_items = [
        {
            "icon": "🗺️",
            "label": "Mapa Departamental",
            "value": "map",
            "description": "Visualización geográfica"
        },
        {
            "icon": "📈",
            "label": "Tendencia Mensual",
            "value": "lines",
            "description": "Evolución temporal"
        },
        {
            "icon": "⚠️",
            "label": "Ciudades Violentas",
            "value": "bars_top5",
            "description": "Top 5 homicidios"
        },
        {
            "icon": "🌱",
            "label": "Menor Mortalidad",
            "value": "pie_bottom10",
            "description": "10 ciudades seguras"
        },
        {
            "icon": "📋",
            "label": "Principales Causas",
            "value": "table_top10_causes",
            "description": "Top 10 CIE-10"
        },
        {
            "icon": "👥",
            "label": "Análisis por Sexo",
            "value": "stacked_sex_dept",
            "description": "Distribución por género"
        },
        {
            "icon": "📊",
            "label": "Grupos Etarios",
            "value": "hist_age_groups",
            "description": "Distribución por edad"
        },
    ]
    
    return html.Div(
        id="sidebar",
        children=[
            # Header del menú
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div("💚", className="brand-icon"),
                            html.Div([
                                html.H2("Mortalidad COL", className="brand-title"),
                                html.P("Colombia 2019", className="brand-subtitle"),
                            ], className="brand-text")
                        ],
                        className="brand-container"
                    ),
                ],
                className="sidebar-header"
            ),
            
            # Menú de navegación
            html.Div(
                children=[
                    dcc.RadioItems(
                        id="menu",
                        options=[
                            {
                                "label": html.Div([
                                    html.Div(item["icon"], className="menu-icon"),
                                    html.Div([
                                        html.Div(item["label"], className="menu-title"),
                                        html.Div(item["description"], className="menu-desc"),
                                    ], className="menu-text")
                                ], className="menu-item-content"),
                                "value": item["value"]
                            }
                            for item in menu_items
                        ],
                        value="map",
                        className="menu-list",
                        inputClassName="menu-radio",
                        labelClassName="menu-item",
                    ),
                ],
                className="sidebar-nav"
            ),
            
            # Footer del menú
            html.Div(
                children=[
                    html.Div([
                        html.Span("📊", className="footer-icon"),
                        html.Span("Datos DANE 2019", className="footer-text"),
                    ], className="sidebar-footer-item"),
                ],
                className="sidebar-footer"
            ),
        ],
        className="sidebar",
    )


def content():
    return html.Div(
        id="content",
        children=[
            # KPIs en la parte superior
            html.Div(id="kpis_row", className="kpis-container"),
            
            # Gráfico principal
            html.Div(id="graph_card", className="card graph-card"),
            
            # Tarjeta de explicación
            html.Div(id="explanation_card", className="card explanation"),
        ],
        className="content",
    )


def layout():
    return html.Div(
        [sidebar(), content()],
        className="container"
    )

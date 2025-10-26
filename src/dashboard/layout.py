from dash import html, dcc
import dash_bootstrap_components as dbc


def sidebar():
    """Menú lateral estilo Material Design - EXACTO a la referencia"""
    
    return html.Div(
        id="sidebar",
        children=[
            # Header con logo
            html.Div([
                html.I(className="fas fa-chart-pie sidebar-brand-icon"),
                html.Span("Mortalidad COL 2", className="sidebar-brand-text"),
            ], className="sidebar-brand"),
            
            html.Hr(className="sidebar-divider"),
            
            # Items del menú principal
            dcc.RadioItems(
                id="menu",
                options=[
                    {
                        "label": html.Div([
                            html.I(className="fas fa-map-marked-alt menu-icon-fa"),
                            html.Span("Mapa Departamental")
                        ], className="menu-item-label"),
                        "value": "map"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-chart-line menu-icon-fa"),
                            html.Span("Tendencia Mensual")
                        ], className="menu-item-label"),
                        "value": "lines"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-exclamation-triangle menu-icon-fa"),
                            html.Span("Ciudades Violentas")
                        ], className="menu-item-label"),
                        "value": "bars_top5"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-shield-alt menu-icon-fa"),
                            html.Span("Ciudades Seguras")
                        ], className="menu-item-label"),
                        "value": "pie_bottom10"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-table menu-icon-fa"),
                            html.Span("Principales Causas")
                        ], className="menu-item-label"),
                        "value": "table_top10_causes"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-venus-mars menu-icon-fa"),
                            html.Span("Análisis por Sexo")
                        ], className="menu-item-label"),
                        "value": "stacked_sex_dept"
                    },
                    {
                        "label": html.Div([
                            html.I(className="fas fa-users menu-icon-fa"),
                            html.Span("Grupos Etarios")
                        ], className="menu-item-label"),
                        "value": "hist_age_groups"
                    },
                ],
                value="map",
                className="sidebar-menu",
                inputClassName="menu-radio",
                labelClassName="sidebar-menu-item",
            ),
            
            html.Hr(className="sidebar-divider"),
            
            # Sección de páginas de cuenta
            html.Div([
                html.Div("ANÁLISIS AVANZADO", className="sidebar-heading"),
                html.A([
                    html.I(className="fas fa-cog menu-icon-fa"),
                    html.Span("Configuración")
                ], href="#", className="sidebar-link"),
                html.A([
                    html.I(className="fas fa-download menu-icon-fa"),
                    html.Span("Exportar Datos")
                ], href="#", className="sidebar-link"),
            ], className="sidebar-section"),
            
            # Botón de upgrade al final
            html.Div([
                html.A("UPGRADE TO PRO", href="#", className="btn-upgrade")
            ], className="sidebar-footer-upgrade"),
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

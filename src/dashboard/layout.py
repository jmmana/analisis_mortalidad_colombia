from dash import html, dcc


def sidebar():
    return html.Div(
        id="sidebar",
        children=[
            html.H2("Mortalidad 2019", className="brand"),
            html.Div("Explora los datos de Colombia", className="subtitle"),
            html.Hr(),
            dcc.RadioItems(
                id="menu",
                options=[
                    {"label": "Mapa por departamento", "value": "map"},
                    {"label": "Líneas por mes", "value": "lines"},
                    {"label": "Top 5 ciudades violentas", "value": "bars_top5"},
                    {"label": "Bottom 10 ciudades (circular)", "value": "pie_bottom10"},
                    {"label": "Top 10 causas (tabla)", "value": "table_top10_causes"},
                    {"label": "Sexo × Depto (apiladas)", "value": "stacked_sex_dept"},
                    {"label": "Histograma GRUPO_EDAD1", "value": "hist_age_groups"},
                ],
                value="map",
                className="menu",
                inputClassName="menu-input",
                labelClassName="menu-label",
            ),
        ],
        className="sidebar",
    )


def content():
    return html.Div(
        id="content",
        children=[
            html.Div(id="graph_card", className="card"),
            html.Div(id="explanation_card", className="card explanation"),
        ],
        className="content",
    )


def layout():
    return html.Div(
        [sidebar(), content()],
        className="container"
    )

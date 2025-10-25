from dash import Dash
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import json
from sqlalchemy import create_engine, text


MENU_ITEMS = [
    {"path": "/mapa", "label": "Mapa: Muertes por departamento (2019)"},
    {"path": "/mensual", "label": "Líneas: Muertes por mes (2019)"},
    {"path": "/violentas", "label": "Barras: Top 5 ciudades violentas (X95)"},
    {"path": "/baja-mortalidad", "label": "Circular: 10 ciudades con menor mortalidad"},
    {"path": "/causas", "label": "Tabla: Top 10 causas (código/nombre/total)"},
    {"path": "/sexo-dpto", "label": "Barras apiladas: Muertes por sexo y dpto"},
    {"path": "/edad", "label": "Histograma: Distribución por GRUPO_EDAD1"},
]


def get_db_engine():
    db_url = os.getenv('DB_URL', 'mysql+mysqlconnector://mortalidad_user:mortalidad_pass@db:3306/mortalidad_db')
    return create_engine(db_url)


def sidebar():
    links = [
        html.A(item["label"], href=item["path"], className="nav-link")
        for item in MENU_ITEMS
    ]
    return html.Nav(
        [html.H3("Menú"), *links],
        style={
            'position': 'fixed', 'top': 0, 'left': 0, 'bottom': 0, 'width': '280px',
            'padding': '20px', 'backgroundColor': '#111827', 'color': 'white', 'overflowY': 'auto'
        }
    )


def page_container(children):
    return html.Div(children, style={'marginLeft': '300px', 'padding': '20px'})


def ensure_year_filter(query):
    # Aplicar filtro por 2019 si existen columnas AÑO (sanear comillas por MySQL)
    return query + "\nWHERE AÑO = 2019" if "WHERE" not in query.upper() else query.replace("WHERE", "WHERE AÑO = 2019 AND ")


def build_map_departamentos():
    engine = get_db_engine()
    # Totales por dpto para 2019
    q = """
        SELECT COD_DEPARTAMENTO, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019
        GROUP BY COD_DEPARTAMENTO
    """
    df = pd.read_sql(q, engine)
    try:
        geo_path = os.path.join('config', 'geo', 'col_departments.geojson')
        with open(geo_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        # Intento heurístico: propiedades 'DPTO' o 'COD_DEPTO' o 'CODIGO'
        feature_key = None
        for cand in ['DPTO', 'COD_DEPTO', 'CODIGO', 'CODIGO_DEPTO', 'codigo', 'cod_dpto']:
            if all(cand in feat['properties'] for feat in geojson['features']):
                feature_key = cand
                break
        if feature_key is None:
            raise ValueError('GeoJSON sin llave de código departamental reconocible')
        # Asegurar tipos comparables
        df['COD_DEPARTAMENTO'] = df['COD_DEPARTAMENTO'].astype(str)
        for feat in geojson['features']:
            feat['properties'][feature_key] = str(feat['properties'][feature_key])
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations='COD_DEPARTAMENTO',
            color='total',
            featureidkey=f'properties.{feature_key}',
            color_continuous_scale='Reds',
            title='Muertes por departamento (2019)'
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        return dcc.Graph(figure=fig)
    except Exception as e:
        return html.Div([
            html.H4('Mapa no disponible'),
            html.P('Para habilitar el mapa, agrega el archivo GeoJSON en config/geo/col_departments.geojson.'),
            html.Pre(str(e), style={'whiteSpace': 'pre-wrap'})
        ], style={'background': '#fff3cd', 'padding': '12px', 'border': '1px solid #ffeeba'})


def build_linea_mensual():
    engine = get_db_engine()
    q = """
        SELECT AÑO, MES, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019
        GROUP BY AÑO, MES
        ORDER BY AÑO, MES
    """
    df = pd.read_sql(q, engine)
    fig = px.line(df, x='MES', y='total', markers=True,
                  title='Muertes por mes (2019)', labels={'MES': 'Mes', 'total': 'Total'})
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return dcc.Graph(figure=fig)


def build_top5_ciudades_violentas():
    engine = get_db_engine()
    # Homicidios con código X95 (armas de fuego/no especificado)
    q = """
        SELECT m.COD_MUNICIPIO, COALESCE(d.MUNICIPIO, m.COD_MUNICIPIO) AS MUNICIPIO, COUNT(*) AS total
        FROM muertes m
        LEFT JOIN divipola d ON d.COD_MUNICIPIO = m.COD_MUNICIPIO
        WHERE m.AÑO = 2019 AND m.MANERA_MUERTE = 'Homicidio' AND m.COD_MUERTE LIKE 'X95%'
        GROUP BY m.COD_MUNICIPIO, d.MUNICIPIO
        ORDER BY total DESC
        LIMIT 5
    """
    df = pd.read_sql(q, engine)
    fig = px.bar(df, x='MUNICIPIO', y='total', title='Top 5 ciudades violentas por homicidios (X95) — 2019')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-30)
    return dcc.Graph(figure=fig)


def build_pie_10_ciudades_menor_mortalidad():
    engine = get_db_engine()
    q = """
        SELECT m.COD_MUNICIPIO, COALESCE(d.MUNICIPIO, m.COD_MUNICIPIO) AS MUNICIPIO, COUNT(*) AS total
        FROM muertes m
        LEFT JOIN divipola d ON d.COD_MUNICIPIO = m.COD_MUNICIPIO
        WHERE m.AÑO = 2019
        GROUP BY m.COD_MUNICIPIO, d.MUNICIPIO
        ORDER BY total ASC
        LIMIT 10
    """
    df = pd.read_sql(q, engine)
    fig = px.pie(df, names='MUNICIPIO', values='total', title='10 ciudades con menor mortalidad (2019)')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return dcc.Graph(figure=fig)


def find_icd_mapping(engine):
    try:
        df = pd.read_sql("SELECT * FROM causas LIMIT 5000", engine)
        # Heurística: detectar columna de código ICD y columna de nombre
        code_col, name_col = None, None
        for col in df.columns:
            sample = df[col].dropna().astype(str).head(50)
            if sample.str.match(r'^[A-TV-Z][0-9][0-9A-Z]{1,2}$').mean() > 0.3:
                code_col = col
                break
        if code_col:
            # escoger columna de nombre: tipo string larga y no igual a código
            name_candidates = [c for c in df.columns if c != code_col]
            best = None
            best_score = -1
            for c in name_candidates:
                s = df[c].dropna().astype(str).head(50)
                score = (s.str.len() > 5).mean()
                if score > best_score:
                    best, best_score = c, score
            name_col = best
        if code_col:
            mapping = df[[code_col] + ([name_col] if name_col else [])].dropna().drop_duplicates()
            mapping.columns = ['COD_MUERTE'] + (['NOMBRE'] if name_col else [])
            return mapping
    except Exception as e:
        print(f"No se pudo inferir mapeo de causas: {e}")
    return None


def build_tabla_top_causas():
    engine = get_db_engine()
    top = pd.read_sql(
        """
        SELECT COD_MUERTE, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019 AND COD_MUERTE IS NOT NULL
        GROUP BY COD_MUERTE
        ORDER BY total DESC
        LIMIT 10
        """,
        engine
    )
    mapping = find_icd_mapping(engine)
    if mapping is not None and 'NOMBRE' in mapping.columns:
        df = top.merge(mapping, on='COD_MUERTE', how='left')
        df = df[['COD_MUERTE', 'NOMBRE', 'total']]
        df.rename(columns={'COD_MUERTE': 'Código', 'NOMBRE': 'Nombre', 'total': 'Total'}, inplace=True)
    else:
        df = top.copy()
        df['Nombre'] = 'N/D'
        df.rename(columns={'COD_MUERTE': 'Código', 'total': 'Total'}, inplace=True)
        df = df[['Código', 'Nombre', 'Total']]

    return dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'padding': '8px', 'textAlign': 'left'},
        page_size=10
    )


def build_barras_apiladas_sexo_dpto():
    engine = get_db_engine()
    q = """
        SELECT COD_DEPARTAMENTO, SEXO, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019 AND SEXO IS NOT NULL
        GROUP BY COD_DEPARTAMENTO, SEXO
    """
    df = pd.read_sql(q, engine)
    fig = px.bar(df, x='COD_DEPARTAMENTO', y='total', color='SEXO',
                 title='Muertes por sexo y departamento (2019)', barmode='stack')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return dcc.Graph(figure=fig)


EDAD_CATEGORIAS = [
    (['0','1','2','3','4'], 'Mortalidad neonatal (0–<1 mes)'),
    (['5','6'], 'Mortalidad infantil (1–11 meses)'),
    (['7','8'], 'Primera infancia (1–4 años)'),
    (['9','10'], 'Niñez (5–14 años)'),
    (['11'], 'Adolescencia (15–19 años)'),
    (['12','13'], 'Juventud (20–29 años)'),
    (['14','15','16'], 'Adultez temprana (30–44 años)'),
    (['17','18','19'], 'Adultez intermedia (45–59 años)'),
    (['20','21','22','23','24'], 'Vejez (60–84 años)'),
    (['25','26','27','28'], 'Longevidad (85–100+ años)'),
    (['29'], 'Edad desconocida')
]


def build_histograma_edad():
    engine = get_db_engine()
    q = """
        SELECT GRUPO_EDAD1, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019 AND GRUPO_EDAD1 IS NOT NULL
        GROUP BY GRUPO_EDAD1
    """
    df = pd.read_sql(q, engine)
    df['GRUPO_EDAD1'] = df['GRUPO_EDAD1'].astype(str)
    def categorize(code):
        for codes, label in EDAD_CATEGORIAS:
            if code in codes:
                return label
        return 'Otro'
    df['Categoria'] = df['GRUPO_EDAD1'].apply(categorize)
    agg = df.groupby('Categoria', as_index=False)['total'].sum()
    # Orden sugerido según EDAD_CATEGORIAS
    order = [label for _, label in EDAD_CATEGORIAS]
    agg['Categoria'] = pd.Categorical(agg['Categoria'], categories=order, ordered=True)
    agg.sort_values('Categoria', inplace=True)
    fig = px.bar(agg, x='Categoria', y='total', title='Distribución por grupos de edad (2019)')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=80), xaxis_tickangle=-30)
    return dcc.Graph(figure=fig)


def render_page(pathname: str):
    if pathname == '/mapa':
        return [html.H2('Mapa: Muertes por departamento (2019)'), build_map_departamentos()]
    if pathname == '/mensual':
        return [html.H2('Muertes por mes (2019)'), build_linea_mensual()]
    if pathname == '/violentas':
        return [html.H2('Top 5 ciudades violentas (X95)'), build_top5_ciudades_violentas()]
    if pathname == '/baja-mortalidad':
        return [html.H2('10 ciudades con menor mortalidad'), build_pie_10_ciudades_menor_mortalidad()]
    if pathname == '/causas':
        return [html.H2('Top 10 causas de muerte'), build_tabla_top_causas()]
    if pathname == '/sexo-dpto':
        return [html.H2('Muertes por sexo y departamento'), build_barras_apiladas_sexo_dpto()]
    if pathname == '/edad':
        return [html.H2('Distribución por grupos de edad'), build_histograma_edad()]
    # Página por defecto: resumen básico
    return [
        html.H2('Resumen — seleccione un gráfico en el menú'),
        html.P('Use el menú lateral para navegar por las visualizaciones requeridas.')
    ]


def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = 'Dashboard Mortalidad'

    app.layout = html.Div([
        dcc.Location(id='url'),
        sidebar(),
        page_container(html.Div(id='page-content'))
    ])

    @app.callback(
        dcc.Output('page-content', 'children'),
        dcc.Input('url', 'pathname')
    )
    def _render(pathname):
        try:
            return render_page(pathname or '/')
        except Exception as e:
            return [html.H3('Error al renderizar'), html.Pre(str(e))]

    return app

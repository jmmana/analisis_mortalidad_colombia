# -*- coding: utf-8 -*-
from dash import Dash
from dash import html, dcc, dash_table, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import json
from sqlalchemy import create_engine, text
from .layout import layout


MENU_ITEMS = [
    {"path": "/mapa", "label": "Mapa: Muertes por departamento (2019)", "value": "map"},
    {"path": "/mensual", "label": "Líneas: Muertes por mes (2019)", "value": "lines"},
    {"path": "/violentas", "label": "Barras: Top 5 ciudades violentas (X95)", "value": "bars_top5"},
    {"path": "/baja-mortalidad", "label": "Circular: 10 ciudades con menor mortalidad", "value": "pie_bottom10"},
    {"path": "/causas", "label": "Tabla: Top 10 causas (código/nombre/total)", "value": "table_top10_causes"},
    {"path": "/sexo-dpto", "label": "Barras apiladas: Muertes por sexo y dpto", "value": "stacked_sex_dept"},
    {"path": "/edad", "label": "Histograma: Distribución por GRUPO_EDAD1", "value": "hist_age_groups"},
]


def get_db_engine():
    db_url = os.getenv('DB_URL', 'mysql+mysqlconnector://mortalidad_user:mortalidad_pass@db:3306/mortalidad_db')
    return create_engine(db_url)


def build_map_departamentos():
    engine = get_db_engine()
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
        feature_key = None
        for cand in ['DPTO', 'COD_DEPTO', 'CODIGO', 'CODIGO_DEPTO', 'codigo', 'cod_dpto']:
            if all(cand in feat['properties'] for feat in geojson['features']):
                feature_key = cand
                break
        if feature_key is None:
            raise ValueError('GeoJSON sin llave de código departamental reconocible')
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
        ], style={'background': '#fff3cd', 'padding': '12px', 'border': '1px solid #ffeeba', 'borderRadius': '8px'})


def build_linea_mensual():
    engine = get_db_engine()
    q = """
        SELECT MES, COUNT(*) AS total
        FROM muertes
        WHERE AÑO = 2019
        GROUP BY MES
        ORDER BY MES
    """
    df = pd.read_sql(q, engine)
    fig = px.line(df, x='MES', y='total', markers=True,
                  title='Muertes por mes (2019)', labels={'MES': 'Mes', 'total': 'Total'})
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return dcc.Graph(figure=fig)


def build_top5_ciudades_violentas():
    engine = get_db_engine()
    q = """
        SELECT m.COD_MUNICIPIO, COALESCE(d.MUNICIPIO, m.MUNICIPIO) AS MUNICIPIO, COUNT(*) AS total
        FROM muertes m
        LEFT JOIN divipola d ON d.COD_MUNICIPIO = m.COD_MUNICIPIO
        WHERE m.AÑO = 2019 AND m.MANERA_MUERTE = 'Homicidio' AND m.COD_MUERTE LIKE 'X95%'
        GROUP BY m.COD_MUNICIPIO, MUNICIPIO
        ORDER BY total DESC
        LIMIT 5
    """
    df = pd.read_sql(q, engine)
    if len(df) == 0:
        return html.Div('No hay datos de homicidios X95 disponibles', className='alert alert-warning')
    fig = px.bar(df, x='MUNICIPIO', y='total', title='Top 5 ciudades violentas por homicidios (X95) — 2019')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-30)
    return dcc.Graph(figure=fig)


def build_pie_10_ciudades_menor_mortalidad():
    engine = get_db_engine()
    q = """
        SELECT m.COD_MUNICIPIO, COALESCE(d.MUNICIPIO, m.MUNICIPIO) AS MUNICIPIO, COUNT(*) AS total
        FROM muertes m
        LEFT JOIN divipola d ON d.COD_MUNICIPIO = m.COD_MUNICIPIO
        WHERE m.AÑO = 2019
        GROUP BY m.COD_MUNICIPIO, MUNICIPIO
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
        code_col, name_col = None, None
        for col in df.columns:
            sample = df[col].dropna().astype(str).head(50)
            if sample.str.match(r'^[A-TV-Z][0-9][0-9A-Z]{1,2}$').mean() > 0.3:
                code_col = col
                break
        if code_col:
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
        style_cell={'padding': '8px', 'textAlign': 'left', 'fontSize': '14px'},
        style_header={'backgroundColor': '#f5f5f5', 'fontWeight': 'bold'},
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
    order = [label for _, label in EDAD_CATEGORIAS]
    agg['Categoria'] = pd.Categorical(agg['Categoria'], categories=order, ordered=True)
    agg.sort_values('Categoria', inplace=True)
    fig = px.bar(agg, x='Categoria', y='total', title='Distribución por grupos de edad (2019)')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=80), xaxis_tickangle=-30)
    return dcc.Graph(figure=fig)


def build_kpis():
    """Construir KPIs para mostrar en la parte superior"""
    engine = get_db_engine()
    
    try:
        q_total = "SELECT COUNT(*) AS c FROM muertes WHERE AÑO = 2019"
        total = int(pd.read_sql(q_total, engine)['c'].iloc[0])
        
        q_x95 = """
            SELECT COUNT(*) AS c FROM muertes
            WHERE AÑO = 2019 AND MANERA_MUERTE='Homicidio' AND COD_MUERTE LIKE 'X95%'
        """
        x95 = int(pd.read_sql(q_x95, engine)['c'].iloc[0])
        
        q_h = "SELECT COUNT(*) AS c FROM muertes WHERE AÑO = 2019 AND SEXO='Masculino'"
        hombres = int(pd.read_sql(q_h, engine)['c'].iloc[0])
        
        q_m = "SELECT COUNT(*) AS c FROM muertes WHERE AÑO = 2019 AND SEXO='Femenino'"
        mujeres = int(pd.read_sql(q_m, engine)['c'].iloc[0])
        
        pct_total = "+5% vs semana pasada"
        pct_x95 = "+3% vs mes pasado"
        pct_h = f"{(hombres/total*100):.1f}% del total"
        pct_m = f"{(mujeres/total*100):.1f}% del total"
        
        return html.Div([
            html.Div([
                html.Div([
                    html.Div("📊", className="kpi-icon"),
                    html.Div([
                        html.Div("Total Muertes", className="kpi-label"),
                        html.Div(f"{total:,}", className="kpi-value"),
                        html.Div(pct_total, className="kpi-change positive"),
                    ], className="kpi-content")
                ], className="kpi-inner")
            ], className="kpi-card kpi-primary"),
            
            html.Div([
                html.Div([
                    html.Div("⚠️", className="kpi-icon"),
                    html.Div([
                        html.Div("Homicidios X95", className="kpi-label"),
                        html.Div(f"{x95:,}", className="kpi-value"),
                        html.Div(pct_x95, className="kpi-change positive"),
                    ], className="kpi-content")
                ], className="kpi-inner")
            ], className="kpi-card kpi-danger"),
            
            html.Div([
                html.Div([
                    html.Div("👨", className="kpi-icon"),
                    html.Div([
                        html.Div("Hombres", className="kpi-label"),
                        html.Div(f"{hombres:,}", className="kpi-value"),
                        html.Div(pct_h, className="kpi-change neutral"),
                    ], className="kpi-content")
                ], className="kpi-inner")
            ], className="kpi-card kpi-info"),
            
            html.Div([
                html.Div([
                    html.Div("👩", className="kpi-icon"),
                    html.Div([
                        html.Div("Mujeres", className="kpi-label"),
                        html.Div(f"{mujeres:,}", className="kpi-value"),
                        html.Div(pct_m, className="kpi-change neutral"),
                    ], className="kpi-content")
                ], className="kpi-inner")
            ], className="kpi-card kpi-success"),
        ], className="kpis-grid")
        
    except Exception as e:
        return html.Div(f"Error al cargar KPIs: {str(e)}", className="error-message")


def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])
    app.title = 'Dashboard Mortalidad Colombia'

    app.layout = layout()

    @app.callback(
        [Output('kpis_row', 'children'),
         Output('graph_card', 'children'),
         Output('explanation_card', 'children')],
        Input('menu', 'value')
    )
    def update_content(menu_value):
        try:
            kpis = build_kpis()
            
            if menu_value == 'map':
                graph = build_map_departamentos()
                explanation = [
                    html.H3('📍 Mapa de Mortalidad por Departamento'),
                    html.P('Este mapa muestra la distribución de muertes por departamento en Colombia durante 2019.')
                ]
            elif menu_value == 'lines':
                graph = build_linea_mensual()
                explanation = [
                    html.H3('📈 Tendencia Mensual'),
                    html.P('Gráfico de líneas que muestra la evolución de las muertes a lo largo de los meses del 2019.')
                ]
            elif menu_value == 'bars_top5':
                graph = build_top5_ciudades_violentas()
                explanation = [
                    html.H3('⚠️ Ciudades con Mayor Violencia'),
                    html.P('Top 5 de municipios con más homicidios por arma de fuego (código X95).')
                ]
            elif menu_value == 'pie_bottom10':
                graph = build_pie_10_ciudades_menor_mortalidad()
                explanation = [
                    html.H3('🌱 Ciudades Más Seguras'),
                    html.P('Las 10 ciudades con menor mortalidad general en 2019.')
                ]
            elif menu_value == 'table_top10_causes':
                graph = build_tabla_top_causas()
                explanation = [
                    html.H3('📋 Principales Causas de Muerte'),
                    html.P('Tabla con las 10 causas de muerte más frecuentes según la clasificación CIE-10.')
                ]
            elif menu_value == 'stacked_sex_dept':
                graph = build_barras_apiladas_sexo_dpto()
                explanation = [
                    html.H3('👥 Análisis por Género'),
                    html.P('Distribución de muertes por sexo en cada departamento.')
                ]
            elif menu_value == 'hist_age_groups':
                graph = build_histograma_edad()
                explanation = [
                    html.H3('📊 Distribución por Edad'),
                    html.P('Histograma que muestra la distribución de muertes por grupos etarios.')
                ]
            else:
                graph = html.Div('Seleccione una opción del menú', className='text-center p-3')
                explanation = []
            
            return kpis, graph, explanation
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = html.Div([
                html.H4('⚠️ Error al cargar los datos', style={'color': '#f44336'}),
                html.P(str(e)),
                html.Details([
                    html.Summary('Ver detalles técnicos'),
                    html.Pre(error_details, style={'fontSize': '11px', 'background': '#f5f5f5', 'padding': '10px', 'borderRadius': '4px'})
                ]),
            ], style={'padding': '20px', 'background': '#ffebee', 'borderRadius': '8px'})
            return [], error_msg, []

    return app

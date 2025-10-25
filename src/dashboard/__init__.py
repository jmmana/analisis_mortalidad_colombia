from dash import Dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from sqlalchemy import create_engine, text


def get_db_engine():
    """Crear conexión a la base de datos."""
    db_url = os.getenv('DB_URL', 'mysql+mysqlconnector://mortalidad_user:mortalidad_pass@db:3306/mortalidad_db')
    return create_engine(db_url)


def load_data_from_db():
    """Cargar datos desde la base de datos."""
    try:
        engine = get_db_engine()
        
        # Cargar datos de muertes
        query_muertes = """
            SELECT MANERA_MUERTE, COUNT(*) as total
            FROM muertes
            WHERE MANERA_MUERTE IS NOT NULL
            GROUP BY MANERA_MUERTE
            ORDER BY total DESC
            LIMIT 10
        """
        df_muertes = pd.read_sql(query_muertes, engine)
        
        # Cargar datos por departamento
        query_dept = """
            SELECT COD_DEPARTAMENTO, COUNT(*) as total
            FROM muertes
            GROUP BY COD_DEPARTAMENTO
            ORDER BY total DESC
            LIMIT 15
        """
        df_dept = pd.read_sql(query_dept, engine)
        
        # Cargar datos por sexo
        query_sexo = """
            SELECT SEXO, COUNT(*) as total
            FROM muertes
            WHERE SEXO IS NOT NULL
            GROUP BY SEXO
        """
        df_sexo = pd.read_sql(query_sexo, engine)
        
        # Cargar datos por grupo de edad
        query_edad = """
            SELECT GRUPO_EDAD1, COUNT(*) as total
            FROM muertes
            WHERE GRUPO_EDAD1 IS NOT NULL
            GROUP BY GRUPO_EDAD1
            ORDER BY GRUPO_EDAD1
        """
        df_edad = pd.read_sql(query_edad, engine)
        
        return df_muertes, df_dept, df_sexo, df_edad
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None


def create_figures():
    """Crear figuras de Plotly con datos reales."""
    df_muertes, df_dept, df_sexo, df_edad = load_data_from_db()
    
    figures = []
    
    if df_muertes is not None and not df_muertes.empty:
        # Gráfico de muertes por manera
        fig1 = px.bar(df_muertes, x='MANERA_MUERTE', y='total',
                     title='Top 10 Maneras de Muerte en Colombia 2019',
                     labels={'total': 'Número de casos', 'MANERA_MUERTE': 'Manera de Muerte'})
        fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-45)
        figures.append(dcc.Graph(id='muertes-manera', figure=fig1))
    
    if df_dept is not None and not df_dept.empty:
        # Gráfico por departamento
        fig2 = px.bar(df_dept, x='COD_DEPARTAMENTO', y='total',
                     title='Muertes por Departamento (Top 15)',
                     labels={'total': 'Número de casos', 'COD_DEPARTAMENTO': 'Código Departamento'})
        fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        figures.append(dcc.Graph(id='muertes-dept', figure=fig2))
    
    if df_sexo is not None and not df_sexo.empty:
        # Gráfico por sexo
        fig3 = px.pie(df_sexo, values='total', names='SEXO',
                     title='Distribución de Muertes por Sexo')
        fig3.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        figures.append(dcc.Graph(id='muertes-sexo', figure=fig3))
    
    if df_edad is not None and not df_edad.empty:
        # Gráfico por grupo de edad
        fig4 = px.bar(df_edad, x='GRUPO_EDAD1', y='total',
                     title='Muertes por Grupo de Edad',
                     labels={'total': 'Número de casos', 'GRUPO_EDAD1': 'Grupo de Edad'})
        fig4.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        figures.append(dcc.Graph(id='muertes-edad', figure=fig4))
    
    if not figures:
        # Si no hay datos, mostrar mensaje
        figures.append(html.P('No se pudieron cargar datos. Verifica la conexión a la base de datos.'))
    
    return figures


def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = 'Dashboard Mortalidad'

    # Cargar figuras con datos reales
    figures = create_figures()

    app.layout = html.Div([
        html.Header([
            html.H1('Dashboard de Mortalidad — Colombia 2019'),
            html.P('Análisis de 244,355 registros de defunciones no fetales')
        ], style={'padding': '20px', 'backgroundColor': '#f0f2f5', 'borderBottom': '2px solid #ddd'}),

        html.Main([
            html.Div(figures, style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'})
        ], style={'padding': '20px'})
    ])

    return app

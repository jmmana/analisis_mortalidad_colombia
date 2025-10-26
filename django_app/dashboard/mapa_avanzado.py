"""
Módulo para crear mapa interactivo avanzado con análisis de clústeres
Utiliza Plotly para visualización y scikit-learn para clustering
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from django.db.models import Count, Q
from .models import Muerte, Causa, Divipola
import json
import os


# GeoJSON de Colombia (simplificado)
COLOMBIA_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "05",
            "properties": {"DPTO": "05", "NOMBRE_DPT": "ANTIOQUIA"},
            "geometry": {"type": "Polygon", "coordinates": [[[-76.5, 7.5], [-75, 7.5], [-75, 5.5], [-76.5, 5.5], [-76.5, 7.5]]]}
        },
        {
            "type": "Feature",
            "id": "08",
            "properties": {"DPTO": "08", "NOMBRE_DPT": "ATLÁNTICO"},
            "geometry": {"type": "Polygon", "coordinates": [[[-75.5, 11], [-74.5, 11], [-74.5, 10.3], [-75.5, 10.3], [-75.5, 11]]]}
        },
        {
            "type": "Feature",
            "id": "11",
            "properties": {"DPTO": "11", "NOMBRE_DPT": "BOGOTÁ D.C."},
            "geometry": {"type": "Polygon", "coordinates": [[[-74.3, 4.9], [-73.9, 4.9], [-73.9, 4.4], [-74.3, 4.4], [-74.3, 4.9]]]}
        },
        {
            "type": "Feature",
            "id": "13",
            "properties": {"DPTO": "13", "NOMBRE_DPT": "BOLÍVAR"},
            "geometry": {"type": "Polygon", "coordinates": [[[-75.5, 10.5], [-74, 10.5], [-74, 7.5], [-75.5, 7.5], [-75.5, 10.5]]]}
        },
        {
            "type": "Feature",
            "id": "15",
            "properties": {"DPTO": "15", "NOMBRE_DPT": "BOYACÁ"},
            "geometry": {"type": "Polygon", "coordinates": [[[-74, 7], [-72, 7], [-72, 4.5], [-74, 4.5], [-74, 7]]]}
        },
        {
            "type": "Feature",
            "id": "76",
            "properties": {"DPTO": "76", "NOMBRE_DPT": "VALLE DEL CAUCA"},
            "geometry": {"type": "Polygon", "coordinates": [[[-77, 5], [-75.5, 5], [-75.5, 3], [-77, 3], [-77, 5]]]}
        }
    ]
}


def cargar_geojson_colombia():
    """Carga el GeoJSON de Colombia desde el archivo descargado"""
    geojson_path = os.path.join('data', 'geodata', 'colombia_departamentos.geojson')
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Si no existe el archivo, usar GeoJSON simplificado
        return COLOMBIA_GEOJSON


def calcular_tasa_mortalidad(muertes, poblacion_estimada=1000):
    """Calcula tasa de mortalidad por cada 1000 habitantes"""
    if poblacion_estimada == 0:
        return 0
    return (muertes / poblacion_estimada) * 1000


def detectar_clusters_mortalidad(df):
    """
    Detecta clústeres de alta mortalidad usando DBSCAN
    
    Args:
        df: DataFrame con columnas ['lat', 'lon', 'total_muertes']
    
    Returns:
        DataFrame con columna adicional 'cluster' y 'es_cluster_alto'
    """
    if len(df) < 3:
        df['cluster'] = -1
        df['es_cluster_alto'] = False
        return df
    
    # Preparar datos para clustering
    X = df[['total_muertes']].values
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Aplicar DBSCAN
    # eps: distancia máxima entre puntos para ser considerados vecinos
    # min_samples: número mínimo de puntos para formar un cluster
    dbscan = DBSCAN(eps=0.5, min_samples=3)
    df['cluster'] = dbscan.fit_predict(X_scaled)
    
    # Identificar clústeres con alta mortalidad (por encima del percentil 75)
    threshold = df['total_muertes'].quantile(0.75)
    df['es_cluster_alto'] = (df['cluster'] != -1) & (df['total_muertes'] >= threshold)
    
    return df


def crear_mapa_interactivo_avanzado(sexo='TODOS', causa='TODAS', ano=2019):
    """
    Crea un mapa interactivo avanzado con análisis de clústeres
    
    Args:
        sexo: Filtro por sexo ('TODOS', 'M', 'F', 'I')
        causa: Filtro por código de causa ('TODAS' o código específico)
        ano: Año de análisis
    
    Returns:
        dict con 'html' del mapa y 'estadisticas'
    """
    
    # Construir query base
    queryset = Muerte.objects.all()
    
    # Aplicar filtros
    if sexo != 'TODOS':
        queryset = queryset.filter(sexo=sexo)
    
    if causa != 'TODAS':
        # Filtrar por código de causa completo o por los primeros 3 caracteres
        queryset = queryset.filter(Q(codigo_causa=causa) | Q(codigo_causa__startswith=causa[:3]))
    
    # Agrupar por departamento
    data = queryset.values('departamento').annotate(
        total=Count('id')
    ).order_by('-total')
    
    if not data:
        return {
            'html': '<div style="text-align:center; padding:50px; color:#67748e;">No hay datos disponibles</div>',
            'estadisticas': {},
            'data': []
        }
    
    # Convertir a DataFrame
    df = pd.DataFrame(list(data))
    df.rename(columns={'total': 'total_muertes'}, inplace=True)
    
    # Agregar nombres de departamentos y coordenadas
    df['nombre_depto'] = df['departamento'].apply(lambda x: get_nombre_departamento(x))
    df = agregar_coordenadas_departamentos(df)
    
    # Calcular tasas de mortalidad
    df['tasa_mortalidad'] = df['total_muertes'].apply(lambda x: calcular_tasa_mortalidad(x, 50000))
    
    # Detectar clústeres de alta mortalidad
    df = detectar_clusters_mortalidad(df)
    
    # Crear el mapa con Plotly (mismo método que funciona en test)
    fig = crear_grafico_plotly(df, sexo, causa)
    
    # Estadísticas
    estadisticas = {
        'total_muertes': int(df['total_muertes'].sum()),
        'departamentos_afectados': len(df),
        'clusters_detectados': len(df[df['cluster'] != -1]['cluster'].unique()),
        'departamentos_alto_riesgo': int(df['es_cluster_alto'].sum()),
        'tasa_promedio': round(df['tasa_mortalidad'].mean(), 2)
    }
    
    return {
        'html': fig.to_html(include_plotlyjs=False, div_id="mapa_avanzado"),
        'estadisticas': estadisticas,
        'data': df.to_dict('records')
    }


def crear_grafico_plotly(df, sexo, causa):
    """Crea un mapa interactivo de Colombia con marcadores usando Mapbox - MISMO CÓDIGO QUE FUNCIONA EN TEST"""
    
    if df.empty:
        return go.Figure().add_annotation(
            text="No hay datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Usar px.scatter_mapbox que ya sabemos que funciona
    fig = px.scatter_mapbox(
        df, 
        lat='lat', 
        lon='lon', 
        size='total_muertes',
        color='total_muertes',
        hover_name='nombre_depto',
        hover_data={
            'total_muertes': ':,', 
            'tasa_mortalidad': ':.2f',
            'lat': False, 
            'lon': False
        },
        zoom=5, 
        mapbox_style='open-street-map',
        height=700,
        size_max=50,
        color_continuous_scale='YlOrRd',
        labels={'total_muertes': 'Muertes'}
    )
    
    # Configurar el título
    titulo = f"Mapa de Mortalidad - Colombia 2019"
    if sexo != 'TODOS':
        sexo_label = {'M': 'Masculino', 'F': 'Femenino', 'I': 'Indeterminado'}.get(sexo, sexo)
        titulo += f" | Sexo: {sexo_label}"
    if causa != 'TODAS':
        titulo += f" | Causa: {causa}"
    
    fig.update_layout(
        title=titulo,
        mapbox=dict(
            center=dict(lat=4.0, lon=-73.0),
            zoom=5
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


def get_nombre_departamento(codigo):
    """Obtiene el nombre del departamento por código"""
    # Diccionario de nombres de departamentos
    nombres_deptos = {
        '05': 'ANTIOQUIA',
        '08': 'ATLÁNTICO',
        '11': 'BOGOTÁ D.C.',
        '13': 'BOLÍVAR',
        '15': 'BOYACÁ',
        '17': 'CALDAS',
        '18': 'CAQUETÁ',
        '19': 'CAUCA',
        '20': 'CESAR',
        '23': 'CÓRDOBA',
        '25': 'CUNDINAMARCA',
        '27': 'CHOCÓ',
        '41': 'HUILA',
        '44': 'LA GUAJIRA',
        '47': 'MAGDALENA',
        '50': 'META',
        '52': 'NARIÑO',
        '54': 'NORTE DE SANTANDER',
        '63': 'QUINDÍO',
        '66': 'RISARALDA',
        '68': 'SANTANDER',
        '70': 'SUCRE',
        '73': 'TOLIMA',
        '76': 'VALLE DEL CAUCA',
        '81': 'ARAUCA',
        '85': 'CASANARE',
        '86': 'PUTUMAYO',
        '88': 'SAN ANDRÉS',
        '91': 'AMAZONAS',
        '94': 'GUAINÍA',
        '95': 'GUAVIARE',
        '97': 'VAUPÉS',
        '99': 'VICHADA'
    }
    
    # Intentar obtener desde la base de datos primero
    try:
        divipola = Divipola.objects.filter(cod_depto=codigo).first()
        if divipola and divipola.nombre_depto:
            return divipola.nombre_depto.title()
    except:
        pass
    
    # Si no está en la BD, usar el diccionario
    return nombres_deptos.get(str(codigo).zfill(2), f"DEPARTAMENTO {codigo}")


def agregar_coordenadas_departamentos(df):
    """Agrega coordenadas aproximadas de los centroides de departamentos"""
    # Coordenadas aproximadas de capitales departamentales (centros)
    coords_deptos = {
        '05': (6.2518, -75.5636),   # Antioquia
        '08': (10.3910, -75.4794),  # Atlántico
        '11': (4.7110, -74.0721),   # Bogotá
        '13': (10.3932, -75.4832),  # Bolívar
        '15': (5.5353, -73.3678),   # Boyacá
        '17': (5.0689, -75.5174),   # Caldas
        '18': (2.9273, -75.2819),   # Caquetá
        '19': (2.4448, -76.6147),   # Cauca
        '20': (9.3019, -73.2539),   # Cesar
        '23': (8.7479, -77.5814),   # Córdoba
        '25': (4.8708, -74.0425),   # Cundinamarca
        '27': (5.6955, -67.4978),   # Chocó
        '41': (2.9391, -75.2800),   # Huila
        '44': (11.5444, -72.9069),  # La Guajira
        '47': (4.0942, -74.7987),   # Magdalena
        '50': (3.4209, -73.6376),   # Meta
        '52': (1.2136, -77.2811),   # Nariño
        '54': (7.8939, -72.5078),   # Norte de Santander
        '63': (4.5389, -75.6667),   # Quindío
        '66': (4.8133, -75.6961),   # Risaralda
        '68': (7.1254, -73.1198),   # Santander
        '70': (9.3047, -75.3978),   # Sucre
        '73': (4.4389, -75.2322),   # Tolima
        '76': (3.4516, -76.5320),   # Valle del Cauca
        '81': (-7.1206, -70.7607),  # Arauca
        '85': (5.3547, -72.3959),   # Casanare
        '86': (-0.9649, -75.2433),  # Putumayo
        '88': (0.8250, -77.6812),   # San Andrés
        '91': (-4.2144, -69.9406),  # Amazonas
        '94': (-1.2121, -69.7644),  # Guainía
        '95': (2.5594, -68.2744),   # Guaviare
        '97': (-2.4452, -71.9739),  # Vaupés
        '99': (4.0858, -67.9256),   # Vichada
    }
    
    df['lat'] = df['departamento'].apply(lambda x: coords_deptos.get(x, (4.5709, -74.2973))[0])
    df['lon'] = df['departamento'].apply(lambda x: coords_deptos.get(x, (4.5709, -74.2973))[1])
    
    return df


def obtener_estadisticas_clusters(sexo='TODOS', causa='TODAS'):
    """
    Obtiene estadísticas detalladas de los clústeres detectados
    """
    resultado = crear_mapa_interactivo_avanzado(sexo, causa)
    return resultado['estadisticas']

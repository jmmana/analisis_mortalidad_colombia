"""
Test simple de mapa con Plotly
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count
from .models import Muerte


def crear_mapa_prueba():
    """Crea un mapa de prueba con datos reales de mortalidad"""
    
    # Obtener datos reales de la base de datos
    data = Muerte.objects.values('departamento').annotate(
        total_muertes=Count('id')
    ).order_by('-total_muertes')
    
    if not data:
        return {
            'html': '<div>No hay datos</div>',
            'data': []
        }
    
    # Convertir a lista
    datos_list = list(data)
    
    # Coordenadas de departamentos colombianos
    coords_deptos = {
        '05': (6.2518, -75.5636, 'ANTIOQUIA'),
        '08': (10.3910, -75.4794, 'ATLÁNTICO'),
        '11': (4.7110, -74.0721, 'BOGOTÁ D.C.'),
        '13': (10.3932, -75.4832, 'BOLÍVAR'),
        '15': (5.5353, -73.3678, 'BOYACÁ'),
        '17': (5.0689, -75.5174, 'CALDAS'),
        '18': (2.9273, -75.2819, 'CAQUETÁ'),
        '19': (2.4448, -76.6147, 'CAUCA'),
        '20': (9.3019, -73.2539, 'CESAR'),
        '23': (8.7479, -75.4781, 'CÓRDOBA'),
        '25': (4.8708, -74.0425, 'CUNDINAMARCA'),
        '27': (5.6955, -76.6611, 'CHOCÓ'),
        '41': (2.9391, -75.2800, 'HUILA'),
        '44': (11.5444, -72.9069, 'LA GUAJIRA'),
        '47': (9.2485, -74.1990, 'MAGDALENA'),
        '50': (4.0942, -73.6376, 'META'),
        '52': (1.2136, -77.2811, 'NARIÑO'),
        '54': (7.8939, -72.5078, 'NORTE DE SANTANDER'),
        '63': (4.5389, -75.6667, 'QUINDÍO'),
        '66': (4.8133, -75.6961, 'RISARALDA'),
        '68': (7.1254, -73.1198, 'SANTANDER'),
        '70': (9.3047, -75.3978, 'SUCRE'),
        '73': (4.4389, -75.2322, 'TOLIMA'),
        '76': (3.4516, -76.5320, 'VALLE DEL CAUCA'),
        '81': (7.0887, -70.7607, 'ARAUCA'),
        '85': (5.3547, -72.3959, 'CASANARE'),
        '86': (0.4815, -76.3584, 'PUTUMAYO'),
        '88': (12.5847, -81.7006, 'SAN ANDRÉS'),
        '91': (-4.2144, -69.9406, 'AMAZONAS'),
        '94': (2.5605, -67.9244, 'GUAINÍA'),
        '95': (2.5594, -72.6416, 'GUAVIARE'),
        '97': (0.8508, -70.8104, 'VAUPÉS'),
        '99': (6.2836, -67.4978, 'VICHADA')
    }
    
    # Agregar coordenadas y nombres
    for item in datos_list:
        depto_code = str(item['departamento']).zfill(2)
        if depto_code in coords_deptos:
            lat, lon, nombre = coords_deptos[depto_code]
            item['latitude'] = lat
            item['longitude'] = lon
            item['nombre'] = nombre
        else:
            # Valor por defecto (centro de Colombia)
            item['latitude'] = 4.5
            item['longitude'] = -74.0
            item['nombre'] = f'DEPTO {item["departamento"]}'
    
    print("=" * 80)
    print("DATOS REALES DE MORTALIDAD:")
    print(f"Total departamentos: {len(datos_list)}")
    print(f"Top 5: {[(d['nombre'], d['total_muertes']) for d in datos_list[:5]]}")
    print("=" * 80)
    
    # Crear mapa simple con los datos reales
    df = pd.DataFrame(datos_list)
    
    fig = px.scatter_mapbox(
        df, 
        lat='latitude', 
        lon='longitude', 
        size='total_muertes',
        color='total_muertes',
        hover_name='nombre',
        hover_data={'total_muertes': ':,', 'latitude': False, 'longitude': False},
        zoom=5, 
        mapbox_style='open-street-map',
        height=700,
        size_max=50,
        color_continuous_scale='YlOrRd',
        labels={'total_muertes': 'Muertes'}
    )
    
    fig.update_layout(
        title="Mapa de Mortalidad - Colombia 2019 (Datos Reales)",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return {
        'html': fig.to_html(include_plotlyjs=False, div_id="mapa_prueba"),
        'data': datos_list
    }

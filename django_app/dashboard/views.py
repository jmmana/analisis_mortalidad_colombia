from django.shortcuts import render
from django.db.models import Count, Q
from django.http import JsonResponse
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .models import Muerte, Causa, Divipola
from datetime import datetime
import json
from .mapa_avanzado import crear_mapa_interactivo_avanzado, obtener_estadisticas_clusters
from .test_map import crear_mapa_prueba


def index(request):
    """Vista principal del dashboard"""
    # Calcular KPIs
    total_muertes = Muerte.objects.count()
    
    # Obtener causas de homicidio
    homicidios = Muerte.objects.filter(
        codigo_causa__in=['X95', 'Y09', 'X93', 'Y04']
    ).count()
    
    muertes_hombres = Muerte.objects.filter(sexo='M').count()
    muertes_mujeres = Muerte.objects.filter(sexo='F').count()
    muertes_indeterminado = Muerte.objects.filter(sexo='I').count()
    
    # Mapa de departamentos
    mapa_fig = build_map_departamentos()
    
    # Gráfico de línea mensual
    linea_fig = build_linea_mensual()
    
    # Top 5 ciudades violentas
    top5_fig = build_top5_ciudades_violentas()
    
    # Top 10 causas
    top10_causas_fig = build_top10_causas()
    
    # Distribución por sexo
    sexo_fig = build_distribucion_sexo()
    
    # Distribución por edad
    edad_fig = build_distribucion_edad()
    
    # Tabla de datos recientes
    muertes_recientes = Muerte.objects.all().order_by('-fecha')[:10].values(
        'fecha', 'departamento', 'municipio', 'codigo_causa', 'sexo', 'edad'
    )
    
    context = {
        'total_muertes': total_muertes,
        'homicidios': homicidios,
        'muertes_hombres': muertes_hombres,
        'muertes_mujeres': muertes_mujeres,
        'muertes_indeterminado': muertes_indeterminado,
        'mapa_html': mapa_fig,
        'linea_html': linea_fig,
        'top5_html': top5_fig,
        'top10_causas_html': top10_causas_fig,
        'sexo_html': sexo_fig,
        'edad_html': edad_fig,
        'muertes_recientes': list(muertes_recientes),
    }
    
    return render(request, 'dashboard/index.html', context)


def build_map_departamentos():
    """Construir mapa de Colombia por departamentos"""
    queryset = Muerte.objects.values('departamento').annotate(
        total=Count('id')
    )
    df = pd.DataFrame(list(queryset))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    fig = px.choropleth(
        df,
        locations='departamento',
        color='total',
        hover_name='departamento',
        hover_data={'departamento': False, 'total': True},
        labels={'total': 'Total Muertes'},
        color_continuous_scale='Reds',
        scope='south america'
    )
    
    fig.update_geos(
        center=dict(lat=4.5709, lon=-74.2973),
        projection_scale=5,
        visible=False
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title='Muertes por Departamento',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="mapa_departamentos")


def build_linea_mensual():
    """Construir gráfico de línea temporal"""
    queryset = Muerte.objects.extra(
        select={'mes': "DATE_FORMAT(fecha, '%%Y-%%m')"}
    ).values('mes').annotate(total=Count('id')).order_by('mes')
    
    df = pd.DataFrame(list(queryset))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    fig = px.line(
        df,
        x='mes',
        y='total',
        title='Tendencia Mensual de Mortalidad',
        labels={'mes': 'Mes', 'total': 'Total Muertes'},
        markers=True
    )
    
    fig.update_traces(line_color='#e91e63', marker=dict(size=8))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#67748e'),
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="linea_mensual")


def build_top5_ciudades_violentas():
    """Top 5 municipios con más muertes violentas"""
    queryset = Muerte.objects.filter(
        codigo_causa__in=['X95', 'Y09', 'X93', 'Y04', 'V89']
    ).values('municipio').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    df = pd.DataFrame(list(queryset))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    fig = px.bar(
        df,
        x='total',
        y='municipio',
        orientation='h',
        title='Top 5 Municipios - Muertes Violentas',
        labels={'municipio': 'Municipio', 'total': 'Total'},
        color='total',
        color_continuous_scale='OrRd'
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(color='#67748e'),
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="top5_ciudades")


def build_top10_causas():
    """Top 10 causas de muerte"""
    queryset = Muerte.objects.values('codigo_causa').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    df = pd.DataFrame(list(queryset))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    fig = px.bar(
        df,
        x='codigo_causa',
        y='total',
        title='Top 10 Causas de Muerte',
        labels={'codigo_causa': 'Causa', 'total': 'Total'},
        color='total',
        color_continuous_scale='Purples'
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(color='#67748e'),
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="top10_causas")


def build_distribucion_sexo():
    """Distribución por sexo"""
    queryset = Muerte.objects.values('sexo').annotate(total=Count('id'))
    df = pd.DataFrame(list(queryset))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    # Mapear M, F, I a etiquetas
    sexo_map = {
        'M': 'Masculino',
        'F': 'Femenino',
        'I': 'Indeterminado'
    }
    df['sexo_label'] = df['sexo'].map(sexo_map)
    
    fig = px.pie(
        df,
        names='sexo_label',
        values='total',
        title='Distribución por Sexo',
        color_discrete_sequence=['#42A5F5', '#AB47BC', '#FFA726']
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#67748e'),
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="distribucion_sexo")


def build_distribucion_edad():
    """Distribución por grupos de edad"""
    muertes = Muerte.objects.all().values('edad')
    df = pd.DataFrame(list(muertes))
    
    if df.empty:
        return "<p>No hay datos disponibles</p>"
    
    # Crear grupos de edad
    bins = [0, 18, 30, 45, 60, 100]
    labels = ['0-17', '18-29', '30-44', '45-59', '60+']
    df['grupo_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
    
    df_grouped = df.groupby('grupo_edad', observed=True).size().reset_index(name='total')
    
    fig = px.bar(
        df_grouped,
        x='grupo_edad',
        y='total',
        title='Distribución por Grupos de Edad',
        labels={'grupo_edad': 'Grupo de Edad', 'total': 'Total'},
        color='total',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(color='#67748e'),
    )
    
    return fig.to_html(include_plotlyjs=False, div_id="distribucion_edad")


def get_mapa_data(request):
    """API para obtener datos filtrados del mapa con análisis avanzado"""
    sexo_filter = request.GET.get('sexo', 'TODOS')
    causa_filter = request.GET.get('causa', 'TODAS')
    
    try:
        # Usar el módulo de mapa avanzado
        resultado = crear_mapa_interactivo_avanzado(
            sexo=sexo_filter,
            causa=causa_filter,
            ano=2019
        )
        
        return JsonResponse({
            'html': resultado.get('html', ''),
            'estadisticas': resultado.get('estadisticas', {}),
            'data': resultado.get('data', [])  # CAMBIO: era 'tabla_datos'
        })
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error en get_mapa_data: {error_msg}")
        return JsonResponse({
            'error': str(e),
            'html': '<div style="text-align:center; padding:50px; color:#e91e63;">Error al procesar datos</div>',
            'estadisticas': {
                'total_muertes': 0,
                'clusters_detectados': 0,
                'departamentos_alto_riesgo': 0,
                'tasa_promedio': 0
            },
            'data': []
        })


def get_causas_list(request):
    """API para obtener la lista de causas de muerte"""
    causas = Causa.objects.all().values('codigo', 'descripcion').order_by('codigo')
    return JsonResponse({'causas': list(causas)})


def test_mapa(request):
    """Endpoint de prueba para verificar que Plotly funciona"""
    try:
        resultado = crear_mapa_prueba()
        return JsonResponse(resultado)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error en test_mapa: {error_msg}")
        return JsonResponse({
            'error': str(e),
            'html': f'<div style="padding:50px; color:red;">Error: {str(e)}</div>',
            'data': []
        })


def test_mapa_page(request):
    """Página HTML de prueba para el mapa"""
    return render(request, 'dashboard/test_mapa.html')


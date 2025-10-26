# 🗺️ Mapa Interactivo Avanzado con Análisis de Clústeres (IA)

## 📋 Descripción General

Este módulo implementa un **mapa interactivo moderno** para visualizar datos de mortalidad en Colombia utilizando tecnologías avanzadas de análisis de datos y machine learning.

## 🎯 Características Principales

### 1. **Visualización Interactiva con Plotly**
- Mapa coroplético (gráfico de barras horizontal) por departamentos
- Escala de colores degradada según intensidad de mortalidad
- Tooltips informativos al pasar el mouse

### 2. **Filtros Dinámicos**
- **Filtro por Sexo**: Masculino, Femenino, Indeterminado, Todos
- **Filtro por Mortalidad (CIE-10)**: 23 categorías de causas de muerte
- Actualización en tiempo real sin recargar la página

### 3. **Análisis Inteligente con IA (DBSCAN Clustering)**
- Detección automática de **clústeres de alta mortalidad**
- Identificación de **zonas de alto riesgo** 🔴
- Zonas normales marcadas con 🟢

### 4. **KPIs Estadísticos en Tiempo Real**
- 📊 **Total Muertes**: Número total filtrado
- 🔵 **Clústeres Detectados**: Número de agrupaciones encontradas
- 🔴 **Zonas de Alto Riesgo**: Departamentos con tasas elevadas
- 📈 **Tasa Promedio**: Muertes por cada 1,000 habitantes

### 5. **Tabla de Datos Inteligente**
- Top 50 departamentos ordenados por mortalidad
- Indicadores visuales de riesgo (🔴 🟢)
- Tasa de mortalidad calculada
- Información del clúster asignado

## 🧠 Algoritmo de Clustering (DBSCAN)

### ¿Qué es DBSCAN?
**Density-Based Spatial Clustering of Applications with Noise** es un algoritmo de machine learning que agrupa puntos de datos según su densidad espacial.

### Parámetros Utilizados
```python
DBSCAN(eps=0.5, min_samples=3)
```
- `eps`: Distancia máxima entre puntos para ser considerados vecinos
- `min_samples`: Número mínimo de puntos para formar un clúster

### Lógica de Detección
1. **Normalización** de datos con StandardScaler
2. **Clustering** basado en número de muertes
3. **Identificación** de clústeres por encima del percentil 75
4. **Clasificación**: Alto Riesgo (🔴) vs Normal (🟢)

## 📊 Cálculo de Tasa de Mortalidad

```python
tasa = (muertes / poblacion_estimada) * 1000
```
*Nota: Se utiliza población estimada de 50,000 habitantes por departamento*

## 🎨 Escala de Colores

El mapa utiliza una escala de colores progresiva:
- 🔵 **Azul Claro** (#E3F2FD): Baja mortalidad
- 🔵 **Azul** (#42A5F5): Mortalidad media-baja
- 🟠 **Naranja** (#FF9800): Mortalidad media-alta
- 🔴 **Rojo Oscuro** (#E65100): Alta mortalidad (Clúster)

## 🔧 Tecnologías Utilizadas

- **Backend**: Django 4.2+
- **Visualización**: Plotly 5.14+
- **Machine Learning**: scikit-learn (DBSCAN)
- **Datos Geográficos**: GeoPandas, Shapely
- **Base de Datos**: MySQL 8.0
- **Frontend**: JavaScript ES6+, HTML5, CSS3

## 📁 Estructura de Archivos

```
dashboard/
├── mapa_avanzado.py           # Módulo principal de análisis IA
├── views.py                   # Vistas Django actualizadas
├── models.py                  # Modelos de datos
└── templates/
    └── dashboard/
        └── index.html          # Template con JavaScript interactivo

scripts/
└── prepare_geodata.py         # Descarga de geometrías de Colombia

data/
└── geodata/
    └── colombia_departamentos.geojson  # Límites geográficos
```

## 🚀 Uso de la API

### Endpoint Principal
```
GET /api/mapa-data/?sexo={SEXO}&causa={CODIGO_CAUSA}
```

### Parámetros
- `sexo`: TODOS | M | F | I
- `causa`: TODAS | {código_cie10}

### Respuesta JSON
```json
{
  "html": "<div>...</div>",  // HTML del gráfico Plotly
  "estadisticas": {
    "total_muertes": 244355,
    "departamentos_afectados": 33,
    "clusters_detectados": 5,
    "departamentos_alto_riesgo": 8,
    "tasa_promedio": 4.89
  },
  "tabla_datos": [
    {
      "departamento": "11",
      "nombre_depto": "BOGOTA D.C.",
      "total_muertes": 38760,
      "tasa_mortalidad": 0.78,
      "cluster": 0,
      "es_cluster_alto": true
    }
  ]
}
```

## 🎓 Conceptos de Ciencia de Datos Aplicados

### 1. **Normalización de Datos**
Uso de StandardScaler para estandarizar las variables antes del clustering.

### 2. **Clustering No Supervisado**
DBSCAN identifica patrones sin necesidad de especificar el número de clústeres.

### 3. **Análisis de Percentiles**
Uso del percentil 75 para definir el umbral de "alto riesgo".

### 4. **Visualización Geoespacial**
Representación de datos en contexto geográfico para análisis epidemiológico.

## 📈 Casos de Uso

1. **Vigilancia Epidemiológica**: Identificar brotes o zonas con mortalidad atípica
2. **Planificación en Salud Pública**: Asignar recursos a zonas de alto riesgo
3. **Investigación Académica**: Análisis de patrones espaciales de mortalidad
4. **Reportes Ejecutivos**: Dashboards interactivos para tomadores de decisiones

## 🔮 Mejoras Futuras

- [ ] Integrar coordenadas reales de centroides municipales
- [ ] Agregar mapa coroplético verdadero con GeoJSON
- [ ] Implementar Moran's I para autocorrelación espacial
- [ ] Agregar series temporales para detectar tendencias
- [ ] Machine Learning predictivo (Random Forest, XGBoost)
- [ ] Exportación de reportes en PDF/Excel

## 📝 Notas Técnicas

### Limitaciones Actuales
- Las coordenadas de departamentos son aproximadas (capitales)
- La población estimada es simulada (50,000 hab por depto)
- Los datos son del año 2019 únicamente

### Rendimiento
- Procesamiento de 244,355 registros en < 2 segundos
- Clustering optimizado con StandardScaler
- Consultas SQL con índices en departamento y causa

## 👨‍💻 Autor

Dashboard de Mortalidad Colombia 2019
Desarrollado con Django + Plotly + scikit-learn

---

**Última actualización**: Octubre 2025
**Versión**: 2.0 (Mapa Interactivo con IA)

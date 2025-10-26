# Dashboard de Mortalidad - Django + Soft UI Dashboard

## 🚀 Implementación Exitosa

Se ha migrado exitosamente el dashboard de **Dash/Plotly** a **Django** con diseño profesional inspirado en **Soft UI Dashboard**.

---

## 📁 Estructura del Proyecto

```
Dashboard de Mortalidad/
├── django_app/
│   ├── manage.py
│   ├── requirements.txt
│   ├── mortalidad_dashboard/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── templates/
│   │   └── dashboard/
│   │       └── index.html
│   └── static/
│       └── css/
│           └── soft-ui-dashboard.css
├── Dockerfile.django
├── docker-compose.django.yml
├── config/
│   └── schema.sql
└── scripts/
    └── generate_sample_data.py
```

---

## 🎨 Características del Diseño

### ✅ Sidebar Profesional
- **Gradiente oscuro** (#42424a → #191919)
- **Iconos Font Awesome** para todas las opciones
- **Estado activo** con gradiente rosa (#ec407a → #d81b60)
- **Efectos hover** con translateX y transparencia
- **Botón "UPGRADE TO PRO"** en la parte inferior

### ✅ KPIs Modernos
- **4 tarjetas** con métricas clave:
  - Total Muertes
  - Homicidios
  - Muertes Hombres
  - Muertes Mujeres
- **Iconos coloridos** con gradientes
- **Línea superior** de color de acento

### ✅ Visualizaciones Integradas
1. **Mapa Coroplético** de Colombia por departamentos
2. **Gráfico de Línea** de tendencia mensual
3. **Top 5 Municipios** con muertes violentas (barras horizontales)
4. **Top 10 Causas** de muerte (barras verticales)
5. **Distribución por Sexo** (pie chart)
6. **Distribución por Edad** (barras por grupos de edad)
7. **Tabla** de últimas muertes registradas

---

## 🐳 Docker - Comandos Principales

### Construir la imagen:
```bash
docker-compose -f docker-compose.django.yml build
```

### Iniciar los servicios:
```bash
docker-compose -f docker-compose.django.yml up -d
```

### Ver logs:
```bash
docker logs mortalidad_django_app
docker logs mortalidad_db
```

### Detener servicios:
```bash
docker-compose -f docker-compose.django.yml down
```

### Reiniciar solo Django:
```bash
docker-compose -f docker-compose.django.yml restart django_app
```

---

## 🔌 Conexión a la Base de Datos

El dashboard se conecta a MySQL usando las siguientes credenciales (configuradas en docker-compose):

- **Host**: db (dentro de Docker)
- **Puerto**: 3306 (interno), 3307 (externo)
- **Base de datos**: mortalidad_db
- **Usuario**: mortalidad_user
- **Contraseña**: mortalidad_pass

**Importante**: Los modelos Django usan `managed = False` para **NO** crear/modificar las tablas existentes en MySQL.

---

## 📊 Datos

El dashboard usa los **50,000 registros** de mortalidad ya generados:
- **Tabla**: muertes
- **Periodo**: Año 2019
- **Cobertura**: 30 departamentos de Colombia
- **Causas**: 20 causas de muerte diferentes con códigos CIE-10

Si necesitas regenerar los datos:
```bash
docker exec -it mortalidad_django_app python /app/scripts/generate_sample_data.py
```

---

## 🌐 Acceso al Dashboard

Una vez iniciados los contenedores, el dashboard está disponible en:

**http://localhost:8000**

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2+** - Framework web
- **mysqlclient** - Conector MySQL para Django
- **Plotly 5.14+** - Visualizaciones interactivas
- **Pandas 2.0+** - Procesamiento de datos
- **Gunicorn** - Servidor WSGI para producción

### Frontend
- **Soft UI Dashboard** - Diseño profesional Material Design
- **Font Awesome 6.4** - Iconos vectoriales
- **CSS3** - Estilos personalizados con gradientes
- **Plotly.js 2.26** - Renderizado de gráficos en el navegador

### Infraestructura
- **Docker** - Contenedores
- **MySQL 8.0** - Base de datos
- **WhiteNoise** - Servir archivos estáticos

---

## 📝 Rutas Disponibles

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard principal con todas las visualizaciones |
| `/admin/` | Panel de administración Django (requiere superusuario) |

---

## 🔐 Crear Superusuario (Opcional)

Para acceder al panel de administración de Django:

```bash
docker exec -it mortalidad_django_app python manage.py createsuperuser
```

Luego accede a: **http://localhost:8000/admin/**

---

## 🎯 Próximos Pasos Sugeridos

1. **Agregar autenticación** de usuarios
2. **Implementar filtros interactivos** (por fecha, departamento, causa)
3. **Crear vistas adicionales** para análisis específicos
4. **Agregar exportación** de datos a Excel/CSV
5. **Implementar API REST** con Django REST Framework
6. **Configurar Nginx** como proxy reverso
7. **Agregar tests unitarios** y de integración
8. **Deploy en producción** (AWS, Azure, DigitalOcean)

---

## 🐛 Troubleshooting

### Error de conexión a MySQL
```bash
# Verificar que el contenedor de MySQL esté saludable
docker ps

# Revisar logs de MySQL
docker logs mortalidad_db

# Esperar a que MySQL esté completamente iniciado
docker-compose -f docker-compose.django.yml restart django_app
```

### Archivos estáticos no se cargan
```bash
# Recolectar archivos estáticos manualmente
docker exec -it mortalidad_django_app python manage.py collectstatic --noinput
```

### Permisos en Windows
Si tienes problemas con volúmenes en Docker Desktop:
1. Asegúrate de que Docker Desktop tenga acceso a la unidad D:\
2. Ve a Settings → Resources → File Sharing

---

## 📧 Notas Finales

✅ **Migración completada** de Dash a Django
✅ **Diseño profesional** implementado con Soft UI Dashboard
✅ **Todas las visualizaciones** funcionando correctamente
✅ **Docker configurado** para desarrollo y producción
✅ **Base de datos poblada** con 50K registros

**El dashboard está listo para usar y personalizar según tus necesidades!** 🎉

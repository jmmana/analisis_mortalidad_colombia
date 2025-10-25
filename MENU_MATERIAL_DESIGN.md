# 🎨 Menú Material Design - Dashboard de Mortalidad

## ✨ Características del Nuevo Diseño

### Diseño Moderno y Profesional
- **Menú lateral estilo Material Design** con efectos visuales avanzados
- **Iconos emoji** para identificación visual rápida de cada sección
- **Animaciones fluidas** y transiciones suaves
- **Efectos hover** y ripple effects en los elementos interactivos
- **Paleta de colores** inspirada en Material Design de Google
- **Sombras y profundidad** según las directrices de Material Design
- **Diseño responsive** que se adapta a dispositivos móviles y tablets

### Estructura del Menú

#### 🗺️ Mapa Departamental
Visualización geográfica de la mortalidad por departamento

#### 📈 Tendencia Mensual
Evolución temporal de las muertes durante 2019

#### ⚠️ Ciudades Violentas
Top 5 de municipios con más homicidios

#### 🌱 Menor Mortalidad
10 ciudades más seguras del país

#### 📋 Principales Causas
Top 10 causas de muerte según CIE-10

#### 👥 Análisis por Sexo
Distribución por género en cada departamento

#### 📊 Grupos Etarios
Distribución de mortalidad por grupos de edad

## 🎨 Características Visuales

### Colores
- **Sidebar**: Gradiente oscuro (#263238 → #1c262b)
- **Primary**: #1976d2 (Material Blue)
- **Accent**: #ff4081 (Material Pink)
- **Success**: #4caf50 (Material Green)

### Tipografía
- **Fuente principal**: Roboto (Google Fonts)
- **Antialiasing**: Optimizado para legibilidad

### Efectos
- **Animaciones**: Cubic-bezier suave
- **Sombras**: 4 niveles según Material Design
- **Hover states**: Feedback visual inmediato
- **Active states**: Indicador lateral azul

## 📁 Archivos Modificados

### `src/dashboard/layout.py`
Nuevo diseño del menú lateral con:
- Estructura jerárquica de elementos
- Iconos y descripciones
- Sistema de radio buttons personalizado
- Header y footer del menú

### `assets/styles.css`
Hoja de estilos completa con:
- Variables CSS para personalización fácil
- Estilos Material Design
- Animaciones y transiciones
- Media queries para responsive design
- Modo de alto contraste
- Soporte para reduced motion

### `src/dashboard/__init__.py`
Actualizado para:
- Usar el nuevo layout
- Callbacks optimizados
- Mensajes de error mejorados
- Explicaciones contextuales

## 🚀 Cómo Ejecutar

### Con Docker (Recomendado)
```bash
docker-compose up
```

### Sin Docker
```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Ejecutar aplicación
python app.py
```

El dashboard estará disponible en: http://localhost:8050

## 🎯 Características de Accesibilidad

- **Contraste**: Cumple con WCAG 2.1 nivel AA
- **Keyboard navigation**: Soporte completo con Tab
- **Focus indicators**: Visibles y claros
- **Reduced motion**: Respeta preferencias del usuario
- **Screen readers**: Estructura semántica HTML

## 🔧 Personalización

### Cambiar Colores
Edita las variables en `assets/styles.css`:

```css
:root {
    --primary-color: #1976d2;  /* Tu color principal */
    --accent-color: #ff4081;   /* Tu color de acento */
    --bg-sidebar: #263238;     /* Color del sidebar */
}
```

### Cambiar Iconos
Edita los emojis en `src/dashboard/layout.py`:

```python
"icon": "🗺️",  # Reemplaza con tu icono preferido
```

### Añadir Nuevas Secciones
1. Agrega el item en `menu_items` en `layout.py`
2. Crea la función de construcción del gráfico
3. Añade el caso en el callback `update_content`

## 📱 Responsive Design

- **Desktop**: Sidebar fijo de 320px
- **Tablet**: Sidebar de 280px
- **Mobile**: Sidebar full-width colapsable

## 🎨 Inspiración de Diseño

Este diseño está inspirado en:
- **Material Design 3** de Google
- **Dashboards modernos** de analytics
- **Principios de UX** para visualización de datos

## 📝 Notas Técnicas

- **Framework**: Dash + Plotly
- **CSS**: Vanilla CSS con variables custom
- **Fuentes**: Google Fonts (Roboto)
- **Iconos**: Emoji Unicode (compatible con todos los navegadores)
- **Animaciones**: CSS transitions y keyframes

## 🐛 Solución de Problemas

### El menú no se ve correctamente
- Asegúrate de que `assets/styles.css` esté en la carpeta correcta
- Dash carga automáticamente los archivos de `assets/`

### Los iconos no se muestran
- Verifica que tu navegador tenga soporte para emojis Unicode
- Los emojis son compatibles con Chrome, Firefox, Safari y Edge modernos

### Las animaciones no funcionan
- Revisa que no tengas activado "Reduce motion" en tu sistema operativo
- El CSS detecta esta preferencia y desactiva automáticamente las animaciones

## 🎉 Resultado Final

El dashboard ahora tiene:
- ✅ Menú lateral profesional estilo Material Design
- ✅ Navegación intuitiva con iconos y descripciones
- ✅ Efectos visuales modernos
- ✅ Diseño responsive
- ✅ Accesibilidad mejorada
- ✅ Rendimiento optimizado

---

**¡Disfruta de tu nuevo dashboard profesional!** 🚀

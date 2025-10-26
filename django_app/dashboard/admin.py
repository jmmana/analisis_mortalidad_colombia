from django.contrib import admin
from .models import Muerte, Causa, Divipola

@admin.register(Muerte)
class MuerteAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'nombre_departamento', 'nombre_municipio', 'causa', 'sexo', 'edad')
    list_filter = ('sexo', 'fecha', 'nombre_departamento')
    search_fields = ('nombre_municipio', 'causa', 'codigo_cie10')
    date_hierarchy = 'fecha'

@admin.register(Causa)
class CausaAdmin(admin.ModelAdmin):
    list_display = ('codigo_cie10', 'descripcion', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('codigo_cie10', 'descripcion')

@admin.register(Divipola)
class DivipolaAdmin(admin.ModelAdmin):
    list_display = ('codigo_departamento', 'nombre_departamento', 'codigo_municipio', 'nombre_municipio')
    search_fields = ('nombre_departamento', 'nombre_municipio')

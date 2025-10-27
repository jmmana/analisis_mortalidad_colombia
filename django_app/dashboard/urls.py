from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/mapa-data/', views.get_mapa_data, name='mapa_data'),
    path('api/causas/', views.get_causas_list, name='causas_list'),
    path('api/test-mapa/', views.test_mapa, name='test_mapa'),
    path('test-mapa/', views.test_mapa_page, name='test_mapa_page'),
    path('debug-mapa/', views.debug_mapa_page, name='debug_mapa_page'),
]

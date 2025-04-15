# optimizer/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('input/', views.input_menu_view, name='input_menu'),
    path('delete/<int:pk>/', views.delete_menu_item, name='delete_item'),
    path('optimize/', views.run_optimization, name='run_optimization'),
    path('results/<int:pk>/', views.results_view, name='results'),
    path('download-pdf/<int:optimization_id>/', views.generate_pdf, name='download_pdf'),
]
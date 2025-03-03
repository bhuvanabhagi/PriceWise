# urls.py
from django.urls import path
from .views import HomeView, OptimizerView, InputParametersView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('optimizer/', OptimizerView.as_view(), name='optimizer'),
    path('input-parameters/<int:menu_item_id>/', InputParametersView.as_view(), name='input_parameters'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cittadini_list, name='home'),
    path('cittadini/', views.cittadini_list, name='cittadini_list'),
    path('ospedali/', views.ospedali_list, name='ospedali_list'),
]

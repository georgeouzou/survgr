from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('upload_reference/', views.upload_reference, name='upload_reference'),
]

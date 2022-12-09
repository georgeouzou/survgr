from django.urls import path
from . import views

app_name = 'procrustes'
urlpatterns = [
	path('', views.index, name='index'),
	path('upload_reference/', views.upload_reference, name='upload_reference'),
]

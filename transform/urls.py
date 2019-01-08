from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.transform, name="transform"),
    #url(r'^api/hattblock/(\d{1,3})/$', views.hattblock_info, name="hattblock"),
]

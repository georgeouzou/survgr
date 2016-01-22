from django.conf.urls import  url
import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/$', views.transform, name="transform"),
    url(r'^api/hattblock/(\d{1,3})/$', views.hattblock_info, name="hattblock"),
]

"""survgr URL Configuration"""
from django.urls import include, path
from django.contrib import admin

import transform.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transform.urls')),
	path('procrustes/', include('procrustes.urls')),
]

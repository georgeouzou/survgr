"""survgr URL Configuration"""
from django.conf.urls import include, url
from django.contrib import admin

import transform.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^transform/', include(transform.urls))
]

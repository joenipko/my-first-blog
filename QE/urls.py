from django.conf.urls import url, patterns
from . import views

urlpatterns = patterns('',
    url(r'^QELocationDetail/(?P<id>\d+)$', views.QELocationDetail, name='QELocationDetail'),
    url(r'^$', views.QECityGridSearch, name='QECityGridSearch'),
)
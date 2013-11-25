from django.conf.urls import *
from django.contrib import admin

from views import *

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^company/', include('companyapp.companyapp.urls', app_name='companyapp', namespace='companyapp')),
    url(r'^users/', include('companyapp.users.urls', app_name='users', namespace='users')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

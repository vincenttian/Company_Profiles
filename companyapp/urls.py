from django.conf.urls import *
from django.contrib import admin
from companyapp.views import *
from django.conf.urls.defaults import handler404

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    # url(r'^$', HomeView.as_view(), name='home'),
    url(r'^company/', include('companyapp.companyapp.urls', app_name='companyapp', namespace='companyapp')),
    url(r'^users/', include('companyapp.users.urls', app_name='users', namespace='users')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'companyapp.views.server_error_404'
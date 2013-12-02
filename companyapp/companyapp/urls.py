from django.conf.urls import patterns, include, url
from companyapp.companyapp import views
from companyapp.companyapp.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'companyapp.views.home', name='home'),
    # url(r'^companyapp/', include('companyapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^company/$', CompanyView.as_view(), name='company_list'),
    # url(r'^$', home, name='home'),
    url(r'^(?P<pk>[\w\d\-]+)/$', CompanyView.as_view(), name='company'),
)

from django.conf.urls import patterns
from django.conf.urls import url

from companyapp.users.views import LoginView, LogoutView, UserRegistrationView

urlpatterns = patterns('',
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', UserRegistrationView.as_view(), name='register'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
)

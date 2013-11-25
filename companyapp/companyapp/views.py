from django.views.generic import *
from companyapp.companyapp.models import *
from django.shortcuts import get_object_or_404, redirect

class CompanyView(DetailView):
    model = Company
    # context_object_name = 'company'
    template_name = 'company_detail.html'

    def get_object(self, queryset=None):
    	pk = self.kwargs.get(self.pk_url_kwarg, None)
    	return get_object_or_404(self.model, pk=pk)
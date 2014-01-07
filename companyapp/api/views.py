# Create your views here.

from django.views.generic import *
from companyapp.api.models import *
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.http import HttpResponse
from django.contrib import messages

class APIView(DetailView):
    model = API
    # context_object_name = 'company'
    template_name = 'api_detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(self.model, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(APIView, self).get_context_data(**kwargs)
        if self.request.method == "GET":
            context['searchform'] = SearchForm()
            return context
        else: # POST requests
            context['searchform'] = SearchForm(self.request.POST)
            return context

    def post (self, request, *args, **kwargs):
        self.object = self.get_object() 
        context = self.get_context_data(object=self.object)
        searchform = context['searchform']

        if searchform.is_valid(): # All validation rules pass
            search = searchform.cleaned_data['api_search']
            return redirect('/api/' + search + '/') # Redirect after POST
        return self.render_to_response(context) 

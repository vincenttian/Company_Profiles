from django.views.generic import *
from companyapp.companyapp.models import *
from companyapp.companyapp.forms import SearchForm
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.http import HttpResponse
from django.contrib import messages

class CompanyView(DetailView):
    model = Company
    # context_object_name = 'company'
    template_name = 'company_detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(self.model, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
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
            search = searchform.cleaned_data['company_search']
            return redirect('/company/' + search + '/') # Redirect after POST
        return self.render_to_response(context) 

# NEED TO MAKE HOME REQUEST NOT JUST SERVING A STATIC PAGE
def home(request):
    return render(request, 'home.html')

class HomeView(View):
    model = Company
    template_name = 'home_search.html'
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(self.model, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
        if self.request.method == "GET":
            context['searchform2'] = SearchForm()
            return context
        else: # POST requests
            context['searchform2'] = SearchForm(self.request.POST)
            return context

    def post (self, request, *args, **kwargs):
        self.object = self.get_object() 
        context = self.get_context_data(object=self.object)
        searchform = context['searchform2']

        if searchform.is_valid(): # All validation rules pass
            search = searchform.cleaned_data['company_search']
            return redirect('/company/' + search + '/') # Redirect after POST
        return self.render_to_response(context) 

def server_error_404(request):
    return render(request, '404.html')

def server_error_500(request):
    return render(request, '404.html')


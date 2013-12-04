from django import forms

class SearchForm(forms.Form):
    company_search = forms.CharField(max_length=100)
  
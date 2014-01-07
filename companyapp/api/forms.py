from django import forms

class SearchForm(forms.Form):
    api_search = forms.CharField(max_length=100)
  
from django import forms

class SearchForm(forms.Form):
    company = forms.CharField(max_length=100)
  
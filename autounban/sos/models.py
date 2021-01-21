from django.db import models
from django import forms
from django.utils.safestring import mark_safe

class ScriptForm(forms.Form):
    url = forms.CharField(required=True, label=mark_safe('</br></br><b>URL without scheme:</b></br>'))

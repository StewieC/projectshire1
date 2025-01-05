# forms.py
from django import forms
from .models import Contribution

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']
        
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'weekly_contribution']
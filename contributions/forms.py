# forms.py
from django import forms
from .models import Contribution
from django.contrib.auth.models import User
from .models import Group

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']
        
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'weekly_contribution']
        
        

class MemberManagementForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')], label="Action")
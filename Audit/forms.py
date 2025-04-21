from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from .models import *
import json
from django.forms import inlineformset_factory
from django import forms



class UserLoginForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'id': 'floatingInput', 'class': 'form-control mb-3'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'floatingPassword', 'class': 'form-control mb-3'}), required=True)

    class Meta:
        model = User
        fields = ['username','password']


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize: none; font-size: 14px;'
            }),
        }

class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['user', 'report']
        widgets = {
            'report': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize: none; font-size: 14px;'
            }),
        }


class InspectionResultForm(forms.ModelForm):
    class Meta:
        model = InspectionResult
        fields = ['inspection', 'requirement', 'is_met', 'comment', 'image']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control comment-field',
                'rows': 2,
                'style': 'resize: none; font-size: 14px; height: 60px;'  # <- ważne!
            })
        }




class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'font-size: 14px; width: 100%;',
            }),
        }


RequirementFormSet = inlineformset_factory(
    Audit,
    Requirement,
    form=RequirementForm,
    fields=('text',),
    extra=1,
    can_delete=True,
)



InspectionResultFormSet = inlineformset_factory(
    Inspection,
    InspectionResult,
    form=InspectionResultForm,
    fields=['requirement', 'is_met', 'comment', 'image'],
    extra=0,
    can_delete=False,
)


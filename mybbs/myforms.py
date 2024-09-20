# author:carey


from django import forms
from django.forms import widgets
from mybbs import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


class RegisterForms(forms.Form):
    name = forms.CharField(max_length=9, label='用户名',
                           widget=widgets.TextInput(attrs={'class': 'form-control'}),
                           error_messages={'required': '该字段必填', 'max_length': '不能长于9位'})
    pwd = forms.CharField(max_length=9, label='密码',
                          widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                          error_messages={'required': '该字段必填', 'max_length': '不能长于9位'})
    re_pwd = forms.CharField(max_length=9, label='确认密码',
                             widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
                             error_messages={'required': '该字段必填', 'max_length': '不能长于9位'})
    email = forms.EmailField(label='邮箱',
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}),
                             error_messages={'required': '该字段必填', 'invalid': '不符合邮箱格式'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        user = models.UserInfo.objects.filter(username=name)
        if user:
            raise ValidationError("用户已存在")
        else:
            return name

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致')

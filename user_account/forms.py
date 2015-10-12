import re

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .models import UserProfile


User = get_user_model()


class RegistrationForm(forms.Form):

    '''sign-up form for a new user'''

    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('User Name'), 'class': 'form-control',
               'autofocus': 'true'}), max_length=30, required=True)
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': _('Email Address'), 'class': 'form-control'}),
        required=True)
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('First Name'), 'class': 'form-control'}),
        max_length=25, required=True)
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('Last Name'), 'class': 'form-control'}),
        max_length=25, required=True)
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('Phone Number'), 'class': 'form-control'}),
        max_length=12, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': _('Password'), 'class': 'form-control'}),
        required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': _('Confirm password'), 'class': 'form-control'}),
        required=True)

    def clean_password2(self):
        if 'password1' in self.data:
            password1 = self.data['password1']
            password2 = self.data['password2']
            if password1 == password2:
                return password2
            raise forms.ValidationError(_('Passwords do not match!'))

    def clean_username(self):
        username = self.data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError(
                _('Only alphanumeric characters and underscores allowed'))
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username

        raise forms.ValidationError(
            _('username {0} is already taken ').format(username))

    class Meta:
        model = UserProfile
        exclude = ('user', 'activation_key', 'key_expires')


class LoginForm(forms.Form):

    ''' Login form for a registered user '''

    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('User Name'), 'class': 'form-control',
               'autofocus': 'true'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': _('Password'), 'class': 'form-control'}))


class PhoneVerificationForm(forms.Form):

    ''' Phone veriification form  '''

    code = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': _('Verification code'), 'class': 'form-control',
               'autofocus': 'true'}), max_length=12, required=True)

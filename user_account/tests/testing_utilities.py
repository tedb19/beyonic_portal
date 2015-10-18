import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from ..models import UserProfile


def populate_test_db():
    user = User.objects.create_user(
        username='test098$',
        email='test@gmail.com',
        password='secret123')

    user.last_name = 'lstname'
    user.first_name = 'fstname'

    user.save()

    UserProfile.objects.create(
        user=user,
        activation_key='f6115c62e890btest2',
        key_expires=timezone.now() + datetime.timedelta(2),
        phone_number='+2541234567'
    )


def login_client_user(self):
    self.client.login(username='test098$', password='secret123')
    return self


def logout_client_user(self):
    self.client.logout()
    return self


def set_up_login_form_values():
    entries = {}
    entries["username"] = 'test098$'
    entries["password"] = 'secret123'
    return entries


def set_up_form_values():
    # define some form fields/values
    entries = {}
    entries['username'] = 'test1'
    entries['email'] = 'test@gmail.com'
    entries['first_name'] = 'test'
    entries['last_name'] = 'test'
    entries['phone_number'] = '254720230439'
    entries['password1'] = 'test'
    entries['password2'] = 'test'
    return entries


def delete_test_data():
    user_profile = UserProfile.objects.get(activation_key='f6115c62e890btest2')
    user = user_profile.user
    user_profile.delete()
    user.delete()

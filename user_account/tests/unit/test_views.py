import datetime

from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.test import TestCase, Client
from django.utils import timezone

from user_account.models import UserProfile
from user_account.views import success, home

from ..testing_utilities import (populate_test_db,
                                 delete_test_data,
                                 login_client_user)


class HomeViewTests(TestCase):

    ''' Tests for the home view '''

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.home_url = reverse('home')

    def test_home_view_renders_successfully(self):
        '''Test home view renders successfully '''

        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beyonic Portal")

    def test_home_uses_home_template(self):
        ''' Test home view uses the home template '''

        home_url = reverse('home')
        response = self.client.get(home_url)
        self.assertTemplateUsed(response, 'user_account/home.html')
        self.assertEqual(response.status_code, 200)
        print(response.content)

    def test_home_url_resolves_to_home_view(self):
        '''Test home url resolves to home view '''
        found = resolve(self.home_url)
        self.assertEqual(found.func, home)


class IndexViewTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.index_url = reverse('index')

    def test_index_redirects_to_home_view(self):
        ''' Test index view redirects to home view '''

        response = self.client.get(self.index_url)
        expected_url = reverse('home')
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200,
                             host=None, msg_prefix='',
                             fetch_redirect_response=True)


class RegistrationViewTests(TestCase):

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=False)
        self.registration_url = reverse('registration')
        self.home_url = reverse('home')

    def test_registration_view_renders(self):
        '''Test registration view renders successfully '''

        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Registration")

    def test_registration_uses_register_template(self):
        ''' Test registration view uses the right template '''

        response = self.client.get(self.registration_url)
        self.assertTemplateUsed(response, 'user_account/register.html')
        self.assertEqual(response.status_code, 200)
        print(response.content)

    def test_registration_form_redirect(self):
        """ Test registration redirect's to home when user logged in """

        login_client_user(self)

        self.assertTrue(login_client_user(self))
        response = self.client.get(self.registration_url)
        self.assertRedirects(response, expected_url=self.home_url,
                             status_code=302, target_status_code=200)

    def tearDown(self):
        delete_test_data()


class LogoutViewTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.logout_url = reverse('user_logout')
        self.login_url = reverse('user_login')

    def test_logout_redirects_to_login(self):
        ''' Test logout view redirects to login view '''

        response = self.client.get(self.logout_url, follow=True)
        self.assertRedirects(response, self.login_url)


class LoginViewTests(TestCase):

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=False)
        self.user_profile = UserProfile.objects.get(
            activation_key='f6115c62e890btest2')
        self.logout_url = reverse('user_logout')
        self.login_url = reverse('user_login')
        self.home_url = reverse('home')
        self.phone_verification_url = reverse(
            'phone-verification', args=[self.user_profile.user.pk])

    def test_login_view_renders_successfully(self):
        '''Test login view renders successfully '''

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login | Beyonic Portal")

    def test_login_view_uses_login_template(self):
        ''' Test login view uses the login template '''

        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'user_account/login.html')
        self.assertEqual(response.status_code, 200)
        print(response.content)

    def test_login_redirects_to_home_when_user_logged_in(self):
        """ Test login redirect's to home when user logged in """

        login_client_user(self)

        self.assertTrue(login_client_user(self))
        response = self.client.get(self.login_url)
        self.assertRedirects(response, expected_url=self.home_url,
                             status_code=302, target_status_code=200)

    def tearDown(self):
        delete_test_data()


class PhoneVerificationViewTests(TestCase):

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=True)
        self.user_profile = UserProfile.objects.get(
            activation_key='f6115c62e890btest2')
        self.phone_verification_url = reverse(
            'phone-verification', args=[self.user_profile.user.pk])

    # home view tests
    def test_phone_verification_view_renders(self):
        '''Test phone verification view renders successfully '''

        response = self.client.get(self.phone_verification_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Phone Number Verification')

    def test_confirm_uses_confirm_template(self):
        ''' Test phone verification view uses the right template '''

        response = self.client.get(self.phone_verification_url)
        self.assertTemplateUsed(
            response, 'user_account/phone-verification.html')
        self.assertEqual(response.status_code, 200)
        print(response.content)

    def tearDown(self):
        delete_test_data()


class ConfirmViewTests(TestCase):

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=True)
        self.confirm_url = reverse(
            'confirm', args=['f6115c62e890btest2'])
        self.user_profile = UserProfile.objects.get(
            activation_key='f6115c62e890btest2')
        self.phone_verification_url = reverse(
            'phone-verification', args=[self.user_profile.user.pk])

    def test_confirm_redirects_to_verification(self):
        ''' Test confirm view redirects to phone verification view '''

        response = self.client.get(self.confirm_url)
        self.assertRedirects(response, self.phone_verification_url,
                             status_code=302, target_status_code=200,
                             host=None, msg_prefix='',
                             fetch_redirect_response=True)

    def test_confirm_displays_error__message_when_key_expires(self):
        '''Test confirm view displays error message when key expires'''
        self.user_profile.key_expires = timezone.now() - datetime.timedelta(2)
        self.user_profile.save()
        response = self.client.get(self.confirm_url)
        error = 'Sorry, but the activation key has expired!'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, error)

    def tearDown(self):
        delete_test_data()


class SuccessViewTests(TestCase):

    ''' Tests for the success view '''

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=True)
        self.user_profile = UserProfile.objects.get(
            activation_key='f6115c62e890btest2')
        self.success_url = reverse(
            'success', args=[self.user_profile.user.pk])

    def test_success_view_renders(self):
        '''Test success view renders successfully '''

        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Successful Registration')

    def test_success_view_uses_home_template(self):
        ''' Test success view uses the success template '''

        response = self.client.get(self.success_url)
        self.assertTemplateUsed(response, 'user_account/success.html')
        self.assertEqual(response.status_code, 200)

    def test_success_url_resolves_to_success_view(self):
        '''Test success url resolves to success view '''
        found = resolve(self.success_url)
        self.assertEqual(found.func, success)

    def tearDown(self):
        delete_test_data()

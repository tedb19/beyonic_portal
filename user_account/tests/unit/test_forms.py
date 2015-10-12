from django.test import TestCase, Client
from django import forms
from django.core.urlresolvers import reverse
from ..testing_utilities import (login_client_user,
                                 populate_test_db,
                                 delete_test_data,
                                 set_up_form_values)

from user_account.forms import RegistrationForm


class RegistrationFormTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        # Log user for all tests
        login_client_user(self)

        # define some form fields/values
        self.entries = set_up_form_values()

    def test_form_field_validation_error_messages(self):
        ''' Tests field validations messages are displayed '''

        form_addr = reverse('registration')
        post_data = {}  # form does not send any data!
        response = self.client.post(form_addr, post_data)
        self.assertEqual(response.status_code, 200)
        msg = 'This field is required.'
        self.assertFormError(response, 'form', 'username', msg)
        self.assertFormError(response, 'form', 'email', msg)
        self.assertFormError(response, 'form', 'first_name', msg)
        self.assertFormError(response, 'form', 'last_name', msg)
        self.assertFormError(response, 'form', 'first_name', msg)

    def test_passwords_dont_match(self):
        ''' Tests validation error thrown if the two passwords dont match '''

        form_addr = reverse('registration')
        self.entries['password2'] = 'test2'
        response = self.client.post(form_addr, self.entries)
        self.assertEqual(response.status_code, 200)
        msg = 'Passwords do not match!'
        self.assertFormError(response, 'form', 'password2', msg)
        form = RegistrationForm(data=self.entries)
        with self.assertRaises(forms.ValidationError):
            form.clean_password2()

    def test_form_field_validations_success_message(self):
        ''' Tests the response when the Registration
            Form is correctly filled '''

        form_addr = reverse('registration')

        # Use follow=true since there will be a redirect after processing
        response = self.client.post(form_addr,
                                    self.entries,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"Successful Registration")

    def test_form_validation(self):
        ''' Test registration rorm validation works correctly '''

        form_data = {
            'username': 'X',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserNameTests(TestCase):

    def setUp(self):
        populate_test_db()
        self.entries = set_up_form_values()

    def test_unique_username(self):
        ''' Test only unique usernames accepted '''
        self.entries['username'] = 'test098$'
        form = RegistrationForm(data=self.entries)
        self.assertFalse(form.is_valid())
        with self.assertRaises(forms.ValidationError):
            form.clean_username()

    def test_username_regex_rule(self):
        ''' Test username abides by set regex rule '''
        self.entries['username'] = '#$%^&*'
        form = RegistrationForm(data=self.entries)
        self.assertFalse(form.is_valid())
        with self.assertRaises(forms.ValidationError):
            form.clean_username()

    def tearDown(self):
        delete_test_data()


class LoginFormTest(TestCase):

    def setUp(self):
        populate_test_db()
        self.client = Client(enforce_csrf_checks=False)

        # define some form fields/values
        self.entries = {}
        self.entries['username'] = 'test098$'
        self.entries['password'] = 'secret123'

    def test_login_form_validation(self):
        ''' Test login form validation works correctly '''

        form_data = {
            'username': 'X',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def tearDown(self):
        delete_test_data()

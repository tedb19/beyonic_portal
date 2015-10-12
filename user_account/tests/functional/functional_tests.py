import time

from selenium.webdriver.firefox import webdriver
from django.core.urlresolvers import reverse
from django import test

from ..testing_utilities import (populate_test_db,
                                 delete_test_data,
                                 set_up_form_values)


class LoginTest(test.LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.WebDriver()
        populate_test_db()

    def tearDown(self):
        time.sleep(3)
        self.selenium.refresh()
        self.selenium.quit()
        delete_test_data()
        time.sleep(3)

    # Auxiliary function to add view subdir to URL
    def _get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    def test_if_user_logs_in(self):
        ''' Test if login succeeds for active user '''
        text = 'Phone Number Verification'
        self.open_login_page()
        time.sleep(3)
        self.submit_login_form()
        time.sleep(3)
        response = self.selenium.find_element_by_css_selector('body').text
        self.assertTrue(text in response)
        self.selenium.refresh()

    def open_login_page(self):
        self.selenium.get(self._get_full_url("user_login"))
        self.assertIn(u'Login', self.selenium.title)

    def submit_login_form(self):
        test_username = 'test098$'
        test_password = 'secret123'

        username = self.selenium.find_element_by_name('username')
        password = self.selenium.find_element_by_name('password')
        username.send_keys(test_username)
        password.send_keys(test_password)
        submit = 'button[type="submit"]'
        submit = self.selenium.find_element_by_css_selector(submit)
        submit.click()


class RegistrationTest(test.LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.WebDriver()
        populate_test_db()
        self.entries = set_up_form_values()

    def tearDown(self):
        time.sleep(3)
        self.selenium.refresh()
        self.selenium.quit()
        delete_test_data()
        time.sleep(3)

    # Auxiliary function to add view subdir to URL
    def _get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    def test_if_registration_succeeds(self):
        ''' Test if registration succeeds with correct arguments '''
        text = 'Successful Registration'
        self.open_registration_page()
        time.sleep(3)
        self.submit_registration_form()
        time.sleep(3)
        response = self.selenium.find_element_by_css_selector('body').text
        self.assertTrue(text in response)
        self.selenium.refresh()

    def open_registration_page(self):
        self.selenium.get(self._get_full_url("registration"))
        self.assertIn(u'User Registration', self.selenium.title)

    def submit_registration_form(self):
        username = self.selenium.find_element_by_name('username')
        email = self.selenium.find_element_by_name('email')
        first_name = self.selenium.find_element_by_name('first_name')
        last_name = self.selenium.find_element_by_name('last_name')
        phone_number = self.selenium.find_element_by_name('phone_number')
        password1 = self.selenium.find_element_by_name('password1')
        password2 = self.selenium.find_element_by_name('password2')

        username.send_keys(self.entries['username'])
        email.send_keys(self.entries['email'])
        first_name.send_keys(self.entries['first_name'])
        last_name.send_keys(self.entries['last_name'])
        phone_number.send_keys(self.entries['phone_number'])
        password1.send_keys(self.entries['password1'])
        password2.send_keys(self.entries['password2'])

        submit = 'input[type="submit"]'
        submit = self.selenium.find_element_by_css_selector(submit)
        submit.click()

import time

from selenium.webdriver.firefox import webdriver
from django.core.urlresolvers import reverse
from django import test

from ..testing_utilities import (populate_test_db,
                                 delete_test_data,
                                 set_up_form_values,
                                 set_up_login_form_values)


class FormTest(test.LiveServerTestCase):

    @classmethod
    def setUp(cls):
        cls.selenium = webdriver.WebDriver()
        populate_test_db()

    @classmethod
    def tearDown(cls):
        time.sleep(3)
        cls.selenium.refresh()
        cls.selenium.quit()
        delete_test_data()
        time.sleep(3)

    # Auxiliary function to add view subdir to URL
    def _get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    def open_form_page(self, url_name, title_text):
        self.selenium.get(self._get_full_url(url_name))
        self.assertIn(title_text, self.selenium.title)

    def submit_form(self,
                    submission_button,
                    entries={}):
        '''
        Assumes that the form element's name is same
        as the corresponding form field
        '''
        for key, elem in entries.items():
            key = self.selenium.find_element_by_name(key)
            key.send_keys(elem)

        submit = self.selenium.find_element_by_css_selector(submission_button)
        submit.click()


class LoginTest(FormTest):

    url_name = u"user_login"
    title_text = u"Login"
    entries = set_up_login_form_values()

    def open_login_page(self):
        return super(LoginTest, self).open_form_page(
            self.url_name, self.title_text)

    def submit_login_form(self):
        return super(LoginTest, self).submit_form(
            'button[type="submit"]', self.entries)

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


class RegistrationTest(FormTest):

    url_name = u"registration"
    title_text = u"User Registration"
    entries = set_up_form_values()

    def open_registration_page(self):
        return super(RegistrationTest, self).open_form_page(
            self.url_name, self.title_text)

    def submit_registration_form(self):
        return super(RegistrationTest, self).submit_form(
            'input[type="submit"]', self.entries)

    def test_if_registration_succeeds(self):
        ''' Test registration of new user '''
        text = 'Successful Registration'
        self.open_registration_page()
        time.sleep(3)
        self.submit_registration_form()
        time.sleep(3)
        response = self.selenium.find_element_by_css_selector('body').text
        self.assertTrue(text in response)
        self.selenium.refresh()

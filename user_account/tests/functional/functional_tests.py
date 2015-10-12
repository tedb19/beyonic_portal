from selenium.webdriver.firefox import webdriver
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from ..testing_utilities import populate_test_db, delete_test_data

import time

from django import test
from selenium.webdriver.firefox import webdriver

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.WebDriver()
        self.selenium.implicitly_wait(3)
        populate_test_db()

    def tearDown(self):
        self.selenium.quit()
        self.selenium.refresh()
        delete_test_data()

    # Auxiliary function to add view subdir to URL
    def _get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    def test_home_title(self):
        """
        Tests that Home is loading properly
        """
        self.selenium.get(self._get_full_url("home"))
        self.assertIn(u'Beyonic Portal', self.selenium.title)
        self.selenium.refresh()

    def test_registration_page(self):
        # new user goes to home page
        self.selenium.get(self._get_full_url("home"))
        # user clicks the sign-up link
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_link_text('sign up').click()
        # user is redirected to registration page
        body = self.selenium.find_element_by_tag_name('body')
        text = 'Please take a moment to register for an account.'
        self.assertIn(text, body.text)
        self.assertIn('User Registration', self.selenium.title)
        self.selenium.refresh()



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
        text = 'We are happy to have you on board!'
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
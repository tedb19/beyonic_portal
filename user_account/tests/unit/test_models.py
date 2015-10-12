from django.test import TestCase
from django.core import mail
from django.conf import settings

from user_account.models import UserProfile
from ..testing_utilities import populate_test_db, delete_test_data


class UserProfileTests(TestCase):

    ''' Tests for the UserProfile Model '''

    def setUp(self):
        # Add records to test DB
        populate_test_db()
        self.user_profile = UserProfile.objects.get(
            activation_key='f6115c62e890btest2')

    def test_creation_of_valid_model_instance(self):
        ''' Test successfull creating of valid UserProfile instance '''

        stringified = 'fstname lstname - test@gmail.com - +2541234567'
        self.assertTrue(isinstance(self.user_profile, UserProfile))
        self.assertEqual(self.user_profile.__str__(), stringified)

    def test_model_instance_values(self):
        ''' Test model instance values '''
        user_profiles = UserProfile.objects.all()
        user_profile = user_profiles[0]
        self.assertEquals(len(user_profiles), 1)
        self.assertEquals(str(user_profile.phone_number), '+2541234567')
        self.assertEquals(user_profile.activation_key, 'f6115c62e890btest2')
        self.assertEquals(user_profile.user.email, 'test@gmail.com')
        self.assertEquals(user_profile.user.last_name, 'lstname')
        self.assertEquals(user_profile.user.first_name, 'fstname')
        self.assertEquals(user_profile.user.username, 'test098$')

    def test_user_profile_verbose_name(self):
        ''' Test UserProfile verbose name '''
        verbose_name = UserProfile._meta.verbose_name.title()
        self.assertEquals(verbose_name, 'User Profile')

    def test_user_profile_verbose_name_plural(self):
        ''' Test UserProfile verbose name plural'''
        verbose_name_plural = UserProfile._meta.verbose_name_plural.title()
        self.assertEquals(verbose_name_plural, 'User Profiles')

    def test_send_activation_link(self):
        ''' Test sending activation link via mail '''
        self.user_profile.send_activation_link()
        root_url = settings.ROOT_URL
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.recipients(), ['test@gmail.com'])
        self.assertEqual(msg.subject, 'Beyonic Portal account confirmation')
        url = "{0}/user/accounts/confirm/{1}/".format(
            root_url, self.user_profile.activation_key)
        self.assertIn(url, msg.body)
        self.assertIn('Below is your account activation link', msg.body)

    def tearDown(self):
        delete_test_data()

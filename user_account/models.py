import logging

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core.cache import cache

from phonenumber_field.modelfields import PhoneNumberField
import twilio
from twilio.rest import TwilioRestClient


logger = logging.getLogger(__name__)


class TimeStampedModel(models.Model):

    '''
    This is a model mixin for models which
    need to be time stamped
    '''
    created = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):

    ''' a user profile for each user '''

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='my_profile'
    )
    phone_number = PhoneNumberField()
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    def __str__(self):
        profile = []
        profile.append(self.user.get_full_name())
        profile.append(self.user.email)
        profile.append(str(self.phone_number))
        return ' - '.join(profile)

    def send_sms(self, code):
        try:
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            twilio_phone_number = settings.CALLER_ID
            phone_number = str(self.phone_number)

            client = TwilioRestClient(account_sid, auth_token)
            body = ('Enter the code: {0} on the'
                    'verification form to verify'
                    ' your phone number').format(code)
            client.messages.create(body=body,
                                   to=phone_number,
                                   from_=twilio_phone_number)
            logger.info(
                _('verification code sent to {0} ').format(phone_number))
        except twilio.TwilioRestException as e:
            error_msg = _('An error occured while sending'
                          ' the verification code: {0}').format(e)
            logger.error(error_msg)

    def verify_code(self, code):
        """ Verify a code is correct """
        return str(code) == str(cache.get(str(self.phone_number)))

    def send_activation_link(self):
        root_url = settings.ROOT_URL
        from_mail = settings.EMAIL_HOST_USER
        email_subject = 'Beyonic Portal account confirmation'
        link = "{0}/user/accounts/confirm/{1}/".format(
            root_url, self.activation_key)

        # for content-type = text/html
        html_msg = ''' <html><body><div>Hello {0},
        <br /><br />
        Thank you for signing up for a Beyonics Portal account.
        To activate your account, click the following link within
         48 hours
        <br /><br />
        {1}
        <br /><br />
        You will then be asked to submit a code that has been sent
         to you at {2} via sms.
        <br /><br />
        Good day
        <br /><br />
        <style="color:green">-Teddy Odhiambo</style>
        <br /><br />
        </div></body></html>
        '''.format(self.user.get_full_name().title(),
                   link, str(self.phone_number))

        # for content-type = text/plain
        email_body = '''Hello {0},\n
         Below is your account activation link\n\n{1}
        \n\nThis link will expire in 48 hours.\n\n
        You will then be asked to submit a code that
         has been sent to you at {2} via sms.
         \n\nThank you'''.format(self.user.get_full_name(),
                                 link, str(self.phone_number))

        try:
            send_mail(email_subject,
                      email_body,
                      from_mail,
                      [self.user.email],
                      html_message=html_msg,
                      fail_silently=False)
            logger.info(
                _('email sent successfully to {0}').format(self.user.email))
        except Exception as detail:
            logger.error(_('Could not send mail. {0}').format(detail))

    class Meta:
        db_table = 'userprofile'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

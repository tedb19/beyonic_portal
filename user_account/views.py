import datetime
import random
import hashlib
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from .models import UserProfile
from .forms import RegistrationForm, LoginForm, PhoneVerificationForm


logger = logging.getLogger(__name__)


def _get_code(length=5):
    """ Return a numeric code with length digits """
    return random.sample(range(10**(length - 1), 10**length), 1)[0]


def registration(request):
    page_title = 'User Registration'
    template_name = 'user_account/register.html'
    root_url = settings.ROOT_URL
    from_mail = settings.EMAIL_HOST_USER
    has_account = False
    if request.user.is_authenticated():
        has_account = True
        messages.warning(request, _(
            'Sorry, {0}. This service is only for registration of new users')
            .format(request.user.username))
        # redirect to homepage...
        return redirect(home)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if request.POST.get('cancel', None):
            return redirect(home)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = '+' + form.cleaned_data['phone_number']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)

            user.is_active = False
            user.first_name = first_name.upper()
            user.last_name = last_name.upper()
            user.save()

            # Build the activation key for their account
            encoded_rand = str(random.random()).encode('utf-8')
            salt = hashlib.sha224(encoded_rand).hexdigest()[:5]
            salted_username = (salt + user.username).encode('utf-8')
            activation_key = hashlib.sha224(
                salted_username).hexdigest()[:40]
            key_expires = timezone.now() + datetime.timedelta(2)

            # Create and save their profile
            profile = UserProfile(user=user,
                                  activation_key=activation_key,
                                  key_expires=key_expires,
                                  phone_number=phone_number)
            profile.save()
            msg = _('new user registered successfully. {0}').format(profile)
            logger.info(msg)
            # store the code in the cache for later verification.
            # valid for 24 hrs
            code = _get_code()
            cache.set(phone_number, code, 24 * 3600)
            profile.send_activation_link()
            profile.send_sms(code)
            return redirect(success, pk=user.pk)
        else:
            msg = ("Ooops! Please correct the highlighted fields,"
                   " then try again.")
            messages.warning(request, _(msg))
            return render(request, template_name, locals())
    else:
        form = RegistrationForm()
        return render(request, template_name, locals())


def confirm(request, activation_key):
    page_title = 'Account confirmation'
    expired = False
    template_name = 'user_account/confirm.html'
    if request.user.is_authenticated():
        msg = ('Sorry, {0}. This service is only for registration of'
               ' new users').format(request.user.username)
        messages.warning(request, _(msg))
        return redirect(home)
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < timezone.now():
        expired = True
        return render(request, template_name, locals())
    user_account = user_profile.user
    msg = 'Congratulations! your email has been verified successfully.'
    messages.info(request, _(msg))
    # redirect to phone verification page
    return redirect(phone_verification, pk=user_account.pk)


def home(request):
    template_name = 'user_account/home.html'
    page_title = 'Beyonic Portal'

    if request.user.is_authenticated():
        user_profile = request.user.my_profile
    return render(request, template_name, locals())


def success(request, pk):
    user = User.objects.get(pk=pk)
    template_name = 'user_account/success.html'
    page_title = 'Successful Registration'
    user.is_authenticated = False
    return render(request, template_name, locals())


def phone_verification(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_authenticated = False
    if user:
        user_profile = user.my_profile
        template_name = 'user_account/phone-verification.html'
        page_title = 'Phone Number Verification'

        if request.method == 'POST':
            form = PhoneVerificationForm(request.POST)
            phone_number = str(user_profile.phone_number)
            if form.is_valid():
                code = form.cleaned_data['code']
                if user_profile.verify_code(code):
                    cache.delete(phone_number)
                    user.is_active = True
                    user.save()
                    user.is_authenticated = True
                    if user.last_login:
                        msg = ('Welcome back {0}'.format(user.get_full_name()))
                    else:
                        msg = ('Phone number has been successfully verified.')
                    messages.info(request, _(msg))
                    return redirect(home)
                else:
                    msg = ('Sorry, the code you provided does not '
                           'match the one sent to {0}').format(
                        phone_number)
                    messages.warning(request, _(msg))
            else:
                msg = ("Ooops! Please correct the highlighted fields,"
                       " then try again.")
                messages.warning(request, _(msg))
        else:
            form = PhoneVerificationForm()
        return render(request, template_name, locals())


def LoginRequest(request):
    template_name = 'user_account/login.html'

    if request.user.is_authenticated():
        return redirect(home)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            siteuser = authenticate(username=username, password=password)

            if siteuser is not None and siteuser.is_active:
                """set a session id for this session"""
                login(request, siteuser)
                user_profile = siteuser.my_profile
                phone_number = str(user_profile.phone_number)
                code = _get_code()
                cache.set(phone_number, code, 24 * 3600)
                user_profile.send_sms(code)
                return redirect(phone_verification, pk=siteuser.pk)

            elif siteuser and not siteuser.is_active:
                msg = ('Please activate your account via the link sent to '
                       'you at ' + siteuser.email + ' then try again')
            else:
                msg = ("Sorry, the login credentials you've provided"
                       " don't match any user account.")
            messages.warning(request, _(msg))
        else:
            msg = ("Ooops! Please correct the highlighted fields,"
                   " then try again.")
            messages.warning(request, _(msg))
    else:
        form = LoginForm()
    return render(request, template_name, locals())


def LogoutRequest(request):
    '''expires the session'''
    logout(request)
    return redirect(LoginRequest)


def index(request):
    return redirect(home)


def error404(request):
    template_name = 'user_account/error404.html'
    page_title = 'Page not found'
    return render(request, template_name, locals())


def error500(request):
    template_name = 'user_account/error500.html'
    page_title = 'Internal server error'
    return render(request, template_name, locals())

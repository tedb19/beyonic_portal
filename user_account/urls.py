from django.conf.urls import patterns, url


urlpatterns = patterns(
    'user_account.views',

    url(r'^sign-up/$', 'registration', name='registration'),
    url(r'^success/(?P<pk>[-\w]+)/$', 'success', name='success'),
    url(r'^phone-verification/(?P<pk>[-\w]+)/$',
        'phone_verification',
        name='phone-verification'),
    url(r'^accounts/confirm/(?P<activation_key>[-\w]+)/$',
        'confirm',
        name='confirm'),
    url(r'^login/$', 'LoginRequest', name='user_login'),
    url(r'^logout/$', 'LogoutRequest', name='user_logout'),
    url(r'^home/$', 'home', name='home'),

)

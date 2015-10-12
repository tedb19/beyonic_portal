from django.conf.urls import include, url, patterns
from django.views.generic.base import RedirectView


urlpatterns = patterns(
    '',
    url(r'^user/', include('user_account.urls')),
    url(r'^$', RedirectView.as_view(
        url='/user/home/', permanent=False), name='index'),
)

handler404 = 'user_account.views.error404'
handler500 = 'user_account.views.error500'

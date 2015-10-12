from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf.urls import handler404, handler500


urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('user_account.urls')),
    url(r'^$', RedirectView.as_view(
        url='/user/home/', permanent=False), name='index'),
)

handler404 = 'user_account.views.error404'
handler500 = 'user_account.views.error500'



from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bet.views.home', name='home'),
    # url(r'^bet/', include('bet.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^sync/(?P<table>[-\w]+)$','main.views.sync_table',name='sync'),
    url(r'^', include(admin.site.urls)),
#    url(r'^$','main.views.index',name='home'),
#    url(r'^bet','main.views.bet', name='bet'),
#    url(r'^errorCheck','main.views.errorCheck', name='errorCheck'),
#    url(r'^logout','main.views.logout_user',name='logout'),

)

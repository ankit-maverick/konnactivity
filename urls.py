from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from pinterested.login import views as login_views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
    url(r'^login/?$', login_views.FB_handler),
    url(r'^finalize/?$', login_views.finalizer),
    # url(r'^pinterested/', include('pinterested.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

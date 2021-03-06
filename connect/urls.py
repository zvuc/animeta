from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^twitter/$', 'connect.views.twitter'),
    (r'^twitter/disconnect/$', 'connect.views.twitter_disconnect'),
    (r'^facebook/$', 'connect.views.facebook'),
    (r'^facebook/disconnect/$', 'connect.views.facebook_disconnect'),
    (r'^widget/$', TemplateView.as_view(template_name='connect/widget.html')),
)

from django.conf.urls import url
from . import views

urlpatterns = [
    #   /oauth/qq/statues/
    url(r'^qq/statues/$',views.OauthQQURLView.as_view(),name='statues'),
    # /oauth/qq/users/
    url(r'^qq/users/$', views.OauthQQView.as_view(), name='qqtoken'),
]
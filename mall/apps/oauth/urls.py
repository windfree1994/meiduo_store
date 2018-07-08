from django.conf.urls import url
from . import views

urlpatterns = [
    #   /oauth/qq/statues/
    url(r'^qq/statues/$',views.OauthQQURLView.as_view(),name='statues'),
]
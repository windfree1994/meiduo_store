from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    #/users/usernames/(?P<username>\w{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountAPIView.as_view(),name='usernamecount'),
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.RegisterPhoneCountAPIView.as_view(), name='phonecount'),

    url(r'^$',views.CreateUserView.as_view()),
    # /users/auths/
    url(r'auths/', obtain_jwt_token),

    url(r'^infos/$',views.UserCenterInfoView.as_view()),

    # /users/emails/
    url(r'^emails/$', views.EmailView.as_view()),
    #GET /users/emails/verification/
    url(r'^emails/verification/$',views.EmailVerifiView.as_view()),
    # /users/browerhistories/
    url(r'^browerhistories/$', views.UserHistoryView.as_view(), name='history'),

]
from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls
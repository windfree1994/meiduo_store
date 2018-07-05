from django.conf.urls import url
from . import views

urlpatterns = [
    #verifications/imagecodes/(?P<image_code_id>.+)/
    url(r'^imagecodes/(?P<image_code_id>.+)/$',views.RegisterImageCodeView.as_view(),name='imagecode'),
    # verifications/smscodes/(?P<mobile>1[345789]\d{9})/
    url(r'^smscodes/(?P<mobile>1[345789]\d{9})/$',views.RegisterSMSCodeView.as_view()),
]
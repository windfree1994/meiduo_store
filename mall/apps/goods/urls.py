from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^index/$',views.IndexVIew.as_view()),
    # /goods/categories/(?P<category_id>\d+)/hotskus/
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUView.as_view()),
    # /goods/categories/(?P<category_id>\d+)/skus/
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListAPIView.as_view()),
]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls
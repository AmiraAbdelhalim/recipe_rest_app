from django.urls import path, include
from . import views
# default router: automatically generate the urls for the viewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls))
]

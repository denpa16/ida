from os import name
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, ImageResizeViewSet
from django.urls import path

router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')

urlpatterns = [
    path('images/<int:pk>/resize/', ImageResizeViewSet.as_view({'post':'create'}), name='resize')
]

urlpatterns += router.urls
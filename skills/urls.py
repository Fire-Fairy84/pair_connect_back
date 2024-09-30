from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StackViewSet, LevelViewSet, ProgLanguageViewSet

router = DefaultRouter()
router.register(r'stacks', StackViewSet, basename='stack')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'languages', ProgLanguageViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
]
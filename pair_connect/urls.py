from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include


def home(request):
    return HttpResponse("Welcome to the Pair Connect API")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/skills/', include('skills.urls')),
    path('api/projects/', include('projects.urls')),
    path('', home),
]

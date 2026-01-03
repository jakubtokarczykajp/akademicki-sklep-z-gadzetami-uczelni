"""
URL configuration for akademickisklepzgadzetami project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.apps import apps
from django.urls import include, path
from django.contrib import admin
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from . import views

DEBUG = settings.DEBUG

urlpatterns = [
    # 1. Obsługa odświeżania przeglądarki (Tailwind) - To naprawi błąd /__reload__/
    path("__reload__/", include("django_browser_reload.urls")),

    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),

    # Twój widok home
    path('home/', views.home, name='home'),

    # Przekierowanie ze strony głównej na /home/
    path('', lambda request: redirect('home/')),

    # Sklep Oscar (musi być na końcu listy, bo przejmuje wiele adresów)
    path('shop/', include(apps.get_app_config('oscar').urls[0])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
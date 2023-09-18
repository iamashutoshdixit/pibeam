"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("a0ce743445e30281/admin/", admin.site.urls),
    path("drivers/", include("drivers.urls")),
    path("fleets/", include("fleets.urls")),
    path("users/", include("users.urls")),
    path("config/", include("config.urls")),
    path("chaining/", include("smart_selects.urls")),
    path("clients/", include("clients.urls")),
    path("bookings/", include("bookings.urls")),
]

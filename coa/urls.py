"""
URL configuration for coa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("coapp.urls")),
    path("accounts/", include("allauth.urls")),

]
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from urllib.parse import unquote
from django.views.static import serve

def decoded_serve(request, path, **kwargs):
    return serve(request, unquote(path), **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("coapp.urls")),
    path("accounts/", include("allauth.urls")),
]

# Добавляем обработку медиа с поддержкой декодирования
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', decoded_serve, {'document_root': settings.MEDIA_ROOT}),
]

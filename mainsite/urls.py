"""apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from mainsite.views import health_check_view


urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('favicon.ico', RedirectView.as_view(url='%sfavicon.ico' % settings.STATIC_URL)),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # Elastic beanstalk ELB requires trailing slash for health check
    path('health/', health_check_view, name='health_check_view'),
    path('health123/', health_check_view, name='health_check_view'),
    # Material icons
    path('material-person-add', RedirectView.as_view(url='%simg/material-person-add.svg' % settings.STATIC_URL)),
    path('material-person-remove', RedirectView.as_view(url='%simg/material-person-remove.svg' % settings.STATIC_URL)),
    path('material-directions-bike', RedirectView.as_view(url='%simg/material-directions-bike.svg' % settings.STATIC_URL)),
    path('material-hail', RedirectView.as_view(url='%simg/material-hail.svg' % settings.STATIC_URL)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
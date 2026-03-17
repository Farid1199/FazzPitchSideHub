"""
URL configuration for config project.

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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from users import views
import re as _re

from users.views import admin_analytics_view

urlpatterns = [
    path('admin/analytics/', admin_analytics_view, name='admin_analytics'),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    #path('dashboard/', views.dashboard_view, name='dashboard'),
]

# Serve media files during development — EXCEPT protected directories
# Protected dirs are served through auth-gated views in users/views.py
_PROTECTED_MEDIA_DIRS = {'scout_certificates', 'coaching_certificates', 'coaching_dashboard_screenshots'}

if settings.DEBUG:
    def _safe_media_serve(request, path, document_root=None):
        """Serve media files but block direct access to protected directories."""
        from django.http import Http404
        top_dir = path.split('/')[0] if '/' in path else path
        if top_dir in _PROTECTED_MEDIA_DIRS:
            raise Http404
        return static_serve(request, path, document_root=document_root)

    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            _safe_media_serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]

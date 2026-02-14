from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),
    path('workspaces/', include('workspaces.urls')),
    path('tasks/', include('tasks.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

# Media files (for avatar uploads)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'core.views.custom_404'
handler403 = 'core.views.custom_403'
handler500 = 'core.views.custom_500'
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', include('tubig_tracker_app.urls')),  # Include your app URLs
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Redirect root URL to login
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
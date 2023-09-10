from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('store/', include('store.urls')),
    path('order/', include('order.urls')),
    # path('__debug__/', include('debug_toolbar.urls')),
    # drf_spectacular
    path('api/schema/', views.SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', views.SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', views.SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

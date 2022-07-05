from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Innotter API",
        default_version='v1',
        description="Innotter will become bigger then twitter one day",
        contact=openapi.Contact(email="eugene.osakovich@gmail.com"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-innotter-api'),
    path('api/', include('api.urls')),
]

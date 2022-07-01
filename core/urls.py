"""innotter URL Configuration

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
from rest_framework import routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from page.views import PageAPIView, PostAPIView
from user.views import UserAPIView, UserLoginAPIView, UserLogoutAPIView, UserProfileAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="Support API",
        default_version='v1',
        description="API for Tech Support Sevice",
        contact=openapi.Contact(email="eugene.osakovich@gmail.com"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
#   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register('user', UserAPIView)
router.register('pages', PageAPIView)
router_post = routers.DefaultRouter()
router_post.register('post', PostAPIView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/pages/<int:pk>/', include(router_post.urls)),
    path('api/v1/user/login/', UserLoginAPIView.as_view()),
    path('api/v1/user/logout/', UserLogoutAPIView.as_view()),
    path('api/v1/user/profile/', UserProfileAPIView.as_view({'get': 'list',
                                                             'put': 'update',
                                                             'delete': 'destroy'})),
    path('api/v1/', include(router.urls)),
    path('schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-innotter-api'),
]

from django.urls import path, include
from rest_framework import routers
from page.views import PageAPIView, PostAPIView
from user.views import UserAPIView, UserLoginAPIView


router = routers.DefaultRouter()
router.register('user', UserAPIView)
router.register('pages', PageAPIView)
router_post = routers.DefaultRouter()
router_post.register('post', PostAPIView)


urlpatterns = [
    path('pages/<int:pk>/', include(router_post.urls)),
    path('user/login/', UserLoginAPIView.as_view()),
    path('', include(router.urls)),
]

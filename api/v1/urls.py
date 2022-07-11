from django.urls import path, include
from rest_framework import routers
from page.views import PageAPIView, PostAPIView
from user.views import UserAPIView, UserLoginAPIView


router = routers.DefaultRouter()
router.register('user', UserAPIView)
router.register('pages', PageAPIView, basename="Pages")
router_post = routers.DefaultRouter()
router_post.register('post', PostAPIView)


urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view()),
    path('', include(router.urls)),
    path('pages/<int:pk>/', include(router_post.urls)),

]

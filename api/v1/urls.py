from django.urls import path, include
from rest_framework import routers
from page.views import PageAPIViewset, PostAPIViewset
from user.views import UserAPIViewset, UserLoginAPIView


router = routers.DefaultRouter()
router.register('user', UserAPIViewset)
router.register('pages', PageAPIViewset, basename="Pages")
router_post = routers.DefaultRouter()
router_post.register('post', PostAPIViewset, basename="Posts")


urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view()),
    path('', include(router.urls)),
    path('pages/<int:page_id>/', include(router_post.urls)),
]

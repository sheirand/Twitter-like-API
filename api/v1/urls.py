from django.urls import path, include
from rest_framework import routers
from page.views import PageAPIViewset, PostAPIViewset, FeedAPIViewset
from user.views import UserAPIViewset, UserLoginAPIView


router = routers.DefaultRouter()
router.register('user', UserAPIViewset)
router.register('pages', PageAPIViewset, basename="Pages")
router.register('feed', FeedAPIViewset, basename="Feed")
router_post = routers.DefaultRouter()
router_post.register('posts', PostAPIViewset, basename="Posts")


urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view()),
    path('', include(router.urls)),
    path('pages/<int:page_id>/', include(router_post.urls)),
]

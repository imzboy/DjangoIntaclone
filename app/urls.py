from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as rest_views
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('login/', views.login.as_view(), name='login'),
    path('logout/', views.logout.as_view()),
    path('upload-post/', views.createPostView.as_view()),
    path('get-posts/', views.listPostsView.as_view()),
    path('upload-story/', views.CreateStoryApiView.as_view()),
    path('get-storyes/', views.ListStoryApiView.as_view()),
    path('like/', views.LikeCreateApiView.as_view()),
    path('unlike/<int:pk>', views.UnLikeAPIView.as_view()),
    path('comment/', views.CommentCreateApiView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

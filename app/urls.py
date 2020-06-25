from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views as rest_views
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('upload-post/', views.make_a_post, name='post'),
    path('posts-list/', views.return_posts, name='posts_list'),
    path('get-user-feed/', views.get_posts, name='get_posts'),
    path('upload-story/', views.make_a_story, name='story'),
    path('get-stories/', views.get_stories, name='get_stories'),
    path('like/', views.like, name='like'),
    path('comment/', views.comment, name='comment'),
    path('get-comments/', views.get_comments_to_object, name='get-comments')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

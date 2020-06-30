import datetime
import json

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status

from app.serializer import (
    UserSerializer,
    PostSerializer,
    StorySerializer,
    LikeSerializer,
    CommentSerializer
    )

from app.models import Post, Story, Comment, Like

from rest_framework import generics
from rest_framework.views import APIView


class login(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(username= serializer.data['username'])
            token, created = Token.objects.get_or_create(user=user)
            return Response({'Token': token.key}, 200)
        return Response({'error': 'idl'})


class logout(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class createPostView(generics.CreateAPIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.pk)

class listPostsView(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def get_queryset(self, request):
        try:
            if json.loads(self.request.data['exclude_user']):  # all posts except current users
                return Post.objects.filter().exclude(author_id=request.user.pk)
            else:  # all posts
                return Post.objects.all()
        except KeyError:  # only current user posts
            return Post.objects.filter(author_id=request.user.pk)

    def list(self, request):
            queryset = self.get_queryset(request=request)
            serializer = PostSerializer(queryset, many=True)
            return Response(serializer.data)

class CreateStoryApiView(generics.CreateAPIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.pk)


class ListStoryApiView(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):  # if a story is older than 24 hour it's not listed
        queryset = Story.objects.all()
        print(queryset)
        if queryset:
            for query in queryset:
                print(query)
                if query.upload_date > query.expier_date:
                    queryset = queryset.exclude(id=query.pk)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = StorySerializer(queryset, many=True)
        return Response(serializer.data)


class LikeCreateApiView(generics.CreateAPIView):
    """
    A view to create a like
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.request.data['object_to_attach_id'])
        if post:
            post.likes += 1
            post.save()
        else:
            comment = Comment.objects.get(id=self.request.data['object_to_attach_id'])
            comment.likes += 1
            comment.save()
        serializer.save(author_id=self.request.user.pk)


class UnLikeAPIView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class CommentCreateApiView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.pk)

    def get_queryset(self, request):
        return Comment.objects.filter(
            object_to_attach_id=request.data['object_to_attach_id']
            )

    def list(self, request):
        queryset = self.get_queryset(request=self.request)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)
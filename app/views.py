# import binascii
# import hashlib
# import uuid
# import os

# from rest_framework.decorators import api_view, parser_classes


# from .models import User, Post, Story, Comment, Like
# from .Utils import (
#     validate_photo,
#     construct_posts_response,
#     construct_story_response
# )

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
    StorySerializer
    )

from app.models import Post

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

class CreateStory(generics.CreateAPIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user.pk)


# # stories list task
# @api_view(['POST'])
# def make_a_story(request):
#     try:
#         token = request.data['token']
#         user = User.objects.get(token=token)
#         if user:  # check the access token
#             story_id = str(uuid.uuid1().hex)  # create a random id
#             author_id = user.id
#             img = request.FILES.get('image')
#             story = Story(
#                 id=story_id,
#                 author_id=author_id,
#                 img=img,
#                 )
#             story.save()
#             img = validate_photo(story.img)  # Extra Task
#             return Response({
#                 'status': 'created',
#                 'story_id': story_id,
#                 'author': user.username}, 200)
#         else:
#             return Response({'Error': 'Not valid token'})
#     except KeyError:
#         return Response({'Error': 'no auth token provided'}, 401)


# # stories list task
# @api_view(['POST'])
# def get_stories(request):
#     try:
#         token = request.data['token']
#         user = User.objects.get(token=token)
#         if user:
#             stories = Story.objects.all()
#             response = construct_story_response(stories)
#             return Response(response, 200)
#         else:
#             return Response({'Error': 'Not valid token'})
#     except KeyError:
#             return Response({'Error': 'no auth token provided'}, 401)

#  # likes task
# @api_view(['POST'])
# def like(request):
#     try:
#         token = request.data['token']
#         attach_object_id = request.data['object_id']
#         user = User.objects.get(token=token)
#         if user:
#             like = Like(
#                 id = str(uuid.uuid1().hex),
#                 author = user.username,
#                 attach_object_id = attach_object_id
#             )
#             like.save()
#             post = Post.objects.get(id=attach_object_id)
#             if post:
#                 post.likes += 1
#                 post.save()
#             else:
#                 comment = Comment.objects.get(id=attach_object_id)
#                 comment.likes +=1
#                 comment.save()
#             return Response({
#                 'status': 'attached',
#                 'author': user.username,
#                 'object_id': attach_object_id
#             })
#         else:
#             return Response({'Error': 'Not valid token'})
#     except KeyError:
#             return Response({'Error': 'no auth token provided or wrong obj id'}, 401)

#  # comment tree task
# @api_view(['POST'])
# def comment(request):
#     try:
#         token = request.data['token']
#         attach_object_id = request.data['object_id']
#         user = User.objects.get(token=token)
#         if user:
#             comment = Comment(
#                 id = str(uuid.uuid1().hex),
#                 object_to_attach_id = attach_object_id,
#                 author_id = user.id,
#                 comment = request.data['comment']
#             )
#             comment.save()
#             return Response({
#                 'status': 'attached',
#                 'author': user.username,
#                 'object_id': attach_object_id
#             })
#         else:
#             return Response({'Error': 'Not valid token'})
#     except KeyError:
#             return Response({'Error': 'no auth token provided'}, 401)

#  # comment tree task
# @api_view(['POST'])
# def get_comments_to_object(request):
#     try:
#         token = request.data['token']
#         object_id = request.data['object_id']
#         user = User.objects.get(token=token)
#         if user:
#             comments = Comment.objects.filter(object_to_attach_id=object_id)
#             response = {
#                 'king': 'CommentTreeList',
#                 'Items_count': 0,
#                 'Items': []
#             }
#             for count ,comment in enumerate(comments):
#                 response['Items'].append({
#                     "kind": "CommentItem",
#                     "id": comment.id,
#                     "attached_object_id": comment.object_to_attach_id,
#                     "author": comment.author_id,
#                     "comment": comment.comment,
#                     "upload_date": comment.upload_date,
#                     "Likes": comment.likes,
#                     "replies": {
#                         "king": "CommentTreeList",
#                         "Items_count": 0,
#                         "Items": []
#                     }}
#                 )
#                 replies = Comment.objects.filter(object_to_attach_id=comment.id)
#                 if replies:
#                     for reply in replies:
#                         response['Items'][count]['replies']['Items'].append(
#                                 {
#                             "kind": "CommentItem",
#                             "id": reply.id,
#                             "attached_object_id": reply.object_to_attach_id,
#                             "author": reply.author_id,
#                             "comment": reply.comment,
#                             "upload_date": reply.upload_date,
#                             "Likes": reply.likes
#                             }
#                         )
#                     response['Items'][count]['replies']['Items_count'] = \
#                         len(response['Items'][count]['replies']['Items'])
#             response["Items_count"] = len(response['Items'])
#             return Response(response, 200)
#         else:
#             return Response({'Error': 'Not valid token'})
#     except KeyError:
#             return Response({'Error': 'no auth token provided'}, 401)

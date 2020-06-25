import binascii
import hashlib
import uuid
import os

from rest_framework.decorators import api_view, parser_classes
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import User, Post, Story, Comment, Like
from .Utils import (
    validate_photo,
    construct_posts_response,
    construct_story_response
)


# users(login/logout only) task
@api_view(['POST'])
def login(request):
    """A function to login the user.

       arguments:
           username: str
           password: str
        returns:
            token: str -- an access token

       After inputting the credentials returns a token.
       With the token the user can access any api"""

    try:
        inputted_password = request.data['password']
        inputted_username = request.data['username']
    except KeyError:  # in case the request didn't include username or pass
        return Response(
                {'Error': 'the POST request must contain values username and password'}
            )
    try:
        user = User.objects.get(username=inputted_username)
        hashed_password = hashlib.pbkdf2_hmac(  # hasing the password
            'sha256',
            inputted_password.encode('utf-8'),
            user.salt ,
            100000
            )
        if hashed_password == user.password:  # password and name is correct
            return Response({
                'Username': user.username,
                'Token': user.token
                })
        else:  # password is not correct
            return Response({'Error': 'wrong password'})
    except User.DoesNotExist:
        return Response({'Error': 'no such user exist'})

# users(login/logout only) task
@api_view(['POST'])
def register(request):
    """A function to register a user.

       arguments:
           username: str
           password: str

       After the user contributed his credentials, create a db entry.
       The entry includes username, hashed password, salt for the password,
       and a generated token for accessing other api endpoints."""

    if request.method == 'POST':
        token = binascii.hexlify(os.urandom(20)).decode()
        try:
            inputted_username = request.data['username']
            inputted_password = request.data['password']

        except KeyError:  # in case the request didn't include username or pass
            return Response(
                {'Error': 'the POST request must contain values username and password'}
            )
        salt = os.urandom(24)
        hashed_password = hashlib.pbkdf2_hmac(  # hasing the password
            'sha256',
            inputted_password.encode('utf-8'),
            salt,
            100000
            )
        user = User(
            username=inputted_username,
            password=hashed_password,
            token=token,
            salt=salt
            )
        user.save()
        return Response({'user': user.username, 'status': 'created'})

# photo upload task
@api_view(['POST'])
def make_a_post(request):
    """A function to make a post.
       Takes a token, image and a description"""
    try:
        token = request.data['token']
        user = User.objects.get(token=token)
        if user:  # check the access token
            post_id = str(uuid.uuid1().hex)  # create a random id
            author_id = user.id
            img = request.FILES.get('image')
            description = request.data['description']
            post = Post(
                id=post_id,
                author_id=author_id,
                img=img,
                description=description
                )
            post.save()
            img = validate_photo(post.img)
            return Response({
                'status': 'created',
                'post_id': post_id,
                'author': user.username,
                'description': description}, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
        return Response({'Error': 'no auth token provided'}, 401)

# photos list task
@api_view(['POST'])
def return_posts(request):
    """An endpoint that returns all of the users posts"""

    try:
        token = request.data['token']
        user = User.objects.get(token=token)
        if user:
            posts = Post.objects.filter(author_id=user.id)
            response = construct_posts_response(posts)

            return Response(response, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided'}, 401)

# photos list task
@api_view(['POST'])
def get_posts(request):
    try:
        token = request.data['token']
        user = User.objects.get(token=token)
        if user:
            posts = Post.objects.all()
            response = construct_posts_response(
                posts,
                user.id,
                request.data['include_viewed'])  # read status required to filter only unread posts task
            return Response(response, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided'}, 401)


# stories list task
@api_view(['POST'])
def make_a_story(request):
    try:
        token = request.data['token']
        user = User.objects.get(token=token)
        if user:  # check the access token
            story_id = str(uuid.uuid1().hex)  # create a random id
            author_id = user.id
            img = request.FILES.get('image')
            story = Story(
                id=story_id,
                author_id=author_id,
                img=img,
                )
            story.save()
            img = validate_photo(story.img)  # Extra Task
            return Response({
                'status': 'created',
                'story_id': story_id,
                'author': user.username}, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
        return Response({'Error': 'no auth token provided'}, 401)


# stories list task
@api_view(['POST'])
def get_stories(request):
    try:
        token = request.data['token']
        user = User.objects.get(token=token)
        if user:
            stories = Story.objects.all()
            response = construct_story_response(stories)
            return Response(response, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided'}, 401)

 # likes task
@api_view(['POST'])
def like(request):
    try:
        token = request.data['token']
        attach_object_id = request.data['object_id']
        user = User.objects.get(token=token)
        if user:
            like = Like(
                id = str(uuid.uuid1().hex),
                author = user.username,
                attach_object_id = attach_object_id
            )
            like.save()
            post = Post.objects.get(id=attach_object_id)
            if post:
                post.likes += 1
                post.save()
            else:
                comment = Comment.objects.get(id=attach_object_id)
                comment.likes +=1
                comment.save()
            return Response({
                'status': 'attached',
                'author': user.username,
                'object_id': attach_object_id
            })
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided or wrong obj id'}, 401)

 # comment tree task
@api_view(['POST'])
def comment(request):
    try:
        token = request.data['token']
        attach_object_id = request.data['object_id']
        user = User.objects.get(token=token)
        if user:
            comment = Comment(
                id = str(uuid.uuid1().hex),
                object_to_attach_id = attach_object_id,
                author_id = user.id,
                comment = request.data['comment']
            )
            comment.save()
            return Response({
                'status': 'attached',
                'author': user.username,
                'object_id': attach_object_id
            })
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided'}, 401)

 # comment tree task
@api_view(['POST'])
def get_comments_to_object(request):
    try:
        token = request.data['token']
        object_id = request.data['object_id']
        user = User.objects.get(token=token)
        if user:
            comments = Comment.objects.filter(object_to_attach_id=object_id)
            response = {
                'king': 'CommentTreeList',
                'Items_count': 0,
                'Items': []
            }
            for count ,comment in enumerate(comments):
                response['Items'].append({
                    "kind": "CommentItem",
                    "id": comment.id,
                    "attached_object_id": comment.object_to_attach_id,
                    "author": comment.author_id,
                    "comment": comment.comment,
                    "upload_date": comment.upload_date,
                    "Likes": comment.likes,
                    "replies": {
                        "king": "CommentTreeList",
                        "Items_count": 0,
                        "Items": []
                    }}
                )
                replies = Comment.objects.filter(object_to_attach_id=comment.id)
                if replies:
                    for reply in replies:
                        response['Items'][count]['replies']['Items'].append(
                                {
                            "kind": "CommentItem",
                            "id": reply.id,
                            "attached_object_id": reply.object_to_attach_id,
                            "author": reply.author_id,
                            "comment": reply.comment,
                            "upload_date": reply.upload_date,
                            "Likes": reply.likes
                            }
                        )
                    response['Items'][count]['replies']['Items_count'] = \
                        len(response['Items'][count]['replies']['Items'])
            response["Items_count"] = len(response['Items'])
            return Response(response, 200)
        else:
            return Response({'Error': 'Not valid token'})
    except KeyError:
            return Response({'Error': 'no auth token provided'}, 401)

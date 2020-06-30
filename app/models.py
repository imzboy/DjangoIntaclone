from django.db import models
from model_utils.models import TimeFramedModel
import datetime

class Post(models.Model):
    """A Post model.
       Has an author id, image, description, likes count, upload date
       and a views list for checking what user already seen this post"""
    author_id = models.IntegerField()
    img = models.ImageField(upload_to='post_pics')
    description = models.TextField(max_length=280, default='')
    likes = models.IntegerField(default=0)
    upload_date = models.DateField(auto_now_add=True)


class Story(models.Model):
    """A story model.
       Has a author id, image and a upload_date.
       If a story is older than 24 hrs it gets deleted"""
    author_id = models.IntegerField()
    img = models.ImageField(upload_to='post_pics')
    upload_date = models.DateTimeField(auto_now_add=True)
    expier_date = models.DateTimeField(
       default=datetime.datetime.now() + datetime.timedelta(hours=24))


class Comment(models.Model):
    """A comment model for comment on posts
       object_to_attach_id is an id of another comment or post object
       that this object will be attached to, creating a comment tree"""
    object_to_attach_id = models.TextField()
    author_id = models.IntegerField()
    comment = models.TextField(max_length=140)
    upload_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

class Like(models.Model):
    """A like model for comments and posts
       Can be attached via attach_object_id to a comment or a post"""
    author_id = models.TextField(max_length=50)
    attach_object_id = models.TextField()

from django.contrib.auth.models import User

from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

import io
import sys

from rest_framework import serializers

from app.models import (
    Post,
    Story,
    Like,
    Comment
    )

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150)
    password = serializers.CharField(max_length=128)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id', 'author_id', 'img',
            'description', 'likes',
            'upload_date']
        read_only_fields = ['id', 'author_id', 'likes', 'upload_date']

    # EXTRA TASK
    def validate_img(self, value):
        image = Image.open(value)
        if image.size[0] > 1000 or image.size[1] > 1000:
            image = image.resize((1000, 1000), Image.ANTIALIAS)
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            return InMemoryUploadedFile(output, 'ImageField',
                                        value.name,
                                        'image/jpeg',
                                        sys.getsizeof(output), None)
        return value


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'author_id', 'img', 'upload_date', 'expier_date']
        read_only_fields = ['id', 'author_id', 'upload_date', 'expier_date']

    # EXTRA TASK
    def validate_img(self, value):
        image = Image.open(value)
        if image.size[0] > 1000 or image.size[1] > 1000:
            image = image.resize((1000, 1000), Image.ANTIALIAS)
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            return InMemoryUploadedFile(output, 'ImageField',
                                        value.name,
                                        'image/jpeg',
                                        sys.getsizeof(output), None)
        return value


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'author_id', 'attach_object_id']
        read_only_fields = ['id', 'author_id']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'object_to_attach_id',
                  'author_id', 'comment', 'upload_date', 'likes']
        read_only_fields = ['id', 'author_id', 'upload_date', 'likes']
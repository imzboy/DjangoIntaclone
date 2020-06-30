from django.contrib.auth.models import User

from django.core.files.images import get_image_dimensions

from PIL import Image

from rest_framework import serializers

from app.models import (
    Post,
    Story
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

    def validate_img(self, value):
        img = Image.open(value)
        if img.size[0] > 1000 or img.size[1] > 1000:
            img = img.resize((1000, 1000))
            Image.Image.save(img, "media\post_pics\\"+str(img.name[10:]))
        return value


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'author_id', 'img', 'upload_date']
        read_only_fields = ['id', 'upload_date']

    def validate_img(self, value):
        # width, height = get_image_dimensions(value)
        # if width > 1000: width = 1000
        # if height > 1000: height = 1000
        return value
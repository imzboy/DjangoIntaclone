"""A general utils file"""
from PIL import Image
import os
import datetime

def validate_photo(image):
    """EXTRA TASK.

       Validates if a photo uploaded is not larger than 1000x1000 px.
       If the photo is larger the function resizes and saves it."""

    img = Image.open(image)
    if img.size[0] > 1000 or img.size[1] > 1000:
        img = img.resize((1000, 1000))
        Image.Image.save(img, "media\post_pics\\"+str(image.name[10:]))
    return img

def construct_posts_response(posts, user_id=0, include_viewed=True):
    """Constructs a dict responce for an api call

    Args:
        posts (QuerySet): posts from the db, could be all the posts or only
        users posts.
    """
    response = {
        "kind": "PhotoPostItemList",
        "item_count": 0,
        "Items":[]
    }
    for post in posts:
        if include_viewed == 'false' and post.views_list.find(str(user_id)) != -1:
            print('opps..')
            continue
        response['Items'].append({
            'post_id': post.id,
            'author_id': post.author_id,
            'img': '{}/media/{}'.format('http://127.0.0.1:8000' ,str(post.img)),
            'description': post.description,
            'likes': post.likes,
            'upload_date': '{}-{}-{}'.format(  # date format YYYY-MM-DD
                post.upload_date.year,
                post.upload_date.month,
                post.upload_date.day
            )
        })
        post.views_list = post.views_list + ' ' + str(user_id)
        post.save()
    response['item_count'] = len(response['Items'])
    return response


def construct_story_response(storys):
    """Constructs a dict responce for an api call

    Args:
        storys (QuerySet): storys from the db

    if a story is older than 24 hours is deletes it
    """
    response = {
        "kind": "PhotoStoryItemList",
        "item_count": 0,
        "Items":[]
    }
    for story in storys:
        tz_info = story.upload_date.tzinfo
        diff = datetime.datetime.now(tz_info) - story.upload_date
        if diff >= datetime.timedelta(days=1):
            story.delete()  # if a story is older than 24 hours is gets deleted
            print(story.id,' deleted')
            continue
        response['Items'].append({
            'story_id': story.id,
            'author_id': story.author_id,
            'img': '{}/media/{}'.format('http://127.0.0.1:8000' ,str(story.img)),
            'upload_date': '{}-{}-{}'.format(  # date format YYYY-MM-DD
                story.upload_date.year,
                story.upload_date.month,
                story.upload_date.day
            )
        })
    response['item_count'] = len(response['Items'])
    return response
from django import template
from django.contrib.auth import get_user_model

Account = get_user_model()
register = template.Library()


@register.simple_tag
def did_vote(post, user_id):
    try:
        return post.votes.exists(user_id)
    except:
        return False

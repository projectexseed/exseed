from django import template
from django.contrib.auth import get_user_model

Account = get_user_model()
register = template.Library()


@register.simple_tag
def did_vote(post, user_id):
    try:
        user = Account.objects.get(pk=user_id)
        return post.votes.exists(user)
    except:
        return False

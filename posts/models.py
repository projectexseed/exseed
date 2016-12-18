from __future__ import unicode_literals
from django.db import models

# http://radiac.net/projects/django-tagulous/documentation/usage/
import tagulous.models

#https://github.com/Beeblio/django-vote
from vote.managers import VotableManager


class PostManager(models.Manager):
    def create_post_with_data(self, request, data):
        title = data['title']
        body = data['body']
        tags = data['tags']
        user = request.user

        Post.objects.create(
            title=title,
            body=body,
            owner=user,
            tags=tags
        )


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    parent = models.ForeignKey("Post", blank=True, null=True, related_name="replies")
    owner = models.ForeignKey("accounts.Account")

    tags = tagulous.models.TagField(force_lowercase=True)
    votes = VotableManager()

    ordinal = models.IntegerField(default=0)

    completed = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['ordinal']

    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {'pk': self.id})

    @property
    def vote_count(self):
        return self.votes.count()

    @property
    def reply_count(self):
        return Post.objects.filter(parent=self).count()

    def next_ordinal(self):
        if self.replies.count() > 0:
            return self.replies.order_by('-ordinal')[0].ordinal + 1
        else:
            return 0

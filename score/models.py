from __future__ import unicode_literals

from django.db import models
# from django.contrib.auth import get_user_model


class PointManager(models.Manager):
    def applyScore(self, post, score):
        account = post.owner
        point, created = Point.objects.get_or_create(account=account)
        point.points = point.points + score
        point.save()


class Point(models.Model):

    account = models.OneToOneField('accounts.Account', on_delete=models.CASCADE, primary_key=True)
    points = models.IntegerField(default=0)

    objects = PointManager()

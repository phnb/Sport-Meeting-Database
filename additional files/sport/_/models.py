from __future__ import unicode_literals
from django.db import models

# Create your models here.

from django.db import models

class player(models.Model):
    # player_id = models.IntegerField
    player_name = models.CharField(max_length=45)
    gender = models.CharField(max_length=45)
    player_College = models.CharField(max_length=45)

# class college(models.Model):
#     College_name = models.CharField(max_length=45)
#     College_score = models.IntegerField
#     Manager = models.CharField(max_length=45)

# class college_rank(models.Model):
#     College_score = models.IntegerField
#     College_ranking = models.IntergerFiedld

# class event(models.Model):
#     Event_name = models.CharField(max_length= 45)
#     Category = models.CharField(max_length = 45)
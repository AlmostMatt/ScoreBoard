from django.db import models
import datetime
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length = 64)
    secret_code = models.IntegerField(default=0)
    create_date = models.DateTimeField('date registered')
    def __str__(self):
        return '%s (%s)' % (self.id, self.name)
    
class HighScore(models.Model):
    user = models.ForeignKey(User)
    level = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    score_date = models.DateTimeField('date score obtained')
    replay = models.TextField()
    class Meta:
        unique_together = (("user", "level"),)
        ordering = ['level', 'score', 'score_date'] # lower score + longer ago is better
    def __str__(self):
        return self.user.name + ", Level " + str(self.level) + ": " + str(self.score)

class CustomLevel(models.Model):
    creator = models.ForeignKey(User)
    level_data = models.TextField()
    level_name = models.CharField(max_length = 256)
    create_date = models.DateTimeField('date registered')
    
    plays = models.IntegerField(default=0)
    completions = models.IntegerField(default=0)
    ratings = models.IntegerField(default=0)
    total_rating = models.IntegerField(default=0) # total_rating / #ratings = avg rating
    avg_rating = models.FloatField(default=0)
    
    def __str__(self):
        return '%s: %s by %s' % (self.id, self.level_name, self.creator.name)

class MetricCount(models.Model):
    metric = models.CharField(max_length=64)
    n = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    def __str__(self):
        return '%s (%s)' % (self.metric, self.n)

from datetime import date
from unicodedata import name
from django.db import models

# Create your models here.

class Candidates(models.Model):
    candidate_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'candidates'
        


class RawTweets(models.Model):
    tweet_id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    tweet_text = models.TextField()
    word_count = models.IntegerField()
    hashtags = models.CharField(max_length=255)
    retweets = models.IntegerField()
    likes = models.IntegerField()
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)

    class Meta:
        db_table = 'raw_tweets'
        ordering = ['-date']


class AggregateTweets(models.Model):
    collect_id = models.AutoField(primary_key=True)
    date = models.DateField()
    followers_count = models.IntegerField()
    tweets_count = models.IntegerField()
    word_count = models.IntegerField()
    hashtags = models.CharField(max_length=255)
    retweets = models.IntegerField()
    likes = models.IntegerField()
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)

    class Meta:
        db_table = 'aggregate_tweets'
        ordering = ['-date']


class InstaRaw(models.Model):
    post_id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    post_text = models.TextField()
    word_count = models.IntegerField()
    hashtags = models.CharField(max_length=255)
    comments_count = models.IntegerField()
    likes = models.IntegerField()
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)

    class Meta:
        db_table = 'insta_raw'
        ordering = ['-date']


class InstaAggregate(models.Model):
    collect_id = models.AutoField(primary_key=True)
    date = models.DateField()
    followers_count = models.IntegerField()
    posts_count = models.IntegerField()
    word_count = models.IntegerField()
    hashtags = models.CharField(max_length=512)
    comments_count = models.IntegerField()
    likes = models.IntegerField()
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)

    class Meta:
        db_table = 'insta_aggregate'
        ordering = ['-date']
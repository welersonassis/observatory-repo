from pydoc_data.topics import topics
from rest_framework import serializers
from .models import Candidates, AggregateTweets, InstaAggregate, RawTweets, InstaRaw

class CandidatesSerializer(serializers.ModelSerializer):
  class Meta:
    model = Candidates
    fields = '__all__'


class AggregateTweetsSerializer(serializers.ModelSerializer):

  collect_id = serializers.IntegerField(required=False)
  date = serializers.DateField(required=False)
  followers_count = serializers.IntegerField(required=False)
  tweets_count = serializers.IntegerField(required=False)
  word_count = serializers.IntegerField(required=False)
  hashtags = serializers.CharField(required=False)
  retweets = serializers.IntegerField(required=False)
  likes = serializers.IntegerField(required=False)
  candidate = serializers.IntegerField(required=False)


  class Meta:
    model = AggregateTweets
    fields = '__all__'



class InstaAggregateSerializer(serializers.ModelSerializer):

  collect_id = serializers.IntegerField(required=False)
  date = serializers.DateField(required=False)
  followers_count = serializers.IntegerField(required=False)
  posts_count = serializers.IntegerField(required=False)
  word_count = serializers.IntegerField(required=False)
  hashtags = serializers.CharField(required=False)
  comments_count = serializers.IntegerField(required=False)
  likes = serializers.IntegerField(required=False)
  candidate = serializers.IntegerField(required=False)

  class Meta:
    model = InstaAggregate
    fields = '__all__'


    
class RawTweetsSerializer(serializers.ModelSerializer):

  tweet_id = serializers.IntegerField(required=False)
  date = serializers.DateField(required=False)
  tweet_text = serializers.CharField(required=False)
  word_count = serializers.IntegerField(required=False)
  hashtags = serializers.CharField(required=False)
  retweets = serializers.IntegerField(required=False)
  likes = serializers.IntegerField(required=False)
  candidate = serializers.IntegerField(required=False)

  class Meta:
    model = RawTweets
    fields = '__all__'


class InstaRawSerializer(serializers.ModelSerializer):

  post_id = serializers.IntegerField(required=False)
  date = serializers.DateField(required=False)
  post_text = serializers.CharField(required=False)
  word_count = serializers.IntegerField(required=False)
  hashtags = serializers.CharField(required=False)
  comments_count = serializers.IntegerField(required=False)
  likes = serializers.IntegerField(required=False)
  candidate = serializers.IntegerField(required=False)

  class Meta:
    model = InstaRaw
    fields = '__all__'


class HashtagSerializer(serializers.Serializer):
  name = serializers.CharField()
  hashtags = serializers.DictField(child = serializers.IntegerField())


class TopicsSerializer(serializers.Serializer):
  name = serializers.CharField()
  topics = serializers.DictField(child = serializers.IntegerField())

class RankingSerializer(serializers.Serializer):
  saude = serializers.DictField(child = serializers.IntegerField())
  seguranca = serializers.DictField(child = serializers.IntegerField())
  saneamento = serializers.DictField(child = serializers.IntegerField())
  educacao = serializers.DictField(child = serializers.IntegerField())

class SpaceSerializer(serializers.Serializer):
  candidate = serializers.CharField()
  saude = serializers.DecimalField(max_digits=5, decimal_places=3)
  seguranca = serializers.DecimalField(max_digits=5, decimal_places=3)
  saneamento = serializers.DecimalField(max_digits=5, decimal_places=3)
  educacao = serializers.DecimalField(max_digits=5, decimal_places=3)
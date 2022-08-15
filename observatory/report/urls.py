from django.urls import path
from . import views


urlpatterns = [
    path('twitter_followers_count', views.twitter_followers_count, name='twitter_followers_count'),
    path('candidate/<int:pk>', views.candidate, name='candidate'),
    path('candidate_hashtags', views.candidate_hashtags, name='candidate_hashtags'),
    path('twitter_likes_count', views.twitter_likes_count, name='twitter_likes_count'),
    path('retweets_count', views.retweets_count, name='retweets_count'),
    path('candidate_topics', views.candidate_topics, name='candidate_topics'),
    path('candidate_ranking', views.candidate_ranking, name='candidate_ranking'),
    path('space_topic', views.space_topic, name='space_topic'),
    
]
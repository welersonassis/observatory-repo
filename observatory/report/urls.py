from django.urls import path
from . import views


urlpatterns = [
    path('followers_count', views.followers_count, name='followers_count'),
    path('candidate/<int:pk>', views.candidate, name='candidate'),
    path('candidate_hashtags', views.candidate_hashtags, name='candidate_hashtags'),
    path('likes_count', views.likes_count, name='likes_count'),
    path('retweets_count', views.retweets_count, name='retweets_count'),
    path('candidate_topics', views.candidate_topics, name='candidate_topics'),
    path('candidate_ranking', views.candidate_ranking, name='candidate_ranking'),
    path('space_topic', views.space_topic, name='space_topic'),
    path('insta_comments_count', views.insta_comments_count, name='insta_comments_count'),
    path('posts_count', views.posts_count, name='posts_count'),
    
]
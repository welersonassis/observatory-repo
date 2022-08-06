import re
from django.shortcuts import render
from .models import AggregateTweets, RawTweets, InstaAggregate, InstaRaw, Candidates
from django.db import connection, transaction
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from unidecode import unidecode
from .serializers import (
    HashtagSerializer,
    CandidatesSerializer, 
    AggregateTweetsSerializer, 
    RawTweetsSerializer, 
    InstaAggregateSerializer, 
    InstaRawSerializer,
    TopicsSerializer
    ) 
from django.db.models import Q
from datetime import datetime, timedelta


@api_view(['GET'])
def candidate(request,pk):
    try:
        candidate = Candidates.objects.get(pk=pk)
    except candidate.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CandidatesSerializer(candidate)
        return Response(serializer.data)


# Metrics

@api_view(['GET'])
def twitter_followers_count(request):

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    date_to = date_to.strftime('%Y-%m-%d')
    date_from = date_from.strftime('%Y-%m-%d')

    try:
        agg_tweets = AggregateTweets.objects.filter(date__range=[date_from, date_to]).values('date', 'followers_count', 'candidate')
    except candidate.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AggregateTweetsSerializer(agg_tweets,many=True)
        return Response(serializer.data)


@api_view(['GET'])
def twitter_likes_count(request):

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    date_to = date_to.strftime('%Y-%m-%d')
    date_from = date_from.strftime('%Y-%m-%d')

    try:
        agg_tweets = AggregateTweets.objects.filter(date__range=[date_from, date_to]).values('date', 'likes', 'candidate')
    except candidate.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AggregateTweetsSerializer(agg_tweets,many=True)
        return Response(serializer.data)

@api_view(['GET'])
def retweets_count(request):

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    date_to = date_to.strftime('%Y-%m-%d')
    date_from = date_from.strftime('%Y-%m-%d')

    try:
        agg_tweets = AggregateTweets.objects.filter(date__range=[date_from, date_to]).values('date', 'retweets', 'candidate')
    except candidate.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AggregateTweetsSerializer(agg_tweets,many=True)
        return Response(serializer.data)



@api_view(['GET'])
def candidate_hashtags(request):

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    date_to = date_to.strftime('%Y-%m-%d')
    date_from = date_from.strftime('%Y-%m-%d')

    with transaction.atomic(), connection.cursor() as cur:
        cur.execute(f"""
                SELECT
                    c.name,
                    array_to_string(array_agg(r.hashtags), ',')
                FROM raw_tweets r
                LEFT JOIN candidates c ON c.candidate_id = r.candidate_id 
                WHERE r.date BETWEEN '{date_from}' AND '{date_to}'
                GROUP BY c.name
        """)

        results = cur.fetchall()

        data = [ {'name':row[0], 'hashtags':row[1]} for row in results ]

        for row in data:
            row['hashtags'] = [ hash for hash in row['hashtags'].split(',') if hash]
            if row['hashtags']:
                row['hashtags'] = hashtags_count(row['hashtags'])
            else:
                row['hashtags'] = {}


    if request.method == 'GET':
        serializer = HashtagSerializer(data,many=True)
        return Response(serializer.data)
        

@api_view(['GET'])
def candidate_topics(request):

    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    date_to = date_to.strftime('%Y-%m-%d')
    date_from = date_from.strftime('%Y-%m-%d')

    with transaction.atomic(), connection.cursor() as cur:
        cur.execute(f"""
                SELECT
                    c.name,
                    array_to_string(array_agg(r.tweet_text), '')
                FROM raw_tweets r
                LEFT JOIN candidates c ON c.candidate_id = r.candidate_id 
                WHERE r.date BETWEEN '{date_from}' AND '{date_to}'
                GROUP BY c.name
        """)

        results = cur.fetchall()

        data = [ {'name':row[0], 'text':row[1]} for row in results ]

        for row in data:
            if row['text']:
                row['text'] = word_cleaning(row['text']).replace('\n', '')
                row['topics'] = dictionary_score(row['text'])
                row.pop('text', None)
            else:
                row['topics'] = {}
                row.pop('text', None)


    if request.method == 'GET':
        serializer = TopicsSerializer(data,many=True)
        return Response(serializer.data)


#Functions

def hashtags_count(hahs_list):
    counts = dict()
    words = hahs_list

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts


def word_cleaning(insta_text):
    # Cleaning
    insta_text = re.sub("@[A-Za-z0-9_]+","", insta_text)
    insta_text = re.sub("#[A-Za-z0-9_]+","", insta_text)
    insta_text = re.sub(r"http\S+", "", insta_text)
    insta_text = re.sub(r"www.\S+", "", insta_text)
    insta_text = re.sub('[()!?]', ' ', insta_text)
    insta_text = re.sub('\[.*?\]',' ', insta_text)
    insta_text = re.sub(r'[^\w\s]', '', insta_text)
    
    return insta_text




def dictionary_score(text):

    word_dict = {}

    health = ['saude', 'hospital', 'medico', 'enfermeiro', 'vacina',
    'seguranca', 'policia', 'violencia', 'saneamento', 'educacao', 'ensino',
    'escola', 'universidade', 'faculdade']

    for row in text.split():
        if unidecode(row.lower()) in health:
            if row.lower() in word_dict:
                word_dict[row.lower()] += 1
            else:
                word_dict[row.lower()] = 1

    return word_dict
            

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
    TopicsSerializer,
    RankingSerializer,
    SpaceSerializer
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
    date_from = date_to - timedelta(days=8)
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


@api_view(['GET'])
def candidate_ranking(request):

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

        topic_list = []

        for row in data:
            if row['text']:
                row['text'] = word_cleaning(row['text']).replace('\n', '')
                tmp = ranking_topic(row['name'],row['text'])
                topic_list.append(tmp)
            else:
                tmp = {'candidate':row['name'], 'health':0, 'security':0, 'infra':0, 'education':0}

        data = {'saude':'name', 'seguranca':'name', 'saneamento':'name', 'educacao':'name'}

        tmp_saude = {}
        tmp_seg = {}
        tmp_infra = {}
        tmp_edu = {}

        for row in topic_list:
            tmp_saude[row['candidate']] = row['health']
            tmp_seg[row['candidate']] = row['security'] 
            tmp_infra[row['candidate']] = row['infra'] 
            tmp_edu[row['candidate']] = row['education']  

        data['saude'] = tmp_saude
        data['seguranca'] = tmp_seg          
        data['saneamento'] = tmp_infra
        data['educacao'] = tmp_edu

        data = [data]

    if request.method == 'GET':
        serializer = RankingSerializer(data,many=True)
        return Response(serializer.data)


@api_view(['GET'])
def space_topic(request):

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

        topic_list = []

        for row in data:
            if row['text']:
                row['text'] = word_cleaning(row['text']).replace('\n', '')
                tmp = ranking_topic(row['name'],row['text'])
                tmp['word_count'] = len(row['text'].split())
                topic_list.append(tmp)
            else:
                tmp = {'candidate':row['name'], 'health':0, 'security':0, 'infra':0, 'education':0, 'word_count':1}

        for row in topic_list:
            row['saude'] = round((row['health'] / row['word_count'])*100, 3)
            row['seguranca'] = round((row['security'] / row['word_count'])*100, 3)
            row['saneamento'] = round((row['infra'] / row['word_count'])*100, 3)
            row['educacao'] = round((row['education'] / row['word_count'])*100, 3)
            row.pop('health', None)
            row.pop('word_count', None)
            row.pop('security', None)
            row.pop('infra', None)
            row.pop('education', None)         

        data = topic_list

    if request.method == 'GET':
        serializer = SpaceSerializer(data,many=True)
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

    health = ['saude', 'hospital', 'hospitais', 'medico', 'medicos', 'enfermeiro', 'enfermeiros',
    'vacina', 'vacinas', 'remedio', 'remedios', 'uti', 'utis', 'leito', 'leitos', 'upa', 'upas', 
    'medicina', 'sus', 'medicamento', 'medicamentos']
    security = ['seguranca', 'policia', 'policiais', 'violencia', 'armas', 'desarmamento', 'mortes', 'assaltos', 'roubos', 'latrocinio', 'impunidade']
    infra = ['saneamento', 'esgoto']
    education = ['educacao', 'ensino', 'escola', 'escolas', 'universidade', 'universidades', 'faculdade', 'faculdades', 'estudantes', 'estudante', 'prouni', 'fies']

    topics = health + security + infra + education

    for row in text.split():
        if unidecode(row.lower()) in topics:
            if row.lower() in word_dict:
                word_dict[row.lower()] += 1
            else:
                word_dict[row.lower()] = 1

    return word_dict


def ranking_topic(candidate,text):

    word_dict = {'candidate':candidate, 'health':0, 'security':0, 'infra':0, 'education':0}

    health = ['saude', 'hospital', 'hospitais', 'medico', 'medicos', 'enfermeiro', 'enfermeiros',
    'vacina', 'vacinas', 'remedio', 'remedios', 'uti', 'utis', 'leito', 'leitos', 'upa', 'upas', 
    'medicina', 'sus', 'medicamento', 'medicamentos']
    security = ['seguranca', 'policia', 'policiais', 'violencia', 'armas', 'desarmamento', 'mortes', 'assaltos', 'roubos', 'latrocinio', 'impunidade']
    infra = ['saneamento', 'esgoto']
    education = ['educacao', 'ensino', 'escola', 'escolas', 'universidade', 'universidades', 'faculdade', 'faculdades', 'estudantes', 'estudante', 'prouni', 'fies']

    for row in text.split():
        if unidecode(row.lower()) in health:
            word_dict['health'] += 1
        if unidecode(row.lower()) in security:
            word_dict['security'] += 1
        if unidecode(row.lower()) in infra:
            word_dict['infra'] += 1
        if unidecode(row.lower()) in education:
            word_dict['education'] += 1

    return word_dict
            

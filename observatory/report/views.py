import re
import pytz
from django.shortcuts import render
from .models import AggregateTweets, RawTweets, InstaAggregate, InstaRaw, Candidates
from django.db import connection, transaction
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from unidecode import unidecode
from .serializers import (
    FollowersSerializer,
    LikesSerializer,
    CommentsSerializer,
    PostsCountSerializer,
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

tzconfig = pytz.timezone("America/Fortaleza")

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
def followers_count(request):

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_from = datetime.strptime(date_from,'%Y-%m-%d')
        date_from = date_from - timedelta(days=1)
        date_from = date_from.strftime('%Y-%m-%d')
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=8)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                        WITH base AS (
                            SELECT date, followers_count, candidate_id,
                            LAG(followers_count,1) OVER (
                                    PARTITION BY candidate_id
                                    ORDER BY date
                                ) prev_count
                            FROM aggregate_tweets
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
                        )

                        SELECT * FROM base WHERE prev_count IS NOT NULL
            """)
            results = cur.fetchall()

    else:
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                        WITH base AS (
                            SELECT date, followers_count, candidate_id,
                            LAG(followers_count,1) OVER (
                                    PARTITION BY candidate_id
                                    ORDER BY date
                                ) prev_count
                            FROM insta_aggregate
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
                        )

                        SELECT * FROM base WHERE prev_count IS NOT NULL
            """)

            results = cur.fetchall()

    data = [ {'date':row[0], 'followers_count':row[1], 'candidate':row[2], 'prev_count':row[3]} for row in results ]

    for row in data:
        row['followers_count'] = row['followers_count'] - row['prev_count']
        row['followers_relative'] = row['followers_count'] / row['prev_count']
        row.pop('prev_count', None)



    if request.method == 'GET':
        serializer = FollowersSerializer(data,many=True)
        return Response(serializer.data)





@api_view(['GET'])
def likes_count(request):

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                            SELECT 
                                date,
                                likes,
                                CASE WHEN tweets_count = 0 THEN 0 ELSE likes/tweets_count END AS likes_by_post,
                                candidate_id
                            FROM aggregate_tweets
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
            """)
            results = cur.fetchall()

            data = [ {'date':row[0], 'likes_count':row[1], 'likes_by_post':row[2], 'candidate':row[3]} for row in results ]

    else:
        date_to = datetime.strptime(date_to,'%Y-%m-%d')
        date_to = date_to + timedelta(days=1)
        date_to = date_to.strftime('%Y-%m-%d')
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                            SELECT 
                                TO_CHAR(date, 'YYYY-MM-DD') AS date,
                                SUM(likes)/COUNT(CASE WHEN likes != 0 THEN post_id END) AS likes_by_post,
                                candidate_id
                            FROM insta_raw
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
                            GROUP BY TO_CHAR(date, 'YYYY-MM-DD'), candidate_id
            """)
            results = cur.fetchall()

            data = [ {'date':row[0], 'likes_by_post':row[1], 'candidate':row[2]} for row in results ]


    if request.method == 'GET':
        serializer = LikesSerializer(data,many=True)
        return Response(serializer.data)

@api_view(['GET'])
def posts_count(request):

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                            SELECT 
                                date,
                                tweets_count,
                                candidate_id
                            FROM aggregate_tweets
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
            """)
            results = cur.fetchall()

    else:
        date_to = datetime.strptime(date_to,'%Y-%m-%d')
        date_to = date_to + timedelta(days=1)
        date_to = date_to.strftime('%Y-%m-%d')
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                            SELECT 
                                date,
                                posts_count,
                                candidate_id
                            FROM insta_aggregate
                            WHERE date BETWEEN '{date_from}' AND '{date_to}'
            """)
            results = cur.fetchall()

    data = [ {'date':row[0], 'posts_count':row[1], 'candidate':row[2]} for row in results ]


    if request.method == 'GET':
        serializer = PostsCountSerializer(data,many=True)
        return Response(serializer.data)

@api_view(['GET'])
def retweets_count(request):

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
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
def insta_comments_count(request):

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    with transaction.atomic(), connection.cursor() as cur:
        cur.execute(f"""
                        SELECT 
                            TO_CHAR(date, 'YYYY-MM-DD') AS date,
                            SUM(comments_count)/COUNT(CASE WHEN comments_count != 0 THEN post_id END) AS comments_by_post,
                            candidate_id
                        FROM insta_raw
                        WHERE date BETWEEN '{date_from}' AND '{date_to}'
                        GROUP BY TO_CHAR(date, 'YYYY-MM-DD'), candidate_id
        """)
        results = cur.fetchall()

        data = [ {'date':row[0], 'comments_by_post':row[1], 'candidate':row[2]} for row in results ]

    if request.method == 'GET':
        serializer = CommentsSerializer(data,many=True)
        return Response(serializer.data)



@api_view(['GET'])
def candidate_hashtags(request):

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

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

    else:
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                    SELECT
                        c.name,
                        array_to_string(array_agg(r.hashtags), ',')
                    FROM insta_raw r
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

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

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

    else:
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                    SELECT
                        c.name,
                        array_to_string(array_agg(r.post_text), '')
                    FROM insta_raw r
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

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

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

    else:
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                    SELECT
                        c.name,
                        array_to_string(array_agg(r.post_text), '')
                    FROM insta_raw r
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

    media = request.query_params['media']

    if 'start' in request.query_params and 'end' in request.query_params:
        date_from = request.query_params['start']
        date_to = request.query_params['end']
    else:
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        date_to = date_to.astimezone(tzconfig)
        date_from = date_from.astimezone(tzconfig)
        date_to = date_to.strftime('%Y-%m-%d')
        date_from = date_from.strftime('%Y-%m-%d')

    if media == 'twitter':

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

    else:
        with transaction.atomic(), connection.cursor() as cur:
            cur.execute(f"""
                    SELECT
                        c.name,
                        array_to_string(array_agg(r.post_text), '')
                    FROM insta_raw r
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
            

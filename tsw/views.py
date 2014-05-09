from django.views.decorators.csrf import csrf_exempt  
from django.shortcuts import render
import json
from tsw.models import *
from django.http import HttpResponse, Http404
from django.utils import timezone

from random import randint
import math

@csrf_exempt   
def new_user(request, name):
    u = User.objects.create(name=name, create_date=timezone.now(), secret_code=randint(0, 100000))
    response_data = {
        'user_id' : u.id,
        'secret' : u.secret_code,
        'name' : u.name,
        'create_date' : str(u.create_date)
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt   
def change_name(request, user_id, name):
    # add a password (or a "secret" random number)
    # the user could download all of their best scores and replays if they have password association
    try:
        u = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404
    u.name = name
    u.save()
    response_data = {
        'user_id' : u.id,
        'name' : u.name,
        'create_date' : str(u.create_date)
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

    
# HIGH SCORES

@csrf_exempt   
def save_score(request):
    user_id = int(request.POST.get("user_id"))
    level = int(request.POST.get("level"))
    score = int(request.POST.get("score"))
    replay = request.POST.get("replay", "")
    try:
        u = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404
    highscore, created = HighScore.objects.get_or_create(user_id=user_id, level=level, defaults={'score_date' : timezone.now()})
    if created or score < highscore.score:
        highscore.score = score
        highscore.score_date = timezone.now()
        highscore.replay = replay
        highscore.save()
    response_data = {
        'user_id' : highscore.user_id,
        'level' : highscore.level,
        'score' : highscore.score,
        'score_date' : str(highscore.score_date),
        'replay' : replay
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_scores(request):
    user_id = int(request.GET.get("user_id", 0))
    level = int(request.GET.get("level", 0))
    page_size = int(request.GET.get("page_size", 3))
    
    # if the user is in the top 2x page_size or has not completed the level, return the top 2x page size
    # otherwise, return the top page_size and the page_size group centered around the current user
    # should probably half page size instead of doublign it (and subtract 1 for the ...)
    
    scores = HighScore.objects.filter(level=level)
    scores = [{'user_id' : score.user_id, 'user_name' : score.user.name, 'score' : score.score, 'replay' : score.replay, 'rank' : (ind+1)} for ind, score in enumerate(scores)]
    rank = None
    for score in scores:
        # do not return the user_ids, just use them to determine the rank of the current user
        if score.get('user_id') == user_id:
            rank = score.get('rank')
        #del score['user_id']
    top_scores = scores[:2 * page_size]
    other_scores = []
    if rank is not None and rank > 2 * page_size:
        top_scores = scores[:page_size]
        other_scores = scores[rank-math.ceil(page_size/2): rank+math.floor(page_size/2)]
    response_data = {
        'top_scores' : top_scores,
        'other_scores' : other_scores,
        'num_scores' : len(scores)
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")

    
# USER CREATED LEVELS
    
@csrf_exempt   
def save_level(request):
    user_id = int(request.POST.get("user_id"))
    level_name = request.POST.get("level_name")
    level_data = request.POST.get("level_data")
    
    try:
        u = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404
    level = CustomLevel.objects.create(creator_id=user_id, level_name=level_name, level_data=level_data, create_date=timezone.now())
    response_data = {
        'creator' : level.creator.name,
        'level_id' : level.id,
        'level_name' : level.level_name,
        'level_data' : level.level_data
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_levels(request):
    user_id = int(request.GET.get("user_id", 0))
    offset = int(request.GET.get("offset", 0))
    mode = request.GET.get("mode", "New") # "Popular", "New", "Top Rated"
    page_size = int(request.GET.get("page_size", 8))
    
    levels = CustomLevel.objects.all()[offset:offset+page_size]
    levels = [{'level_name' : level.level_name, 'level_id' : level.id, 'creator' : level.creator_id, 'creator_name' : level.creator.name, 'level_data' : level.level_data, 'rating' : level.avg_rating} for level in levels]
    response_data = {
        'levels' : levels,
        'num_levels' : len(levels)
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def rate_level(request):
    user_id = int(request.GET.get("user_id", 0))
    level = int(request.GET.get("level"))
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def played_level(request):
    user_id = int(request.GET.get("user_id", 0))
    level = int(request.GET.get("level"))
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
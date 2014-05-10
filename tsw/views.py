from django.views.decorators.csrf import csrf_exempt  
from django.shortcuts import render
import json
from tsw.models import *
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied

from django.utils import timezone
from datetime import timedelta

from random import randint
import math

@csrf_exempt   
def new_user(request, name):
    u = User.objects.create(name=name, create_date=timezone.now(), secret_code=randint(0, 100000))
    response_data = {
        'user_id' : u.id,
        'secret_code' : u.secret_code,
        'name' : u.name,
        'create_date' : str(u.create_date)
    }
    response = HttpResponse(json.dumps(response_data), content_type="application/json")
    return response

@csrf_exempt   
def change_name(request, user_id, name):
    # add a password (or a "secret" random number)
    # the user could download all of their best scores and replays if they have password association
    secret_code = int(request.POST.get("secret_code"))
    
    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

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
    secret_code = int(request.POST.get("secret_code"))
    
    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()
    
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
    page_size = int(request.GET.get("page_size", 16))
    mode = request.GET.get("mode", "New") # "Daily", "Weekly", "Monthly", "All Time"
    
    # if the user is in the top page_size or has not completed the level, return the top page size
    # otherwise, return the top page_size/2 and the page_size/2 group centered around the current user
    # if the user is in the bottom page_size/4 users, the bottom page_size/4 is used instead of being centered on the user

    # if the user is not in the top page_size, 1 fewer entry is returned since the client will indicate a ... between the areas
    
    start_time = None
    if mode == "Daily":
        start_time = timezone.now() - timedelta(hours=24)
    elif mode == "Weekly":
        start_time = timezone.now() - timedelta(days=7)
    elif mode == "Monthly":
        start_time = timezone.now() - timedelta(days=30)
        
    if start_time is None:
        scores = HighScore.objects.filter(level=level)
    else:
        scores = HighScore.objects.filter(level=level, score_date__gte=start_time)
    
    scores = [{'user_id' : score.user_id, 'user_name' : score.user.name, 'score' : score.score, 'replay' : score.replay, 'rank' : (ind+1)} for ind, score in enumerate(scores)]
    rank = None
    for score in scores:
        # do not return the user_ids, just use them to determine the rank of the current user
        if score.get('user_id') == user_id:
            rank = score.get('rank')
        #del score['user_id']
    top_scores = scores[:page_size]
    other_scores = []
    if rank is not None and rank > page_size:
        top_scores = scores[:math.floor((page_size-1)/2)]
        num_other_scores = math.ceil((page_size-1)/2)
        if rank > len(scores) - math.floor(num_other_scores/2):
            other_scores = scores[-num_other_scores:]
        else:
            other_scores = scores[rank-math.ceil(num_other_scores/2): rank+math.floor(num_other_scores/2)]
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
    secret_code = int(request.POST.get("secret_code"))
    
    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()
    level = CustomLevel.objects.create(creator_id=user_id, level_name=level_name, level_data=level_data, create_date=timezone.now(), ratings=1, avg_rating=10, total_rating=10, plays=1, completions=1)
    response_data = {
        'creator' : level.creator.name,
        'level_id' : level.id,
        'level_name' : level.level_name,
        'level_data' : level.level_data
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_level(request):
    user_id = int(request.GET.get("user_id", 0))
    level = int(request.POST.get("level"))
    
    lvl = None
    try:
        lvl = CustomLevel.objects.get(pk=level)
    except CustomLevel.DoesNotExist:
        raise Http404
    
    response_data = {
        'level_name' : lvl.level_name,
        'level_id' : lvl.id,
        'creator' : lvl.creator_id,
        'creator_name' : lvl.creator.name,
        'level_data' : lvl
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def get_levels(request):
    user_id = int(request.GET.get("user_id", 0))
    offset = int(request.GET.get("offset", 0))
    mode = request.GET.get("mode", "New") # "Popular", "New", "Top Rated"
    page_size = int(request.GET.get("page_size", 8))
    
    levels = []
    if mode == "Popular":
        levels = CustomLevel.objects.all()
    elif mode == "New":
        levels = CustomLevel.objects.order_by('-create_date')
    elif mode == "Top Rated":
        levels = CustomLevel.objects.order_by('-avg_rating')
        
    levels = levels[offset:offset+page_size]
    levels = [{'level_name' : level.level_name, 'level_id' : level.id, 'creator' : level.creator_id, 'creator_name' : level.creator.name, 'level_data' : level.level_data, 'rating' : level.avg_rating} for level in levels]
    response_data = {
        'levels' : levels,
        'num_levels' : len(levels)
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@csrf_exempt   
def rate_level(request):
    user_id = int(request.POST.get("user_id", 0))
    level = int(request.POST.get("level"))
    rating = int(request.POST.get("rating"))
    secret_code = int(request.POST.get("secret_code"))

    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

    lvl = None
    try:
        lvl = CustomLevel.objects.get(pk=level)
    except CustomLevel.DoesNotExist:
        raise Http404
    # Don't rate your own level
    if lvl.creator_id != user_id:
        lvl.total_rating += rating
        lvl.ratings += 1
        lvl.avg_rating = lvl.total_rating / lvl.ratings
        lvl.save()
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt   
def played_level(request):
    user_id = int(request.POST.get("user_id", 0))
    level = int(request.POST.get("level"))
    secret_code = int(request.POST.get("secret_code"))

    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

    lvl = None
    try:
        lvl = CustomLevel.objects.get(pk=level)
    except CustomLevel.DoesNotExist:
        raise Http404
    # Don't count additional plays of your own level
    if lvl.creator_id != user_id:
        lvl.plays += 1
        lvl.save()
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt   
def completed_level(request):
    user_id = int(request.POST.get("user_id", 0))
    level = int(request.POST.get("level"))
    secret_code = int(request.POST.get("secret_code"))

    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

    lvl = None
    try:
        lvl = CustomLevel.objects.get(pk=level)
    except CustomLevel.DoesNotExist:
        raise Http404
    # Don't count additional plays of your own level
    if lvl.creator_id != user_id:
        lvl.completions += 1
        lvl.save()
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
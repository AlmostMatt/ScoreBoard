from django.views.decorators.csrf import csrf_exempt  
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from tsw.models import *

from datetime import timedelta
from random import randint
import json
import math


def _increment_metric(metric, n=0):
    metric_count, created = MetricCount.objects.get_or_create(metric=metric, n=n, defaults={'count': 1}) 
    if not created:
        metric_count.count += 1
        metric_count.save()

def server_info(request):
    domain = request.GET.get('domain', 'UNKNOWN')
    # count how many times people hit the shell
    _increment_metric('server_info')
    _increment_metric('domain: %s' % domain)
    response_data = {
        # base url should not have http, swf url can
        'base_url': 'www.almostmatt.com/dj/tsw',
        'swf_url': 'http://www.almostmatt.com/tsw/tsw_v0.swf'
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def log_metric(request):
    user_id = int(request.POST.get("user_id"))
    metric = request.POST.get("metric")
    n = int(request.POST.get("n", 0))
    #secret_code = int(request.POST.get("secret_code"))
    #try:
    #    u = User.objects.get(pk=user_id)
    #    if u.secret_code != secret_code:
    #        raise PermissionDenied()
    #except User.DoesNotExist:
    #    raise PermissionDenied()
    _increment_metric(metric, n)
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt   
def new_user(request):
    name = request.POST.get("name", "")
    if name == "": name = "Anon%s" % randint(100, 9999) # duplicates are OK
    u = User.objects.create(name=name, create_date=timezone.now(), secret_code=randint(0, 1000000000))
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
    
    try:   
        player_score = HighScore.objects.get(level=level, user_id=user_id)
        if start_time is None:
            better_scores = HighScore.objects.filter(level=level, score__lt=player_score.score)
            worse_scores = HighScore.objects.filter(level=level, score__gte=player_score.score)
        else:
            better_scores = HighScore.objects.filter(level=level, score__lt=player_score.score, score_date__gte=start_time)
            worse_scores = HighScore.objects.filter(level=level, score__gte=player_score.score, score_date__gte=start_time)
        rank = better_scores.count() + 1
        num_scores = rank + worse_scores.count() - 1 # currently the player's score is in worse scores
        worse_scores = worse_scores.exclude(user_id=user_id)
        
    except HighScore.DoesNotExist:
        if start_time is None:
            better_scores = HighScore.objects.filter(level=level)
        else:
            better_scores = HighScore.objects.filter(level=level, score_date__gte=start_time)
        worse_scores = []
        rank = None
        num_scores = better_scores.count()

    if rank is not None and rank > page_size:
        # note that getting the last elements of a query set might be expensive. also query better, worse, player, anc ount better, worse ...
        top_scores = list(better_scores[:(page_size-1)/2])
        num_other_scores = page_size/2
        if rank > num_scores - (num_other_scores/2):
            # last page
            other_scores = zip(range(num_scores + 1 - num_other_scores, num_scores + 1),
                               list(better_scores[num_scores - num_other_scores:]) + [player_score] + list(worse_scores))
        else:
            # some page in the middle
            num_before_p = (num_other_scores+1)/2 - 1 
            num_after_p = num_other_scores/2
            other_scores = zip(range(rank - num_before_p, rank + num_after_p + 1),
                               list(better_scores[rank - 1 - num_before_p:]) + [player_score] + list(worse_scores[:num_after_p]))
    elif rank <= page_size:
        top_scores = list(better_scores) + [player_score] + list(worse_scores[:page_size-rank])
        other_scores = []
    else:
        top_scores = list(better_scores[:page_size])
        other_scores = []
    
    response_data = {
        'top_scores' : scores_json(zip(range(1, len(top_scores) + 1), top_scores)),
        'other_scores' : scores_json(other_scores),
        'num_scores' : num_scores
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def scores_json(scores_zipped):
    return [
        {'user_id' : score.user_id,
         'user_name' : score.user.name,
         'score' : score.score,
         'replay' : score.replay,
         'rank' : rank
        } for rank, score in scores_zipped]
 
# USER CREATED LEVELS
    
@csrf_exempt   
def save_level(request):
    user_id = int(request.POST.get("user_id"))
    level_name = request.POST.get("level_name")
    level_data = request.POST.get("level_data")
    level_id = request.POST.get("level_id", None)
    secret_code = int(request.POST.get("secret_code"))
    
    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()
    
    if level_id is None:
        # create a new level
        level = CustomLevel.objects.create(creator_id=user_id, level_name=level_name, level_data=level_data,
            create_date=timezone.now(), ratings=1, avg_rating=10, total_rating=10, plays=1, completions=1)
    else:
        # update an existing level
        try:
            level = CustomLevel.objects.get(pk=level_id)
        except CustomLevel.DoesNotExist:
            raise Http404
        if level.creator_id != user_id:
            raise PermissionDenied()
        level.level_name = level_name
        level.level_data = level_data
        level.save()

    response_data = {
        'creator' : level.creator.name,
        'share_url' : 'www.almostmatt.com/tsw/?level=%s' % level.id,
        'level_id' : level.id,
        'level_name' : level.level_name,
        'level_data' : level.level_data
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_level(request):
    user_id = int(request.GET.get("user_id", 0))
    level = int(request.GET.get("level"))
    
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
        'level_data' : lvl.level_data,
        'rating' : lvl.avg_rating
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
def get_levels(request):
    user_id = int(request.GET.get("user_id", 0))
    offset = int(request.GET.get("offset", 0))
    mode = request.GET.get("mode", "New") # "Popular", "New", "Top Rated"
    page_size = int(request.GET.get("page_size", 6))
    
    levels = []
    if mode == "Popular":
        levels = CustomLevel.objects.order_by('-plays')
    elif mode == "New":
        levels = CustomLevel.objects.order_by('-create_date')
    elif mode == "Top Rated":
        levels = CustomLevel.objects.order_by('-avg_rating')
    elif mode == "My Levels":
        levels = CustomLevel.objects.filter(creator__id=user_id)
    numlevels = levels.count()
    
    levels = levels[offset:offset+page_size]
    levels = [{
                'level_name' : level.level_name,
                'level_id' : level.id,
                'creator_name' : level.creator.name,
                'level_data' : level.level_data,
                'rating' : level.avg_rating,
                'plays' : level.plays
              } for level in levels]
    response_data = {
        'levels' : levels,
        'num_levels' : numlevels
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
        lvl.avg_rating = lvl.total_rating / float(lvl.ratings)
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
    # if lvl.creator_id != user_id:
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

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required

from tsw.models import *

import urllib2
from datetime import timedelta
from random import randint
import json
import math


@csrf_exempt
def save_score(request):
    user_id = int(request.POST.get("user_id", "-1"))
    if (user_id == -1):
        raise PermissionDenied()
    level = int(request.POST.get("level"))
    score = int(request.POST.get("score"))
    replay = request.POST.get("replay", "")
    secret_code = int(request.POST.get("secret_code").strip("/"))

    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

    # it's important to set all the fields during the create of a score is created with a score of 0
    highscore, created = HighScore.objects.get_or_create(user_id=user_id, level=level,
            defaults={'score': score, 'replay': replay, 'score_date' : timezone.now()})
    if not created and score < highscore.score:
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
    page_size = int(request.GET.get("page_size", "16").strip('/'))
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

    is_top_player = False
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
    elif rank is not None and rank <= page_size:
        is_top_player = True
        top_scores = list(better_scores) + [player_score] + list(worse_scores[:page_size-rank])
        other_scores = []
    else:
        top_scores = list(better_scores[:page_size])
        other_scores = []

    response_data = {
        'top_scores' : scores_json(zip(range(1, len(top_scores) + 1), top_scores), True), # is_top_player
        'other_scores' : scores_json(other_scores, True),
        'num_scores' : num_scores
    }
    # do not return replays if the current user has not completed the level
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def scores_json(scores_zipped, replays=True):
    return [
        {'user_id' : score.user_id,
         'user_name' : score.user.name,
         'score' : score.score,
         'replay' : score.replay if replays else None,
         'rank' : rank
        } for rank, score in scores_zipped]


@csrf_exempt
def flag_replay(request):
    response_data = {}
    return HttpResponse(json.dumps(response_data), content_type="application/json")



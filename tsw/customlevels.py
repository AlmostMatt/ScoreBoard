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
def save_level(request):
    user_id = int(request.POST.get("user_id"))
    level_name = request.POST.get("level_name")
    level_data = request.POST.get("level_data")
    level_id = request.POST.get("level_id", None)
    secret_code = int(request.POST.get("secret_code").strip('/'))

    try:
        u = User.objects.get(pk=user_id)
        if u.secret_code != secret_code:
            raise PermissionDenied()
    except User.DoesNotExist:
        raise PermissionDenied()

    if level_id is None:
        # create a new level
        level = CustomLevel.objects.create(creator_id=user_id, level_name=level_name[:63], level_data=level_data,
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
        levels = CustomLevel.objects.filter(avg_rating__gte=6.0).order_by('-plays')
    elif mode == "New":
        levels = CustomLevel.objects.order_by('-create_date')
    elif mode == "Top Rated":
        levels = CustomLevel.objects.filter(ratings__gte=2).order_by('-avg_rating')
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



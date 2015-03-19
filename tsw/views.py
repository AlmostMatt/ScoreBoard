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


def _increment_metric(metric, n=0):
    metric_count, created = MetricCount.objects.get_or_create(metric=metric, n=n, defaults={'count': 1})
    if not created:
        metric_count.count += 1
        metric_count.save()

def server_info(request):
    domain = request.GET.get('domain', 'UNKNOWN').strip('/')
    domain = urllib2.unquote(domain) # %20 to space, etc
    version = int(request.GET.get('version', '0').strip('/'))
    # count how many times people hit the shell
    _increment_metric('server_info', version)
    _increment_metric('domain: %s' % domain, version)
    response_data = {
        # base url should not have http, swf url can
        'base_url': 'www.almostmatt.com/dj/tsw',
        'swf_url': 'http://www.almostmatt.com/tsw/tsw_v0.swf' # % version
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def log_metric(request):
    #user_id = int(request.POST.get("user_id", 0))
    metric = request.POST.get("metric", 'None')
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
    domain = request.POST.get("domain", None)
    referrer = request.META.get('HTTP_REFERER', None)

    if name == "":
        name = "Anon%s" % randint(100, 9999) # duplicates are OK
        _increment_metric("anonymous")

    # with shell, shell sets domain and it is passed as an arg
    # with inner, the request comes from where it is hosted
    if referrer and (domain is None or domain.strip("/") == "<not set>"):
        ref_split = referrer.split("//")
        domain = ref_split[0] if len(ref_split) == 1 else ref_split[1]
        domain = domain.split("/")[0]
    if domain:
        _increment_metric("new_user: %s" % domain.strip("/"))

    u = User.objects.create(name=name[:63], create_date=timezone.now(),
                            secret_code=randint(0, 1000000000), domain=domain)
    response_data = {
        'user_id' : u.id,
        'secret_code' : u.secret_code,
        'name' : u.name,
        'create_date' : str(u.create_date),
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


def get_domain_update(request):
    user_id = int(request.GET.get("user_id", 0))
    secret_code = int(request.GET.get("secret_code"))

    referrer = request.META.get('HTTP_REFERER', None)

    if referrer:
        ref_split = referrer.split("//")
        domain = ref_split[0] if len(ref_split) == 1 else ref_split[1]
        domain = domain.split("/")[0]

        _increment_metric("domain_updated: %s" % domain.strip("/"))

        try:
            u = User.objects.get(pk=user_id)
            if u.secret_code != secret_code:
                raise PermissionDenied()
            # if it is already a good value, leave it as is
            if (u.domain == "www.almostmatt.com" or u.domain == "" or u.domain == None):
                u.domain = domain
                u.save()
        except User.DoesNotExist:
            raise PermissionDenied()

    response_data = {}
    response = HttpResponse(json.dumps(response_data), content_type="application/json")
    return response


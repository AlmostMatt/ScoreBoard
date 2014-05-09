from django.shortcuts import render
import json
from polls.models import Poll
from django.http import HttpResponse

def index(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    output = ', '.join([p.question for p in latest_poll_list])
    return HttpResponse(output)

def detail(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404
    return render(request, 'polls/detail.html', {'poll': poll})

def results(request, poll_id):
    response_data = {}
    response_data['result'] = 'failed'
    response_data['message'] = 'You messed up'
    response_data['a list'] = [1,2,3]
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    #return HttpResponse("<b>You're looking at the results of poll %s.</b>" % poll_id)

def vote(request, poll_id):
    return HttpResponse("You're voting on poll %s." % poll_id)
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from guard.settings import DEBUG
from tsw.models import *
from django.db.models import Sum, Count

from chartit import DataPool, Chart, PivotDataPool, PivotChart

from collections import defaultdict
import urllib2
from datetime import timedelta, datetime

import logging
logger = logging.getLogger(__name__)

def _chart_style(w=1200, h=600):
    return {
        'width': w,
        'height': h,
        'borderWidth': 2,
        'plotShadow': True,
        #'plotBorderWidth': 2,
        #'plotBorderColor': '#000000',
        'backgroundColor': '#f3f3ff',
        'plotBackgroundColor': '#fafafa',
        'marginRight': 20,
    }


def stats(request):
    num_users = User.objects.count()
    num_scores = HighScore.objects.count()


#@staff_member_required
def level_completion(request):
    #NUM_LEVELS = 56
    #    event_count = defaultdict(lambda: defaultdict(int))
    event_names = {
            'level_complete': 'Complete',
            'level_skip': 'Skip',
            'level_abandon': 'Abandon',
            'level_play': "Level Select (excludes 'Next Level')",
            'level_improve': 'Improve Time',
            'time_up': 'Time Limit Reached'
    }
    prefixes = event_names.keys()
    data = DataPool(
            series =
                [{'options': {
                    'source': MetricCount.objects.filter(metric=event),
                    },
                  'terms': [
                    {'%s_n' % event: 'n'},
                    {event_names[event]: 'count'}]
                 } for event in prefixes])

    chart = Chart(
            datasource = data,
            series_options =
            [{'options':{
                'type': 'line',
                'stacking': False},
              'terms': {
                  ('%s_n' % event): [event_names[event]]
                }
              } for event in prefixes],
            chart_options =
              {'title': {'text': 'Level Statistics'},
               'xAxis': {'title': {'text': 'Level number'},
                        },
               'yAxis': {'title': {'text': 'Number of Players'},
                         'min': 0},
               'chart': _chart_style()
              })
    return render_to_response('chart.html', {'chart': chart})

#@staff_member_required
def domain_distribution(request):
    domain_data = PivotDataPool(
            series = [
              {'options': {
                  'source': MetricCount.objects.filter(metric__startswith='domain: ', count__gte=30),
                  'categories': ['metric'],
                  #'legend_by': 'n'
                  },
               'terms': {
                   'Views': Sum('count')}}])

    domain_chart = PivotChart(
            datasource = domain_data,
            series_options = [
              {'options': {
                  'type': 'bar',
                  'stacking': True,
                  'xAxis': 0,
                  'yAxis': 0},
                'terms': ['Views']
                }],
            chart_options =
              {'title': {'text': 'Domain distribution'},
               'xAxis': {'title': {'text': 'Domains'},
                        },
               'yAxis': {'title': {'text': 'Number of Loads'}},
               'chart': _chart_style(h=900)})
    return render_to_response('chart.html', {'chart': domain_chart})


def hourly_users(request):
    now = datetime.now()
    result = []
    t2 = now
    for n in range(10):
        t1 = t2 - timedelta
        usrs = User.objects.filter(create_date__gte=t1, create_date__lt=t2).count()
        result.append((n, usrs))
        t2 = t1
    return result


#@staff_member_required
def new_users(request):
    now = datetime.now()
    if DEBUG:
        # SQLite
        date_format = "date(create_date)"
    else:
        date_format = "to_char(create_date, 'YYYY-MM-DD HH24:00')"

    user_data = PivotDataPool(
            series = [
              {'options': {
                  # man, why does chartit make life so hard
                  'source': User.objects.extra({'create_date': date_format}),
                  'categories': ['create_date'],
                  #'legend_by': 'n'
                  },
               'terms': {
                   'Num Users': Count('id')}}])

    user_chart = PivotChart(
            datasource = user_data,
            series_options = [
              {'options': {
                  'type': 'line',
                  #'stacking': True,
                  'xAxis': 0,
                  'yAxis': 0},
                'terms': ['Num Users']
                }],
            chart_options =
              {'title': {'text': 'New Users by hour'},
               'xAxis': {'title': {'text': 'Hour'},
                        },
               'yAxis': {'title': {'text': 'Number of New Users'},
                         'min': 0},
               'chart': _chart_style()})
    duration = datetime.now() - now
    logger.info("new_users took %s" % duration)
    return render_to_response('chart.html', {'chart': user_chart})


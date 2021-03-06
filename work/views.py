# -*- coding: utf-8 -*-
import json
import urllib
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from work.models import Work, TitleMapping
from record.models import Record, History, get_episodes

def old_url(request, remainder):
    return redirect('work.views.detail', title=remainder)

def merge_dashboard(request):
    return redirect('/moderation/merge/')

def _get_record(request, work):
    if request.user.is_authenticated():
        try:
            record = request.user.record_set.get(work=work)
        except:
            record = None
    else:
        record = None
    return record

def _get_work(title):
    return get_object_or_404(TitleMapping, title=title).work

def detail(request, title):
    work = _get_work(title)

    N = 6
    history = work.history_set.all().select_related('user')
    comments = list(history.exclude(comment='')[:N])
    if len(comments) < N:
        comments += list(history.filter(comment='')[:N-len(comments)])

    alt_titles = TitleMapping.objects.filter(work=work) \
            .exclude(title=work.title).values_list('title', flat=True)
    episodes = get_episodes(work)
    return render(request, "work/work_detail.html", {
        'work': work,
        'episodes': episodes,
        'record': _get_record(request, work),
        'records': work.record_set,
        'alt_titles': alt_titles,
        'comments': comments,
        'preload_data': json.dumps({
            'work': {'title': work.title},
            'episodes': get_episodes(work, include_without_comment=True),
            'daum_api_key': settings.DAUM_API_KEY,
        })
    })

def episode_detail(request, title, ep):
    ep = int(ep)
    work = _get_work(title)
    history_list = work.history_set.filter(status=str(ep)).exclude(comment='').order_by('-id')
    return render(request, 'work/episode.html', {
        'work': work,
        'current_episode': ep,
        'episodes': get_episodes(work),
        'record': _get_record(request, work),
        'history_list': history_list,
    })

def list_users(request, title):
    work = _get_work(title)
    return render(request, "work/users.html", {
        'work': work,
        'record': _get_record(request, work),
        'records': work.record_set.select_related('user') \
                .order_by('status_type', 'user__username')
    })

def video(request, title, provider, id):
    assert provider == 'tvpot'
    return redirect('http://tvpot.daum.net/v/' + id)

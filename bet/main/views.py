from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.core import urlresolvers
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from main.forms import LoginForm, BetForm
from main.models import Agent, Bet
from models import OddCategory, Match, Ticket, Odd, Result

__author__ = 'kenneth'

def index(request, template_name='main/index.html'):
    page_title = 'Welcome To Country Sports Bet'
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
            if user and user.is_active:
                login(request,user)
                return HttpResponseRedirect(urlresolvers.reverse('bet'))
    return render_to_response(template_name,locals(),context_instance=RequestContext(request))

@csrf_exempt
def bet(request, template_name='main/bet.html'):
    page_title = 'Place Bet'
    form = BetForm()
    if request.method == 'POST':
        form = request.POST['ticket']
        ticket = Ticket(amount = request.POST['amount']).save()
        bets = form.split(" ")
        for bet_string in bets:
            bet_stuff = bet_string.strip().split("-")
            match = get_object_or_404(Match,id = int(bet_stuff[0]))
            category = get_object_or_404(OddCategory,name=bet_stuff[3])
            odd = get_object_or_404(Odd,match=match,category=category, oddCode = bet_stuff[1])
            betT = Bet(odd=odd,ticket=ticket).save()
        return HttpResponseRedirect(urlresolvers.reverse('bet')+'staked')
    return render_to_response(template_name,locals(),context_instance=RequestContext(request))

@require_POST
def errorCheck(request):
    match = get_object_or_404(Match,id = request.POST['match_code'])
    side_picked = request.POST['side_picked']
    category = get_object_or_404(OddCategory,name=request.POST['category'])
    try:
        odd = Odd.objects.get(match = match, oddCode=side_picked,category=category)
    except Exception:
        return HttpResponse('no match')
    return HttpResponse('%s'%odd.odd)


def sync_table(request,table):
    response = simplejson.dumps({'name':"no data"})
    data = {}
    if table == 'oddcat':
        objects = []
        for cat in OddCategory.objects.filter(synced=False):
            obj = {'iid':cat.id,'name':cat.name }
            objects.append(obj)
            cat.synced = True
            cat.save()
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)
    if table == 'match':
        objects = []
        for match in Match.objects.filter(synced=False):
            obj = {'iid':match.code,'homeTeam':match.homeTeam,'awayTeam':match.awayTeam,'startTime':str(match.startTime),'league':match.league}
            objects.append(obj)
            match.synced = True
            match.save()
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)
    if table == 'ticket':
        objects = []
        for ticket in Ticket.objects.filter(synced=False):
            obj = {'iid':ticket.id,'amount':ticket.amount,'betOn':ticket.betOn}
            objects.append(obj)
            ticket.synced = True
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)
    if table == 'odd':
        objects = []
        for odd in Odd.objects.filter(synced=False):
            try:
                obj = {'iid':odd.id,"odd":str(odd.odd),"oddCode":odd.oddCode,"match":odd.match.code,"category":odd.category_id}
            except Exception:
                pass
            else:
                objects.append(obj)
            odd.synced = True
            odd.save()
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)

    if table == 'agent':
        objects = []
        for agent in Agent.objects.filter(synced=False):
            obj = {'iid':agent.id,'username':agent.username,'password':agent.password,
                                                                      'email':agent.email,'role':agent.role,'joined_on':str(agent.joined_on)}
            objects.append(obj)
            agent.synced = True
            agent.save()
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)
    if table == 'result':
        objects = []
        for result in Result.objects.filter(synced=False):
            obj = {'odd':result.odd_id}
            objects.append(obj)
            result.synced = True
            result.save()
        data['name'] = objects
        if len(objects) < 1:
            data['up-to-date'] = 'true'
        response = simplejson.dumps(data)
    return HttpResponse(response)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(urlresolvers.reverse('home'))
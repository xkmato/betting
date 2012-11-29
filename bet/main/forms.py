from django import forms
from django.forms.fields import ChoiceField
from main.models import OddCategory, Odd, Match, Bet, Ticket


__author__ = 'kenneth'

CATEGORIES = tuple([(name,name) for name in OddCategory.objects.all()])

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class BetForm(forms.Form):
    ticket = forms.CharField()
    match_code = forms.CharField()
    side_picked = forms.CharField()
    odd = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    category = ChoiceField(widget=forms.Select(),choices = CATEGORIES)

    def save(self):
        match = Match.objects.get(id=self.cleaned_data['match_code'])
        category = OddCategory.objects.get(name=self.cleaned_data.get('category'))
        odd = Odd(odd=self.cleaned_data.get('odd'),oddCode=self.cleaned_data.get('side_picked'),category=category,match=match).save()
        ticket_id = self.cleaned_data.get('ticket')
        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
        else:
            ticket = Ticket().save()
        bet = Bet(odd=odd,ticket=ticket)
        return bet


class TicketForm(forms.Form):
    ticket = forms.IntegerField()
    branch = forms.IntegerField()
    amount = forms.CharField()
    betOn = forms.DateTimeField()

    def save(self):
        cleaned_data = self.cleaned_data
        ticket = Ticket.objects.create(iid=cleaned_data['ticket'],amount=cleaned_data['amount'],betOn=cleaned_data['betOn'])
        return ticket


class BetForm(forms.Form):
    ticket = forms.IntegerField()
    odd = forms.IntegerField()

    def save(self):
        cleaned_data = self.cleaned_data
        bet = Bet.objects.create(ticket = cleaned_data['ticket'],odd = cleaned_data['odd'])
        return bet
from django.contrib import admin
from main.models import OddCategory, Match, Odd, Result, Ticket, Agent

__author__ = 'kenneth'

class OddCategoryAdmin(admin.ModelAdmin):
    list_display = ['name','synced']

admin.site.register(OddCategory,OddCategoryAdmin)

class OddInline(admin.TabularInline):
    model = Odd
    extra = 7
    #list_display = ['category','oddCode','match','odd']

class MatchAdmin(admin.ModelAdmin):
    list_display = ['code','homeTeam','awayTeam','startTime','league']
    inlines = [OddInline]

admin.site.register(Match,MatchAdmin)

admin.site.register(Result)

admin.site.register(Agent)

class TicketAdmin(admin.ModelAdmin):
    list_display = ['amount','expectedAmount','is_winner']

admin.site.register(Ticket,TicketAdmin)

class BetAdmin(admin.ModelAdmin):
    list_display = ['ticket','odd','is_winner']
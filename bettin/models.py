from datetime import datetime
from decimal import Decimal

__author__ = 'kenneth'
import peewee

db = peewee.SqliteDatabase('bet.sqlite3',threadlocals=True)

class ModelStuff(peewee.Model):
    class  Meta:
        database = db

class User(ModelStuff):
    iid = peewee.IntegerField()
    username = peewee.CharField()
    password = peewee.CharField()
    email = peewee.CharField()
    role = peewee.CharField()
    joined_on = peewee.DateTimeField()

    def __unicode__(self):
        return self.username

class Match(ModelStuff):
    iid = peewee.IntegerField(unique=True)
    homeTeam = peewee.CharField(max_length=10)
    awayTeam = peewee.CharField(max_length=10)
    startTime = peewee.DateTimeField()
    league = peewee.CharField(max_length=15)

    def is_valid(self):
        return self.startTime > datetime.now()

    def __unicode__(self):
        return self.homeTeam + " vs " +self.awayTeam

class Ticket(ModelStuff):
    branch = peewee.IntegerField(default=1)
    amount = peewee.DecimalField(max_digits=9,decimal_places=2)
    betOn = peewee.DateTimeField()
    paid = peewee.BooleanField(default=False)
    paidDate = peewee.DateTimeField(null=True)
    synced = peewee.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id)

    @property
    def totalOdds(self):
        odd = 1
        for bet in self.bet_set:
            odd = odd * bet.odd.odd
        return Decimal(odd).quantize(Decimal("0.01"))

    @property
    def expectedAmount(self):
        amount = Decimal(self.amount)
        for bet in self.bet_set:
            amount = amount * Decimal(bet.odd.odd)
        return Decimal(amount).quantize(Decimal("0.01"))

    def is_winner(self):
        if len([b for b in self.bet_set])<1:
            return False
        for bet in self.bet_set:
            if not bet.is_winner():
                return False

        else:
            return True

    def clear(self):
        for bet in self.bet_set:
            bet.delete_instance()
        self.delete_instance()

class OddCategory(ModelStuff):
    iid = peewee.IntegerField(unique=True)
    name = peewee.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Odd(ModelStuff):
    iid = peewee.IntegerField(unique=True)
    odd = peewee.DecimalField(max_digits=3,decimal_places=2)
    category = peewee.ForeignKeyField(OddCategory)
    oddCode = peewee.CharField(max_length=3)
    match = peewee.ForeignKeyField(Match)

    def __unicode__(self):
        return  '%s vs %s (%s) - %s'%(self.match.homeTeam, self.match.awayTeam, self.category.name,self.oddCode)


class Bet(ModelStuff):
    ticket = peewee.ForeignKeyField(Ticket)
    odd = peewee.ForeignKeyField(Odd)
    synced = peewee.BooleanField(default=False)

    def is_winner(self):
        return self.odd in [result.odd for result in Result.select()]

    def __unicode__(self):
        return '%s - %s - %s'%(self.odd.match.id,self.odd.oddCode,self.odd)

class Result(ModelStuff):
    iid = peewee.IntegerField(unique=True)
    odd = peewee.ForeignKeyField(Odd)

    def __unicode__(self):
        return self.odd.__unicode__()
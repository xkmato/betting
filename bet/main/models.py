__author__ = 'kenneth'
from django.db import models
#ODD_CHOICES = (('U','U'),('O','O'),('1','1'),('2','2'),('X','X'),('1/1',1/1),('1/2','1/2'),('1/X','1/X'),('X/2','X/2'),('1/1','1/1'),('X/1','X/1'),())

class Result(models.Model):
    odd = models.ForeignKey('Odd')
    synced = models.BooleanField(default=False)

    def __unicode__(self):
        return self.odd.__unicode__()


class Bet(models.Model):
    ticket = models.ForeignKey('Ticket')
    odd = models.ForeignKey('Odd')
    synced = models.BooleanField(default=False)

    def is_winner(self):
        return self.odd in [result.odd for result in Result.objects.all()]

    def __unicode__(self):
        return '%s - %s - %s'%(self.odd.match_id,self.odd.oddCode,self.odd)

class Ticket(models.Model):
    amount = models.DecimalField(max_digits=9,decimal_places=2)
    betOn = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.pk)

    @property
    def bets(self):
        return self.bet_set.all()

    @property
    def totalOdds(self):
        odd = 1
        for bet in self.bet_set.all():
            odd = odd * bet.odd.odd
        return odd

    @property
    def expectedAmount(self):
        return self.totalOdds * self.amount

    def is_winner(self):
        for bet in self.bets:
            if not bet.is_winner():
                return False
        return True

    def delete(self, using=None):
        for bet in self.bets():
            bet.delete()
        super(Ticket,self).delete()

class Odd(models.Model):
    odd = models.DecimalField(max_digits=5,decimal_places=2)
    category = models.ForeignKey('OddCategory')
    oddCode = models.CharField(max_length=3)
    match = models.ForeignKey('Match')
    synced = models.BooleanField(default=False)

    def delete(self, using=None):
        for result in self.result_set.all():
            result.delete()
        for bet in self.bet_set.all():
            bet.delete()
        super(Odd,self).delete()

    def __unicode__(self):
        return  '%s vs %s (%s) - %s'%(self.match.homeTeam, self.match.awayTeam, self.category.name,self.oddCode)

class Match(models.Model):
    code = models.IntegerField(unique=True)
    homeTeam = models.CharField(max_length=100)
    awayTeam = models.CharField(max_length=100)
    startTime = models.DateTimeField()
    league = models.CharField(max_length=15)
    synced = models.BooleanField(default=False)

    def delete(self, using=None):
        for odd in self.odd_set.all():
            odd.delete()
        super(Match,self).delete()

    def __unicode__(self):
        return self.homeTeam + " vs " +self.awayTeam

class OddCategory(models.Model):
    name = models.CharField(max_length=50)
    synced = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def delete(self, using=None):
        for odd in self.odd_set.all():
            odd.delete()
        super(OddCategory,self).delete()

class Agent(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    role = models.CharField(max_length=100,default="Agent")
    joined_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    def  __unicode__(self):
        return self.username
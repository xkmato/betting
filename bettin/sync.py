from httplib import HTTPConnection
import httplib
import json
import socket
from multitask import sleep
from urllib2 import Request, URLError, HTTPError, urlopen
import peewee
from models import OddCategory, Match, Ticket, Odd, Result, User

__author__ = 'kenneth'

class Synchronize(object):
    URL = 'kirooto.alwaysdata.net'
    connection = HTTPConnection(URL)

    def __init__(self):
        OddCategory.create_table(fail_silently=True)
        Match.create_table(fail_silently=True)
        Ticket.create_table(fail_silently=True)
        Odd.create_table(fail_silently=True)
        Result.create_table(fail_silently=True)

    @classmethod
    def exists(cls,iid,table):
        if table == "match":
            try:
                Match.get(iid=iid)
            except Match.DoesNotExist:
                return False
        if table == "odd":
            try:
                Odd.get(iid=iid)
            except Odd.DoesNotExist:
                return False
        if table == "cat":
            try:
                OddCategory.get(idd=iid)
            except OddCategory.DoesNotExist:
                return False
        if table == "result":
            try:
                Result.get(iid=iid)
            except Result.DoesNotExist:
                return False
        if table == "user":
            try:
                User.get(iid=iid)
            except User.DoesNotExist:
                return False
        return True


    def syncOddCatTable(self):
        self.connection.request("GET", "/sync/oddcat")
        response = self.connection.getresponse()
        data = response.read()
        data = json.loads(data)
        print response.read()
        if not data.has_key('up-to-date'):
            for cat in data['name']:
                try:
                    OddCategory.create(iid=cat['iid'],name=cat['name'])
                except Exception, e:
                    print str(e) + "- OddCat"

    def syncMatchTable(self):
        self.connection.request("GET", "/sync/match")
        response = self.connection.getresponse()
        data = response.read()
        data = json.loads(data)
        print response.read()
        print data
        if not data.has_key('up-to-date'):
            for match in data['name']:
                try:
                    Match.create(iid=match['iid'],homeTeam=match['homeTeam'], awayTeam=match["awayTeam"], startTime=match['startTime'],
                        league=match['league'])
                except Exception, e:
                    print str(e) + "- Match"

    def syncTicketTable(self):
        data = {}
        objects = []
        if not data.has_key('up-to-date'):
            for ticket in Ticket.select():
                obj = {'ticket_id':ticket.id,'branch':1,'amount':str(ticket.amount),'betOn':str(ticket.betOn),'paid':ticket.paid,'paidDate':str(ticket.paidDate)}
                objects.append(obj)
            data['name'] = objects
            request = Request(url='http://'+self.URL+'/sync/ticket',data=json.dumps(data))
            try:
                urlopen(request).read()
            except HTTPError, err:
                pass
            except  URLError,err:
                pass

    def syncOddTable(self):
        self.connection.request("GET", "/sync/odd")
        response = self.connection.getresponse()
        data = json.loads(response.read())
        print response.read()
        if not data.has_key('up-to-date'):
            for odd in data['name']:
                try:
                    category = OddCategory.get(iid=int(odd['category']))
                    match = Match.get(iid=int(odd['match']))
                    Odd.create(iid=odd['iid'],odd=unicode(odd['odd']), category=category, oddCode=unicode(odd['oddCode']), match=match)
                except Exception, e:
                    print str(e) + "- Odd"

    def syncResult(self):
        self.connection.request("GET", "/sync/result")
        response = self.connection.getresponse()
        data = json.loads(response.read())
        print response.read()
        if not data.has_key('up-to-date'):
            for result in data['name']:
                odd = Odd.get(iid=result['odd'])
                Result.create(iid=result['iid'],odd=odd)

    def syncUser(self):
        self.connection.request("GET", "/sync/agent")
        response = self.connection.getresponse()
        data = json.loads(response.read())
        print response.read()
        if not data.has_key('up-to-date'):
            for user in data['name']:
                User.create(iid=user['iid'],username=user['username'],password=user['password'],
                    email=user['email'],role=user['role'],joined_on=user['joined_on'])



    def run(self):
        while True:
            try:
                self.syncUser()
            except httplib.HTTPException:
    #            app.connection.set_text("Connection Error")
                pass
            except socket.gaierror:
    #            app.connection.set_text("OffLine")
                pass
            except peewee.DoesNotExist:
    #            app.connection.set_text("Updated...")
                pass
            except Exception,e:
    #            app.connection.set_text("Ignore - User Error")
                print e
            try:
                self.syncMatchTable()
            except httplib.HTTPException:
    #            app.connection.set_text("Connection Error")
                pass
            except socket.gaierror:
    #            app.connection.set_text("OffLine")
                pass
            except peewee.DoesNotExist:
    #            app.connection.set_text("Updated...")
                pass
            except Exception,e:
    #            app.connection.set_text("Ignore - Match Error")
                print e
            try:
                self.syncOddCatTable()
            except httplib.HTTPException:
    #            app.connection.set_text("Connection Error")
                pass
            except socket.gaierror:
    #            app.connection.set_text("OffLine")
                pass
            except peewee.DoesNotExist:
    #            app.connection.set_text("Updated...")
                pass
            except Exception,e:
    #            app.connection.set_text("Ignore - Category Error")
                print e
            try:
                self.syncResult()
            except httplib.HTTPException:
    #            app.connection.set_text("Connection Error")
                pass
            except socket.gaierror:
    #            app.connection.set_text("OffLine")
                pass
            except peewee.DoesNotExist:
    #            app.connection.set_text("Updated...")
                pass
            except Exception,e:
    #            app.connection.set_text("Ignore - Result Error")
                print e
            try:
                self.syncOddTable()
            except httplib.HTTPException:
    #            app.connection.set_text("Connection Error")
                pass
            except socket.gaierror:
    #            app.connection.set_text("OffLine")
                pass
            except peewee.DoesNotExist:
    #            app.connection.set_text("Updated...")
                pass
            except Exception,e:
    #            app.connection.set_text("Ignore - Odd Error")
                print e
    #        self.syncTicketTable()
            yield sleep(20)
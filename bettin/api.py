
import peewee
from models import User, Match, Bet, Ticket, Odd, OddCategory
#import win32print

#classes
class BetError(RuntimeError):
    pass

#functions
def authenticate(username,password):
    try:
        user = User.get(username=username,password=password)
    except peewee.DoesNotExist:
        return None
    else:
        return user


def create_bet(match,oddCode,category):
    try:
        odd = Odd.get(match=match,category=category,oddCode=oddCode)
    except peewee.DoesNotExist, e:
        raise BetError(str(e))
    bet = Bet()
    bet.odd = odd
    return bet


def verify(ticket_id):
    try:
        ticket = Ticket.get(id = ticket_id)
        if ticket.has_won():
            return ticket
        else:
            return None
    except Ticket.DoesNotExist:
        return None


def done_paying(ticket_id):
    ticket = Ticket.get(id=ticket_id)
    amount = ticket.amount
    ticket.delete_instance()

def cancel_receipt():
    pass


def printTicket(ticket,user):
    tic =  "Country Sports Bet\n%s\nAgent: %s\n-----------------------------\n"%(str(ticket.betOn),user.username)
    for bet in ticket.bet_set:
        tic += 'match code: %s\ncategory: %s\n%s vs %s \nbet on:%s \nOdd: %s \nstartsOn: %s\n\n'%(bet.odd.match.iid,bet.odd.category.name,bet.odd.match.homeTeam,
                                                                                         bet.odd.match.awayTeam,bet.odd.oddCode,
                                                                                         bet.odd.odd,str(bet.odd.match.startTime))
    tic += "-----------------------------\nAmount -    %s \n"%ticket.amount
    tic +=  "Expected - %s \n"%ticket.expectedAmount
    tic += "Odd -   %s \n"%ticket.totalOdds
    tic += "|||%d||| AwesomeNux Inc. \n"%ticket.id
    tic += "\n\n\n\n"

    try:
        hPrinter = win32print.OpenPrinter ("EPSON TM-U220D Receipt(1)")
    except Exception:
        try:
            hPrinter = win32print.OpenPrinter("EPSON TM-U220D Receipt")
        except Exception:
            ti = open('tictet %d'%ticket.id, 'w')
            ti.write(tic)
            ti.close()
            return "No Printer Detected"
#    job = win32print.StartDocPrinter (hPrinter, 1, ("Recipt %d\n"%ticket.id, None, "RAW"))
#    win32print.WritePrinter(hPrinter, tic)
#    win32print.EndDocPrinter (hPrinter)
#    return None

def confirm_button():
    pass


def check_available(match_id,oddCode,category_name):
    try:
        match = Match.get(iid=match_id)
        category = OddCategory.get(name=category_name)
        odd = Odd.get(match=match,category=category,oddCode=oddCode)
    except peewee.DoesNotExist:
        return None
    else:
        return odd.odd

def get_side_picked(match_id,side):
    match = check_available(match_id)
    if match:
        odd = Odd.get(match=match,oddCode=side)
        return odd.odd
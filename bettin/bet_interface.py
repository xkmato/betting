from datetime import datetime
import gobject
import gtk
import peewee
from api import authenticate, create_bet,  BetError, printTicket
from models import Ticket, Match, OddCategory, Odd
import printer
from sync import Synchronize

__authors__ = 'kenneth and emma'


class BettingApp(object):
    bets = []
    fullTicket = None
    user = None


    def on_window_destroy(self,widget,data=None):
        gtk.mainquit()

    def on_serial_number_changed(self,widget,data=None):
        id = self.serial_number.get_text()
        if id != "":
            try:
                ticket = Ticket.get(id=id,branch=1)
                self.validity_label.set_text("Available")
                self.verify_serial.set_sensitive(True)
            except Ticket.DoesNotExist:
                self.validity_label.set_text("Invalid")
                self.verify_serial.set_sensitive(False)
        else:
            self.verify_serial.set_sensitive(False)

    def on_login_clicked(self,widget,data=None):
        username = self.username_text.get_text()
        password = self.password_text.get_text()
        user = authenticate(username,password)
        self.user = user
        if user:
            self.current_user.show()
            self.enterbet_box.show()
            self.bet_box.show()
            self.currentusers_box.show()
            self.payment_box.show()
            self.stakebox.show()
            self.amount.show()
            self.amountstaked.show()
            self.loginbox.hide()
            self.user_now.set_text("Logged in as :"+self.username_text.get_text())
            self.username_text.set_text("")
            self.password_text.set_text("")
            self.amountstaked.set_text("")
            self.matchCode.set_text("")
            self.bet.set_text("")
            self.totalstake.set_text("")
            self.totalOdd.set_text("")
            self.exAmount.set_text("")

        else:
            self.wrong_login.show()
            self.wrong_login.set_text("*Wrong login")

    def on_logout_clicked(self,widget,data=None):
        self.loginbox.show()
        self.enterbet_box.hide()
        self.currentusers_box.hide()
        self.payment_box.hide()
        self.bet_box.hide()
        self.anothermatch_label.hide()
        self.stakebox.hide()
        self.confirmVbox.hide()
        self.wrong_login.set_text("")


    def on_stakeButton_clicked(self,widget,data=None):
        self.fullTicket = Ticket.create(amount = self.amountstaked.get_text(),betOn=datetime.now())
        if len(self.bets) < 0:
            #Todo make sure no empty bets are made
            pass
        else:
            for bet in self.bets:
                bet.ticket = self.fullTicket
                bet.save()
            self.totalstake.set_text(str(self.amountstaked.get_text()))
            self.exAmount.set_text(str(self.fullTicket.expectedAmount))
            self.totalOdd.set_text(str(self.fullTicket.totalOdds))
            self.confirmVbox.show()
            self.stakebox.hide()
            self.enterbet_box.hide()
            self.payment_box.hide()
            self.bet_box.hide()
            self.anothermatch_label.hide()

    def on_confirmButton_clicked(self,widget,data=None):
        pt = printTicket(self)
        if pt:
            self.noPrinter.set_text(pt)
        else:
            self.fullTicket = None
            self.bets = []
            self.hbox2.show()
            self.enterbet_box.show()
            self.bet_box.show()
            self.amount.show()
            self.stakebox.show()
            self.amountstaked.show()
            self.payment_box.show()
            self.confirmVbox.hide()
            self.anothermatch_label.hide()
            self.amountstaked.set_text("")
            self.matchCode.set_text("")
            self.bet.set_text("")
            self.totalstake.set_text("")
            self.totalOdd.set_text("")
            self.exAmount.set_text("")
            self.amountstaked.set_text("")

    def on_cancel_reciept_clicked(self,widget,data=None):
        for bet in self.fullTicket.bet_set:
            bet.delete_instance()
        self.fullTicket.delete_instance()
        self.cancel_bet()
        self.bet_box.show()
        self.currentusers_box.show()
        self.enterbet_box.show()
        self.stakebox.show()
        self.confirmVbox.hide()
        self.payment_box.show()
        self.totalstake.set_text("")
        self.totalOdd.set_text("")
        self.exAmount.set_text("")
        self.amountstaked.set_text("")

    def on_update_clicked(self,widget,data=None):
        Synchronize().run(self)

    def on_addMatchButton_clicked(self,widget,data=None):
        matchId = self.matchCode.get_text()
        oddCode = self.bet.get_text()
        category = self.category.get_active_text()
        try:
            match = Match.get(iid=matchId)
            category = OddCategory.get(name=category)
        except peewee.DoesNotExist:
            self.addMatchButton.set_sensitive(False)
        else:

            try:
                bet = create_bet(match,oddCode,category)
                self.bets.append(bet)
                self.matchCode.set_text("")
                self.bet.set_text("")
                self.category.set_active(0)

            except BetError, e:
                #Todo Catch this error
                self.available.set_text("Unavailable")

    def on_cancle_match_clicked(self,widget,data=None):
        self.cancel_bet()


    def on_back_clicked(self,widget,data=None):
        self.stakebox.show()
        self.enterbet_box.show()
        self.payment_box.hide()
        self.confirmVbox.hide()
        self.bet_box.show()
        self.anothermatch_label.hide()
        self.totalOdd.set_text("")
        self.totalstake.set_text("")
        self.exAmount.set_text("")

    def on_category_combo_changed(self,widget,data=None):
        self.check()

    def on_pay_client_clicked(self,widget,data=None):
        self.verifyreciept_box.show()
        self.enterbet_box.hide()
        self.amount.hide()
        self.amountstaked.hide()
        self.bet_box.hide()
        self.payment_box.hide()

    def on_done_paying_clicked(self,widget,data=None):
        self.enterbet_box.show()
        self.bet_box.show()
        self.amount.show()
        self.amountstaked.show()
        self.amountstaked.set_text("")
        self.matchCode.set_text("")
        self.bet.set_text("")
        self.verifyreciept_box.hide()
        self.payment_box.show()

    def on_verify_serial_clicked(self,widget,data=None):
        id = self.serial_number.get_text()
        try:
            ticket = Ticket.get(id=id,branch=1)
            if ticket.is_winner():
                if not ticket.paid:
                    self.validity_label.set_text(str(ticket.expectedAmount))
                    self.pay.set_sensitive(True)
                else:
                    self.validity_label.set_text("Already payed")
                    self.pay.set_sensitive(False)
                    self.serial_number.set_text("")
            else:
                self.validity_label.set_text("Ticket Lost")
                self.pay.set_sensitive(False)
                self.serial_number.set_text("")
        except Ticket.DoesNotExist:
            self.validity_label.set_text("Invalid Ticket")
            self.pay.set_sensitive(False)
            self.serial_number.set_text("")

    def on_pay_clicked(self,widget,data=None):
        id = self.serial_number.get_text()
        ticket = Ticket.get(id=id)
        ticket.paid = True
        ticket.paidDate = datetime.now()
        ticket.save()
        self.serial_number.set_text("")
        self.validity_label.set_text("")
        self.pay.set_sensitive(False)

    def on_matchCode_changed(self,widget,data=None):
        self.check()

    def on_bet_changed(self,widget,data=None):
        self.check()

    def on_amountstaked_changed(self,widget,data=None):
        self.check()

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("interface.glade")
        self.window = builder.get_object("window")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_size_request(1000,600)
        builder.connect_signals(self)



        self.reason = builder.get_object("reason")
        self.confirmVbox = builder.get_object("confirmVbox")
        self.bet_box = builder.get_object("bet_box")
        self.enterbet_box = builder.get_object("enterbet_box")
        self.confirmButton = builder.get_object("confirmButton")
        self.addNotify = builder.get_object("addNotify")
        self.current_user = builder.get_object("current_user")
        self.username_box = builder.get_object("username_box")
        self.password_box = builder.get_object("password_box")
        self.loginbutton_box = builder.get_object("loginbutton_box")
        self.loginbox = builder.get_object("loginbox")
        self.currentusers_box = builder.get_object("currentusers_box")
        self.anothermatch_label = builder.get_object("anothermatch_label")
        self.stakebox = builder.get_object("stakebox")
        self.payment_box = builder.get_object("payment_box")
        self.back = builder.get_object("back")
        self.verifyreciept_box = builder.get_object("verifyreciept_box")
        self.done_verifying = builder.get_object("done_verifying")
        self.cancel_match = builder.get_object("cancel_match")
        self.user_now = builder.get_object("user_now")
        self.username_text = builder.get_object("username_text")
        self.password_text = builder.get_object("password_text")
        self.totalstake = builder.get_object("totalstake")
        self.amountstaked = builder.get_object("amountstaked")
        self.amount = builder.get_object("amount")
        self.matchCode = builder.get_object("matchCode")
        self.bet = builder.get_object("bet")
        self.validity_label = builder.get_object("validity_label")
        self.serial_number = builder.get_object("serial_number")
        self.totalOdd = builder.get_object("totalOdd")
        self.exAmount = builder.get_object("exAmount")
        self.wrong_login = builder.get_object("wrong_login")
        self.aligning = builder.get_object("aligning")
        self.addanothermatch_label = builder.get_object("addanothermatch_label")
        self.odd = builder.get_object('odd')
        self.available = builder.get_object('available')
        self.stakebutton = builder.get_object('stakeButton')
        self.login = builder.get_object('login')
        self.addMatchButton = builder.get_object('addMatchButton')
        self.category = builder.get_object("category_combo")
        self.hbox2 = builder.get_object("hbox2")
        self.verify_serial = builder.get_object("verify_serial")
        self.done_paying = builder.get_object("done_paying")
        self.pay = builder.get_object("pay")
        self.connection = builder.get_object("connection")
        self.noPrinter = builder.get_object("no_printer")
        self.update = builder.get_object("update")
        self.connect_printer = builder.get_object("printer_connection")
        self.printer_box = builder.get_object("printer_box")

        self.store = gtk.ListStore(gobject.TYPE_STRING)

        self.addMatchButton.set_sensitive(False)
        self.verify_serial.set_sensitive(False)
        self.validity_label.set_text("Invalid")


        cats = [[cat.name] for cat in OddCategory.select()]

        for c in cats:
            self.store.append(c)
        self.category.set_model(model=self.store)
        cell = gtk.CellRendererText()
        self.category.pack_start(cell,True)
        self.category.add_attribute(cell,'text',0)
        self.category.set_active(0)

        self.printer_store = gtk.ListStore(gobject.TYPE_STRING)
        printers = [[print_guy['Name']] for print_guy in printer.PrinterList()]
        for p__ in printers:
            self.printer_store.append(p__)
        self.printer_box.set_model(model=self.printer_store)
        self.printer_box.pack_start(cell,True)
        self.printer_box.add_attribute(cell,'text',0)
        self.printer_box.set_active(0)


        if self.amountstaked.get_text()=="":
            self.stakebutton.set_sensitive(False)

        self.odd.set_text("")
        self.confirmVbox.hide()
        self.currentusers_box.hide()
        self.anothermatch_label.hide()
        self.enterbet_box.hide()
        self.stakebox.hide()
        self.bet_box.hide()
        self.payment_box.hide()
        self.verifyreciept_box.hide()
        self.amount.hide()
        self.amountstaked.hide()
        #self.connect_printer.hide()

    def check(self):
        try:
            match = Match.get(iid=self.matchCode.get_text())
            category = OddCategory.get(name=self.category.get_active_text())
            odd = Odd.get(match=match,category=category,oddCode=self.bet.get_text())
            self.addMatchButton.set_sensitive(False)
            self.reason.set_text("Match Started")
        except Match.DoesNotExist:
            self.addMatchButton.set_sensitive(False)
            self.odd.set_text("")
            self.reason.set_text("Invalid Match")
        except OddCategory.DoesNotExist:
            self.addMatchButton.set_sensitive(False)
            self.odd.set_text("")
            self.reason.set_text("Invalid Category")
        except Odd.DoesNotExist:
            self.addMatchButton.set_sensitive(False)
            self.odd.set_text("")
            self.reason.set_text("Invalid Bet")
        else:
            if match.is_valid():
                self.addMatchButton.set_sensitive(True)
                self.reason.set_text("Available")
                self.odd.set_text(str(odd.odd))
            else:
                self.addMatchButton.set_sensitive(False)
                self.reason.set_text("Match Started")
        if len(self.bets)>0 and self.amountstaked.get_text()!= "":
            self.stakebutton.set_sensitive(True)
        else:
            self.stakebutton.set_sensitive(False)

    def cancel_bet(self):
        self.bet.set_text("")
        self.matchCode.set_text("")
        self.odd.set_text("")

    def on_printer_changed(self,widget,data=None):
        pass

if __name__ == "__main__":
    app = BettingApp()
    Synchronize().run(app)
    app.window.show()
    gtk.main()

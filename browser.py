#!/sw/bin/python2.6
#
# Copyright 2010 Uiri Noyb
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# You may contact Uiri Noyb via electronic mail with the address uiri@compucrunch.com
#
# Based off of GPL'd code snippet I found.
# <http://www.eurion.net/python-snippets/snippet/Webkit%20Browser.html>

import pygtk, gtk, webkit, gobject, os, time, threading, urllib2, urllib, platform, feedparser
from operator import itemgetter

class Browser:
    refresh_button = []
    forward_button = []
    back_button = []
    web_view = []
    scroll_window = []
    newtab = []
    closetab = []
    etcbutton = []
    historybutton = []
    hbox = []
    vbox = []
    url_bar = []
    history = []
    n = 0
    change_title = 0

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        self.prefsfile = open(os.path.expanduser("~/pyg/prefs"), 'w')
        for p in self.preferences:
            p = str(p) + "\n"
            self.prefsfile.writelines(p)
        self.prefsfile.close()
        self.historyfile = open(os.path.expanduser("~/pyg/history"), 'w')
        for a in self.history:
            a = str(a[0] + ": " + a[1])
            self.historyfile.writelines(a)
        self.historyfile.close()
        gtk.main_quit()

    def __init__(self):
        if not os.path.exists(os.path.expanduser("~/pyg")):
            os.mkdir(os.path.expanduser("~/pyg"))
        if not os.path.exists(os.path.expanduser("~/pyg/prefs")):
            self.prefsfile = open(os.path.expanduser("~/pyg/prefs"), 'w')
            self.prefsfile.write("1\nhttp://google.com/\n0\n1\n15\n")
            self.prefsfile.close()
        prefsfile = open(os.path.expanduser("~/pyg/prefs"), 'r')
        tmppref = prefsfile.readlines()
        self.preferences = []
        prefsfile.close()
        for pref in tmppref:
            self.preferences.append(pref.rstrip())
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)
        self.window.set_title("Pygmy Web")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_default_size(600,600)
        self.tabbook = gtk.Notebook()
        self.tabbook.set_scrollable(True)
        self.tabbook.popup_enable()
        if self.preferences[1] == '0':
            self.preferences[1] = "http://google.com/"
        if self.preferences[0] == '1':
            self.tabbook.set_tab_pos(gtk.POS_LEFT)
        elif self.preferences[0] == '2':
            self.tabbook.set_tab_pos(gtk.POS_TOP)
        elif self.preferences[0] == '3':
            self.tabbook.set_tab_pos(gtk.POS_RIGHT)
        elif self.preferences[0] == '4':
            self.tabbook.set_tab_pos(gtk.POS_BOTTOM)
        else:
            self.tabbook.set_tab_pos(gtk.POS_LEFT)
        self.addtab(openurl=self.preferences[1])
        if self.preferences[2] == '1':
            self.rssreader()
            self.t = threading.Thread(target=self.ping_rss)
            self.t.daemon = True
            self.t.start()
        self.mainbox.pack_start(self.tabbook, True, True, 0)
        self.tabbook.set_current_page(1)
        self.window.add(self.mainbox)
        self.window.show_all()
        self.tabbook.connect("switch_page", self.set_window_title)
        self.kbd_shortcuts(self.tabbook)

        #if self.preferences != None:
        #    if self.preferences[3] != '1': 
        if not os.path.exists(os.path.expanduser("~/pyg/history")):
            self.historyfile = open(os.path.expanduser("~/pyg/history"), 'w')
            self.historyfile.write("Google: http://www.google.com\n")
            self.historyfile.close()
        self.historyfile = open(os.path.expanduser("~/pyg/history"), 'r')
        self.historytemp = self.historyfile.readlines()
        self.history = []
        for a in self.historytemp:
            a = a.split(": ")
            self.history.append(a)
            while 1:
                try:
                    self.history.remove('\n')
                except:
                    break
        self.historyfile.close()

    def rssreader(self):
        try:
            self.n = self.n + 1
            rssfile = open(os.path.expanduser("~/pyg/feedlist"), 'r')
            rssstring = rssfile.read()
            self.rsslist = rssstring.split("\n")
            self.rssentries = []
            rssfile.close()
            for f in self.rsslist:
                d = feedparser.parse(f, None, None, "Pygmy RSS")
                for i in d['entries']:
                    entry = [i.title, i.link, i.description, d.encoding, i.summary_detail.type, i.summary_detail.base, i.updated_parsed]
                    self.rssentries.append(entry)
            self.rssstore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
            self.rssentries = sorted(self.rssentries, key=itemgetter(6), reverse=True)
            for x in self.rssentries:
                if len(x[0]) > 74:
                    title = x[0][0:72] + "..."
                else:
                    title = x[0]
                self.rssstore.append([title, x[0], x[1], x[2], x[3], x[4], x[5], x[6]])
            self.rssview = gtk.TreeView(self.rssstore)
            rssscroll = gtk.ScrolledWindow(None, None)
            rssscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            rssscroll.add(self.rssview)
            rsscell = gtk.CellRendererText()
            rsscolumn = gtk.TreeViewColumn("Title", rsscell, text=0)
            self.rssview.append_column(rsscolumn)
            self.rssbox = gtk.HBox(True, 0)
            self.rssbox.pack_start(rssscroll, True, True, 0)
            rssdisplaybox = gtk.VBox(False, 0)
            self.rsstitle = gtk.Label('Title')
            self.rssdescript = webkit.WebView()
            self.rssitemscroll = gtk.ScrolledWindow(None, None)
            self.rssitemscroll.add(self.rssdescript)
            self.rsslink = gtk.Button('Link')
            rssdisplaybox.pack_start(self.rsstitle, False, True, 0)
            rssdisplaybox.pack_start(self.rssitemscroll, True, True, 0)
            rssdisplaybox.pack_start(self.rsslink, False, True, 0)
            self.rssbox.pack_start(rssdisplaybox, False, True, 0)
            self.tabbook.prepend_page(self.rssbox)
            self.tabbook.set_tab_label_text(self.rssbox, "Pygmy RSS")
            self.tabbook.get_tab_label(self.rssbox).set_tooltip_text("Pygmy RSS")
            self.rssview.get_selection().connect("changed", self.show_rss_entry, self)
            self.tabbook.show_all()
            self.rsslinkcb = 'lol'
        except:
            if not os.path.exists(os.path.expanduser("~/pyg/feedlist")):
                rssfile = open(os.path.expanduser("~/pyg/feedlist"), "w")
                rssfile.write("None")
            raise

    def show_rss_entry(something, lol, self):
        rssrow, rssdata = self.rssview.get_selection().get_selected()
        self.rssdescript.load_string(rssrow.get_value(rssdata, 3), rssrow.get_value(rssdata, 5), rssrow.get_value(rssdata, 4), rssrow.get_value(rssdata, 6))
        self.rsstitle.set_text(rssrow.get_value(rssdata, 1))
        linktopost = rssrow.get_value(rssdata, 2)
        if self.rsslinkcb != 'lol':
            self.rsslink.disconnect(self.rsslinkcb)
        self.rsslinkcb = self.rsslink.connect("clicked", self.addtab, None, None, None, linktopost)

    def ping_rss(self):
        while 1:
            time.sleep(300)
            for f in self.rsslist:
                d = feedparser.parse(f, None, None, "Pygmy RSS")
                for i in d['entries']:
                    y = 0
                    for x in self.rssentries:
                        if x[0] == i.title:
                            y = 1
                    if y == 0:
                        entry = [i.title, i.link, i.description, d.encoding, i.summary_detail.type, i.summary_detail.base, i.updated_parsed]
                        self.rssentries.append(entry)
            sorted(self.rssentries, key=itemgetter(6))
            for x in self.rssentries:
                y = 0
                if len(x[0]) > 74:
                    title = x[0][0:72] + "..."
                else:
                    title = x[0]
                for s in self.rssstore:
                    if title == s[0]:
                        y = 1
                if y == 0:
                    self.rssstore.append([title, x[0], x[1], x[2], x[3], x[4], x[5], x[6]])
            time.sleep(3300)

    def addtab(self, widget=None, dummy=None, dummier=None, dummiest=None, openurl="http://google.com/"):
        self.web_view.append(webkit.WebView())
        self.web_view[len(self.web_view)-1].open(openurl)

        self.back_button.append(gtk.ToolButton(gtk.STOCK_GO_BACK))
        self.back_button[len(self.back_button)-1].connect("clicked", self.go_back)

        self.forward_button.append(gtk.ToolButton(gtk.STOCK_GO_FORWARD))
        self.forward_button[len(self.forward_button)-1].connect("clicked", self.go_forward)

        self.refresh_button.append(gtk.ToolButton(gtk.STOCK_REFRESH))
        self.refresh_button[len(self.refresh_button)-1].connect("clicked", self.refresh)

        self.url_bar.append(gtk.Entry())
        self.url_bar[len(self.url_bar)-1].connect("activate", self.on_active)

        self.etcbutton.append(gtk.Button('Prefs'))
        self.historybutton.append(gtk.Button('Hist'))
        self.historybutton[len(self.historybutton)-1].connect("activate", self.historytab)
        self.historybutton[len(self.historybutton)-1].connect("clicked", self.historytab)
        self.etcbutton[len(self.etcbutton)-1].connect("activate", self.show_prefs)
        self.etcbutton[len(self.etcbutton)-1].connect("clicked", self.show_prefs)
        self.newtab.append(gtk.Button('+'))
        self.newtab[len(self.newtab)-1].connect("activate", self.addtab)
        self.newtab[len(self.newtab)-1].connect("clicked", self.addtab)
        self.closetab.append(gtk.Button('X'))
        self.closetab[len(self.closetab)-1].connect("activate", self.removetab)
        self.closetab[len(self.closetab)-1].connect("clicked", self.removetab)

        self.web_view[len(self.web_view)-1].connect("load_committed", self.update_buttons)
        self.web_view[len(self.web_view)-1].connect("load_finished", self.set_tab_title)
        self.web_view[len(self.web_view)-1].connect("download_requested", self.download)

        self.scroll_window.append(gtk.ScrolledWindow(None, None))
        self.scroll_window[len(self.scroll_window)-1].add(self.web_view[len(self.web_view)-1])
        self.scroll_window[len(self.scroll_window)-1].set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.hbox.append(gtk.HBox(False, 0))
        self.vbox.append(gtk.VBox(False, 0))
        self.mainbox = gtk.VBox(False, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.back_button[len(self.back_button)-1], False, True, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.forward_button[len(self.forward_button)-1], False, True, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.refresh_button[len(self.refresh_button)-1], False, True, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.newtab[len(self.newtab)-1], False, True, 3)
        self.hbox[len(self.hbox)-1].pack_start(self.closetab[len(self.closetab)-1], False, True, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.url_bar[len(self.url_bar)-1], True, True, 3)
        self.hbox[len(self.hbox)-1].pack_start(self.historybutton[len(self.historybutton)-1], False, True, 0)
        self.hbox[len(self.hbox)-1].pack_start(self.etcbutton[len(self.etcbutton)-1], False, True, 0)
        self.vbox[len(self.vbox)-1].pack_start(self.hbox[len(self.hbox)-1], False, True, 0)
        self.vbox[len(self.vbox)-1].pack_start(self.scroll_window[len(self.scroll_window)-1], True, True, 0)
        self.tabbook.append_page(self.vbox[len(self.vbox)-1])
        self.tabbook.show_all()
        self.tabbook.set_current_page(len(self.vbox)-1+self.n)

    def on_active(self, widge, data=None):
        '''When the user enters an address in the bar, we check to make
           sure they added the http://, if not we add it for them.  Once
           the url is correct, we just ask webkit to open that site.'''
        url = self.url_bar[self.tabbook.get_current_page()-self.n].get_text()
        try:
            url.index(" ")
            url = "http://google.ca/search?q=" + url
        except:
            try:
                url.index("mailto")
                try:
                    platform.system().index("Win")
                    os.system("start "+url)
                except:
                    try:
                        platform.system().index("Dar")
                        os.system("open "+url)
                    except:
                        try:
                            platform.system().index("Lin")
                            os.system("xdg-open "+url)
                        except:
                            print "Good on you for running this on an unsupported system. Sorry, this thing can't open mailto urls for you"
            except:
                try:
                    url.index("://")
                except:
                    url = "http://"+url
        self.url_bar[self.tabbook.get_current_page()-self.n].set_text(url)
        try:
            url.index("mailto")
        except:
            self.web_view[self.tabbook.get_current_page()-self.n].open(url)

    def go_back(self, widget, data=None, other=None, etc=None):
        '''Webkit will remember the links and this will allow us to go
           backwards.'''
        self.web_view[self.tabbook.get_current_page()-self.n].go_back()

    def go_forward(self, widget, data=None, other=None, etc=None):
        '''Webkit will remember the links and this will allow us to go
           forwards.'''
        self.web_view[self.tabbook.get_current_page()-self.n].go_forward()

    def refresh(self, widget, data=None, etc=None, more=None):
        '''Simple makes webkit reload the current back.'''
        self.web_view[self.tabbook.get_current_page()-self.n].reload()

    def update_buttons(self, widget, data=None):
        '''Gets the current url entry and puts that into the url bar.
           It then checks to see if we can go back, if we can it makes the
           back button clickable.  Then it does the same for the foward
           button.'''
        self.url = widget.get_main_frame().get_uri()
        histthread = threading.Thread(target=self.addhistoryitem)
        histthread.daemon = True
        histthread.start()
        self.url_bar[self.tabbook.get_current_page()-self.n].set_text(self.url)
        self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()-self.n], "Loading...")
        self.tabbook.get_tab_label(self.vbox[self.tabbook.get_current_page()-self.n]).set_tooltip_text("LOADING!")
        self.window.set_title("Loading...")
        self.back_button[self.tabbook.get_current_page()-self.n].set_sensitive(self.web_view[self.tabbook.get_current_page()-self.n].can_go_back())
        self.forward_button[self.tabbook.get_current_page()-self.n].set_sensitive(self.web_view[self.tabbook.get_current_page()-self.n].can_go_forward())

    def addhistoryitem(self):
        url = self.url
        view = self.web_view[self.tabbook.get_current_page()-self.n]
        time.sleep(10)
        nurl = url + "\n"
        unique = 0
        for h in self.history:
            if nurl == h[1]:
                unique = 1
            if url == h[1]:
                unique = 1
        if unique == 0:
            self.history.append([view.get_main_frame().get_title(), url + "\n"])
            try:
                self.historybox
                uri = url.rstrip()
                self.historyliststore.append([self.history[len(self.history)-1][0], uri])
            except:
                uri = url.rstrip()

    def set_tab_title(self, widget, data=None):
        #if self.preferences != None:
        #   maxlen = self.preferences[4]
        #else:
        maxlen = '15'
        if self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_title() != None:
            real_title = self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_title()
            if len(self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_title()) > int(maxlen):
                newmaxlen = int(maxlen) - 3
                script = 'document.title=document.title.substring(0,' + str(newmaxlen) + ') + "...";'
                self.web_view[self.tabbook.get_current_page()-self.n].execute_script(script)
            self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()-self.n], self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_title())
            self.tabbook.get_tab_label(self.vbox[self.tabbook.get_current_page()-self.n]).set_tooltip_text(real_title)
            self.window.set_title(self.tabbook.get_tab_label(self.vbox[self.tabbook.get_current_page()-self.n]).get_text() + " - Pygmy Web")
        else:
            newmaxlen = int(maxlen) - 3
            if len(self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_uri()) > int(maxlen):
                uri = self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_uri()[0:newmaxlen] + "..."
            else:
                uri = self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_uri()
            self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()-self.n], uri)
            self.tabbook.get_tab_label(self.vbox[self.tabbook.get_current_page()-self.n]).set_tooltip_text(self.web_view[self.tabbook.get_current_page()-self.n].get_main_frame().get_uri())
            self.window.set_title("Pygmy Web")
        self.change_title = 0

    def set_window_title(self, widget, weirdpointerthing, n):
        if n-self.n >= 0:
            if self.tabbook.get_tab_label(self.vbox[n-self.n]) != None:
                self.window.set_title(self.tabbook.get_tab_label(self.vbox[n-self.n]).get_text() + " - Pygmy Web")
            else:
                self.window.set_title("Pygmy Web")
        else:
            if self.tabbook.get_tab_label_text(self.tabbook.get_nth_page(n)) == "Pygmy RSS":
                self.window.set_title("RSS Reader - Pygmy RSS")
            if self.tabbook.get_tab_label_text(self.tabbook.get_nth_page(n)) == "History":
                self.window.set_title("History - Pygmy Web")


    def removetab(self, widget=None, dummy=None, dummier=None, dummiest=None):
        if self.tabbook.get_current_page()-self.n >= 0:
            self.web_view.pop(self.tabbook.get_current_page()-self.n)
            self.back_button.pop(self.tabbook.get_current_page()-self.n)
            self.forward_button.pop(self.tabbook.get_current_page()-self.n)
            self.refresh_button.pop(self.tabbook.get_current_page()-self.n)
            self.url_bar.pop(self.tabbook.get_current_page()-self.n)
            self.newtab.pop(self.tabbook.get_current_page()-self.n)
            self.closetab.pop(self.tabbook.get_current_page()-self.n)
            self.scroll_window.pop(self.tabbook.get_current_page()-self.n)
            self.hbox.pop(self.tabbook.get_current_page()-self.n)
            self.vbox.pop(self.tabbook.get_current_page()-self.n)
        else:
            self.n = self.n - 1
        self.tabbook.remove_page(self.tabbook.get_current_page())
        if self.tabbook.get_current_page() == -1:
            self.destroy(self.tabbook)

    def kbd_shortcuts(self, widget):
        self.kbdgroup = gtk.AccelGroup()
        self.window.add_accel_group(self.kbdgroup)
        self.kbdgroup.connect_group(ord('L'), gtk.gdk.CONTROL_MASK, 0, self.select_all_url)
        self.kbdgroup.connect_group(ord('W'), gtk.gdk.CONTROL_MASK, 0, self.removetab)
        self.kbdgroup.connect_group(ord('T'), gtk.gdk.CONTROL_MASK, 0, self.addtab)
        self.kbdgroup.connect_group(ord('R'), gtk.gdk.CONTROL_MASK, 0, self.refresh)
        self.kbdgroup.connect_group(ord('H'), gtk.gdk.CONTROL_MASK, 0, self.historytab)
        self.kbdgroup.connect_group(ord('['), gtk.gdk.CONTROL_MASK, 0, self.go_back)
        self.kbdgroup.connect_group(ord(']'), gtk.gdk.CONTROL_MASK, 0, self.go_forward)
        self.kbdgroup.connect_group(ord('F'), gtk.gdk.CONTROL_MASK, 0, self.search_page)
        self.kbdgroup.connect_group(ord('P'), gtk.gdk.MOD1_MASK, 0, self.show_prefs)

    def select_all_url(self, kbdgroup, window, key, mod):
        self.url_bar[self.tabbook.get_current_page()-self.n].grab_focus()

    def historytab(self, something=None, other=None, somethingelse=None, lol=None):
        self.historysearch = gtk.Entry()
        histclosebutton = gtk.Button('X')
        histclosebutton.connect("activate", self.removetab)
        histclosebutton.connect("clicked", self.removetab)
        self.historysearch.connect("activate", self.search_history)
        historysearchbutton = gtk.Button('Search')
        historysearchbutton.connect("activate", self.search_history)
        historysearchbutton.connect("clicked", self.search_history)
        historysearchbox = gtk.HBox(False, 0)
        historysearchbox.pack_start(self.historysearch, False, True, 0)
        historysearchbox.pack_start(historysearchbutton, False, True, 0)
        historysearchbox.pack_end(histclosebutton, False, True, 0)
        self.historyliststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for item in self.history:
            uri = item[1].rstrip()
            self.historyliststore.append([item[0], uri])
        self.historylistview = gtk.TreeView(self.historyliststore)
        historylistcell = gtk.CellRendererText()
        historylistcell2 = gtk.CellRendererText()
        historylistcol = gtk.TreeViewColumn('Title', historylistcell, text=0)
        historylistcol2 = gtk.TreeViewColumn('URL', historylistcell2, text=1)
        historylistscroll = gtk.ScrolledWindow(None, None)
        historylistscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        historylistscroll.add(self.historylistview)
        self.historylistview.append_column(historylistcol)
        self.historylistview.append_column(historylistcol2)
        self.historybox = gtk.VBox(False, 0)
        self.historybox.pack_start(historysearchbox, False, True, 0)
        self.historybox.pack_start(historylistscroll, True, True, 0)
        self.tabbook.prepend_page(self.historybox)
        self.tabbook.show_all()
        self.tabbook.set_tab_label_text(self.historybox, "History")
        self.tabbook.get_tab_label(self.historybox).set_tooltip_text("History")
        self.tabbook.set_current_page(0)
        self.n = self.n + 1
        self.historylistview.connect("row-activated", self.openhistoryitem)

    def openhistoryitem(self, treeview, path, view_column):
        historyrow, historydata = self.historylistview.get_selection().get_selected()
        historydata = historyrow.get_iter(path[0])
        histurl = historyrow.get_value(historydata, 1)
        self.addtab(None, None, None, None, histurl)

    def search_history(self, whatever=None, something=None, overboard=None):
        histres = []
        if self.historysearch.get_text == "":
            histres = self.history
        else:
            terms = self.historysearch.get_text()
            for row in self.history:
                if row[1].rstrip().find(terms) != -1:
                    histres.append([row[0], row[1].rstrip()])
        histresstore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        for item in histres:
            histresstore.append([item[0], item[1]])
        self.historylistview.set_model(histresstore)

    def search_page(self, some=None, thing=None, other=None, etc=None):
        try:
            self.searchbox.show()
            self.searchentry.grab_focus()
        except:
            self.searchentry = gtk.Entry()
            searchbutton = gtk.Button('Search')
            searchbutton.connect("activate", self.perform_search)
            searchbutton.connect("clicked", self.perform_search)
            self.searchentry.connect("activate", self.perform_search)
            closesearch = gtk.Button('X')
            self.searchbox = gtk.HBox(False, 0)
            closesearch.connect("activate", self.remove_search, self.searchbox, self.searchentry)
            closesearch.connect("clicked", self.remove_search, self.searchbox, self.searchentry)
            self.searchbox.pack_start(self.searchentry, False, True, 0)
            self.searchbox.pack_start(searchbutton, False, True, 0)
            self.searchbox.pack_end(closesearch, False, True, 5)
            self.vbox[self.tabbook.get_current_page()-self.n].pack_end(self.searchbox, False, True, 0)
            self.vbox[self.tabbook.get_current_page()-self.n].show_all()
            self.searchentry.grab_focus()

    def perform_search(self, some=None, thing=None, other=None, etc=None):
        self.web_view[self.tabbook.get_current_page()-self.n].search_text(self.searchentry.get_text(), False, True, True)
        
    def remove_search(self, some, searchbox, searchentry):
        searchbox.hide()

    def download(self, widget, download):
        saveas = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        saveas.set_default_response(gtk.RESPONSE_OK)
        resp = saveas.run()
        if resp == gtk.RESPONSE_OK:
            downloadto = saveas.get_filename()
        saveas.destroy()
        downloadfrom = download.get_network_request().get_uri()
        urllib.urlretrieve(downloadfrom, downloadto)

    def show_prefs(self, widget, some=None, thing=None, other=None):
        self.prefwin = gtk.Window()
        self.prefwin.set_title("Pygmy Preferences")
        self.prefwin.set_default_size(200, 200)

        tabposbox = gtk.HBox(False, 0)
        self.leftbutton = gtk.RadioButton(None, "Left")
        self.topbutton = gtk.RadioButton(self.leftbutton, "Top")
        self.rightbutton = gtk.RadioButton(self.leftbutton, "Right")
        self.bottombutton = gtk.RadioButton(self.leftbutton, "Bottom")
        tabposlabel = gtk.Label("Tab Position:")
        tabposbox.pack_start(tabposlabel, False, True, 5)
        tabposbox.pack_start(self.leftbutton, False, True, 5)
        tabposbox.pack_start(self.topbutton, False, True, 5)
        tabposbox.pack_start(self.rightbutton, False, True, 5)
        tabposbox.pack_start(self.bottombutton, False, True, 5)

        homebox = gtk.HBox(False, 0)
        homelabel = gtk.Label("Homepage: ")
        self.homeentry = gtk.Entry()
        homebox.pack_start(homelabel, False, True, 10)
        homebox.pack_start(self.homeentry, True, True, 10)

        checkbox = gtk.HBox(False, 0)
        self.rssbutton = gtk.CheckButton("Show RSS Tab", False)
        self.histbutton = gtk.CheckButton("Record History", False)
        checkbox.pack_start(self.rssbutton, False, True, 0)
        checkbox.pack_start(self.histbutton, False, True, 0)

        widthbox = gtk.HBox(False, 0)
        widthlabel = gtk.Label("Tab width (in characters):")
        self.widthbutton = gtk.SpinButton()
        self.widthbutton.set_range(0, 99)
        self.widthbutton.set_value(15)
        self.widthbutton.set_increments(1.0, 1.0)
        widthbox.pack_start(widthlabel, False, True, 5)
        widthbox.pack_start(self.widthbutton, False, True, 5)

        donebox = gtk.HBox(False, 0)
        cancelbutton = gtk.Button(stock=gtk.STOCK_CANCEL)
        okbutton = gtk.Button(stock=gtk.STOCK_OK)
        donebox.pack_start(cancelbutton, True, False, 0)
        donebox.pack_start(okbutton, True, False, 0)

        okbutton.connect("activate", self.write_prefs)
        okbutton.connect("clicked", self.write_prefs)
        cancelbutton.connect("activate", self.write_prefs)
        cancelbutton.connect("clicked", self.write_prefs)

        if self.preferences != None:
            if self.preferences[0] == '4':
                bottombutton.set_active(True)
            elif self.preferences[0] == '2':
                self.topbutton.set_active(True)
            elif self.preferences[0] =='3':
                self.rightbutton.set_active(True)
            else:
                self.leftbutton.set_active(True)
            self.homeentry.set_text(self.preferences[1])
            if self.preferences[2] != '0':
               self.rssbutton.set_active(True)
            if self.preferences[3] == '0':
                self.histbutton.set_active(True)
            self.widthbutton.set_value(float(self.preferences[4]))
        
        prefbox = gtk.VBox(False, 0)
        prefbox.pack_start(tabposbox, False, True, 5)
        prefbox.pack_start(homebox, False, True, 5)
        prefbox.pack_start(checkbox, False, True, 5)
        prefbox.pack_start(widthbox, False, True, 5)
        prefbox.pack_start(donebox, False, True, 5)
        self.prefwin.add(prefbox)
        self.prefwin.show_all()

    def write_prefs(self, first):
        if first.get_label() == 'gtk-ok':
            self.preferences = []
            if self.bottombutton.get_active():
                self.preferences.append('4')
            elif self.topbutton.get_active():
                self.preferences.append('2')
            elif self.rightbutton.get_active():
                self.preferences.append('3')
            else:
                self.preferences.append('1')
            if self.homeentry.get_text():
                self.preferences.append(self.homeentry.get_text())
            else:
                self.preferences.append('0')
            if self.rssbutton.get_active():
                self.preferences.append('1')
            else:
                self.preferences.append('0')
            if self.histbutton.get_active():
                self.preferences.append('0')
            else:
                self.preferences.append('1')
            self.preferences.append(str(self.widthbutton.get_value_as_int()))
        self.prefwin.hide()

    def destroy_prefs(self):
        self.prefwin.hide()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    browser = Browser()
    browser.main()

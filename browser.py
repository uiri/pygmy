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

import pygtk, gtk, webkit, gobject, feedparser, os, time, threading, urllib2
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
    hbox = []
    vbox = []
    url_bar = []
    history = []

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        self.historyfile = open(os.path.expanduser("~/pyg/history"), 'w')
        self.historyfile.writelines(self.history)
        self.historyfile.close()
        gtk.main_quit()

    def __init__(self):
        gobject.threads_init()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)
        self.window.set_title("Pygmy Web")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_default_size(600,600)
        self.tabbook = gtk.Notebook()
        self.tabbook.set_tab_pos(gtk.POS_LEFT)
        self.addtab()
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
        
        if not os.path.exists(os.path.expanduser("~/pyg/history")):
            self.historyfile = open(os.path.expanduser("~/pyg/history"), 'w')
            self.historyfile.write("http://www.google.com")
            self.historyfile.close()
        self.historyfile = open(os.path.expanduser("~/pyg/history"), 'r')
        self.history = self.historyfile.readlines()
        self.historyfile.close()

    def rssreader(self):
        try:
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
            self.rssview.get_selection().connect("changed", self.show_rss_entry, self)
            self.tabbook.show_all()
            self.rsslinkcb = 'lol'
        except:
            if not os.path.exists(os.path.expanduser("~/pyg")):
                os.mkdir(os.path.expanduser("~/pyg"))
            if not os.path.exists(os.path.expanduser("~/pyg/feedlist")):
                rssfile = open(os.path.expanduser("~/pyg/feedlist"), "w")
                rssfile.write("None")

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

    def addtab(self, widget=None, dummy=None, dummier=None, dummiest=None, openurl="http://google.com"):
        #webkit.WebView allows us to embed a webkit browser
        #it takes care of going backwards/fowards/reloading
        #it even handles flash
        self.web_view.append(webkit.WebView())
        self.web_view[len(self.web_view)-1].open(openurl)

        #create the back button and connect the action to
        #allow us to go backwards using webkit
        self.back_button.append(gtk.ToolButton(gtk.STOCK_GO_BACK))
        self.back_button[len(self.back_button)-1].connect("clicked", self.go_back)

        #same idea for forward button
        self.forward_button.append(gtk.ToolButton(gtk.STOCK_GO_FORWARD))
        self.forward_button[len(self.forward_button)-1].connect("clicked", self.go_forward)

        #again for refresh
        self.refresh_button.append(gtk.ToolButton(gtk.STOCK_REFRESH))
        self.refresh_button[len(self.refresh_button)-1].connect("clicked", self.refresh)

        #entry bar for typing in and display URLs, when they type in a site
        #and hit enter the on_active function is called
        self.url_bar.append(gtk.Entry())
        self.url_bar[len(self.url_bar)-1].connect("activate", self.on_active)

        self.etcbutton.append(gtk.Button('etc'))
        self.etcbutton[len(self.etcbutton)-1].connect("activate", self.historytab)
        self.etcbutton[len(self.etcbutton)-1].connect("clicked", self.historytab)
        self.newtab.append(gtk.Button('+'))
        self.newtab[len(self.newtab)-1].connect("activate", self.addtab)
        self.newtab[len(self.newtab)-1].connect("clicked", self.addtab)
        self.closetab.append(gtk.Button('X'))
        self.closetab[len(self.closetab)-1].connect("activate", self.removetab)
        self.closetab[len(self.closetab)-1].connect("clicked", self.removetab)

        #anytime a site is loaded the update_buttons will be called
        self.web_view[len(self.web_view)-1].connect("load_committed", self.update_buttons)
        self.web_view[len(self.web_view)-1].connect("load_finished", self.set_tab_title)

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
        self.hbox[len(self.hbox)-1].pack_start(self.etcbutton[len(self.etcbutton)-1], False, True, 0)
        self.vbox[len(self.vbox)-1].pack_start(self.hbox[len(self.hbox)-1], False, True, 0)
        self.vbox[len(self.vbox)-1].pack_start(self.scroll_window[len(self.scroll_window)-1], True, True, 0)
        self.tabbook.append_page(self.vbox[len(self.vbox)-1])
        self.tabbook.show_all()
        self.tabbook.set_current_page(len(self.vbox))

    def on_active(self, widge, data=None):
        '''When the user enters an address in the bar, we check to make
           sure they added the http://, if not we add it for them.  Once
           the url is correct, we just ask webkit to open that site.'''
        url = self.url_bar[self.tabbook.get_current_page()-1].get_text()
        try:
            url.index(" ")
            url = "http://google.ca/search?q=" + url
        except:
            try:
                url.index("://")
            except:
                url = "http://"+url
        self.url_bar[self.tabbook.get_current_page()-1].set_text(url)
        self.web_view[self.tabbook.get_current_page()-1].open(url)

    def go_back(self, widget, data=None, other=None, etc=None):
        '''Webkit will remember the links and this will allow us to go
           backwards.'''
        self.web_view[self.tabbook.get_current_page()-1].go_back()

    def go_forward(self, widget, data=None):
        '''Webkit will remember the links and this will allow us to go
           forwards.'''
        self.web_view[self.tabbook.get_current_page()-1].go_forward()

    def refresh(self, widget, data=None, etc=None, more=None):
        '''Simple makes webkit reload the current back.'''
        self.web_view[self.tabbook.get_current_page()-1].reload()

    def update_buttons(self, widget, data=None):
        '''Gets the current url entry and puts that into the url bar.
           It then checks to see if we can go back, if we can it makes the
           back button clickable.  Then it does the same for the foward
           button.'''
        url = widget.get_main_frame().get_uri()
        self.url_bar[self.tabbook.get_current_page()-1].set_text(url)
        unique = 0
        nurl = url + "\n"
        for h in self.history:
            if nurl == h:
                unique = 1
            if url == h:
                unique = 1
        if unique == 0:
            self.history.append(url + "\n")
        self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()-1], "Loading...")
        self.window.set_title("Loading...")
        self.back_button[self.tabbook.get_current_page()-1].set_sensitive(self.web_view[self.tabbook.get_current_page()-1].can_go_back())
        self.forward_button[self.tabbook.get_current_page()-1].set_sensitive(self.web_view[self.tabbook.get_current_page()-1].can_go_forward())

    def set_tab_title(self, widget, data=None):
        if self.web_view[self.tabbook.get_current_page()-1].get_main_frame().get_title() != None:
            if len(self.web_view[self.tabbook.get_current_page()-1].get_main_frame().get_title()) > 15:
                self.web_view[self.tabbook.get_current_page()-1].execute_script('document.title=document.title.substring(0,12)+"...";')
            self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()-1], self.web_view[self.tabbook.get_current_page()-1].get_main_frame().get_title())
            self.window.set_title(self.tabbook.get_tab_label(self.vbox[self.tabbook.get_current_page()-1]).get_text() + " - Pygmy Web")
        else:
            if len(self.web_view[self.tabbook.get_current_page()-1].get_main_frame().get_uri()) > 15:
                uri = self.web_view[self.tabbook.get_current_page()].get_main_frame().get_uri()[0:12] + "..."
            else:
                uri = self.web_view[self.tabbook.get_current_page()].get_main_frame().get_uri()
            self.tabbook.set_tab_label_text(self.vbox[self.tabbook.get_current_page()], uri)
            self.window.set_title("Pygmy Web")

    def set_window_title(self, widget, weirdpointerthing, n):
        try:
            if self.tabbook.get_tab_label(self.vbox[n-1]) != None:
                self.window.set_title(self.tabbook.get_tab_label(self.vbox[n-1]).get_text() + " - Pygmy Web")
            else:
                self.window.set_title("Pygmy Web")
        except:
            self.window.set_title("RSS Reader - Pygmy Web")


    def removetab(self, widget=None, dummy=None, dummier=None, dummiest=None):
        if self.tabbook.get_current_page() != 0:
            if self.tabbook.get_tab_label_text(self.tabbook.get_nth_page(self.tabbook.get_current_page())) != "History":
                self.web_view.pop(self.tabbook.get_current_page()-1)
                self.back_button.pop(self.tabbook.get_current_page()-1)
                self.forward_button.pop(self.tabbook.get_current_page()-1)
                self.refresh_button.pop(self.tabbook.get_current_page()-1)
                self.url_bar.pop(self.tabbook.get_current_page()-1)
                self.newtab.pop(self.tabbook.get_current_page()-1)
                self.closetab.pop(self.tabbook.get_current_page()-1)
                self.scroll_window.pop(self.tabbook.get_current_page()-1)
                self.hbox.pop(self.tabbook.get_current_page()-1)
                self.vbox.pop(self.tabbook.get_current_page()-1)
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

    def select_all_url(self, kbdgroup, window, key, mod):
        self.url_bar[self.tabbook.get_current_page()-1].grab_focus()

    def historytab(self, something=None, other=None, somethingelse=None, lol=None):
        historysearch = gtk.Entry()
        historysearchbutton = gtk.Button('Search')
        historysearchbox = gtk.HBox(False, 0)
        historysearchbox.pack_start(historysearch, False, True, 0)
        historysearchbox.pack_start(historysearchbutton, False, True, 0)
        historyliststore = gtk.ListStore(gobject.TYPE_STRING)
        for item in self.history:
            uri = item.rstrip()
            historyliststore.append([uri])
        historylistview = gtk.TreeView(historyliststore)
        historylistcell = gtk.CellRendererText()
        historylistcol = gtk.TreeViewColumn('URL', historylistcell, text=0)
        historylistscroll = gtk.ScrolledWindow(None, None)
        historylistscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        historylistscroll.add(historylistview)
        historylistview.append_column(historylistcol)
        self.historybox = gtk.VBox(False, 0)
        self.historybox.pack_start(historysearchbox, False, True, 0)
        self.historybox.pack_start(historylistscroll, True, True, 0)
        self.tabbook.append_page(self.historybox)
        self.tabbook.show_all()
        self.tabbook.set_tab_label_text(self.historybox, "History")

    def main(self):
        gtk.main()


if __name__ == "__main__":
    browser = Browser()
    browser.main()

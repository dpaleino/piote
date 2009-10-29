#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Piote Is an Osm Tag Editor
#
# © 2009, David Paleino <d.paleino@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygtk
pygtk.require("2.0")
import gtk

import Piote
from Piote.Utils import *
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError, DuplicateSectionError
from base64 import b64decode, b64encode
import SignalHandlers as handlers

class PreferencesDialog(gtk.Dialog):
    def __init__(self, widget):
        # TODO: REMOVE!
        self.cfg = SafeConfigParser()
        self.cfg.read("piote.cfg")

        gtk.Dialog.__init__(self,
                            "Preferences",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.set_resizable(False)

        frame = gtk.Frame()
        label = gtk.Label("<b>Authentication</b>")
        label.set_use_markup(True)
        frame.set_label_widget(label)
        frame.set_shadow_type(gtk.SHADOW_NONE)
        align = gtk.Alignment()
        align.set_padding(0,0,12,0)
        vbox = gtk.VBox()
        vbox.pack_start(gtk.Label("Username"))
        username = gtk.Entry()
        vbox.pack_start(username)
        vbox.pack_start(gtk.Label("Password"))
        password = gtk.Entry()
        password.set_visibility(False)
        vbox.pack_start(password)
        align.add(vbox)
        frame.add(align)
        self.vbox.pack_start(frame)

        frame = gtk.Frame()
        label = gtk.Label("<b>API</b>")
        label.set_use_markup(True)
        frame.set_label_widget(label)
        frame.set_shadow_type(gtk.SHADOW_NONE)
        align = gtk.Alignment()
        align.set_padding(0,0,12,0)
        vbox = gtk.VBox()
        api = gtk.RadioButton(label="api.openstreetmap.org")
        api06dev = gtk.RadioButton(group=api, label="api06.dev.openstreetmap.org")
        try:
            if self.cfg.get("DEFAULT", "api") == "api.openstreetmap.org":
                api.set_active(True)
            else:
                api06dev.set_active(True)
        except NoOptionError:
            api.set_active(True)
        vbox.pack_start(api)
        vbox.pack_start(api06dev)
        align.add(vbox)
        frame.add(align)
        self.vbox.pack_start(frame)

        username.connect("activate", check_empty, "Username", self)
        password.connect("activate", check_empty, "Password", self)

        api.connect("toggled", self.__api_changed, "api.openstreetmap.org")
        api06dev.connect("toggled", self.__api_changed, "api06.dev.openstreetmap.org")

        # populate fields
        try:
            username.set_text(self.cfg.get("Authentication", "username"))
            password.set_text(b64decode(self.cfg.get("Authentication", "password")))
        except NoSectionError, NoOptionError:
            pass

        self.vbox.show_all()
        response = self.run()
        self.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(username, "Username") and check_empty(password, "Password"):
                try:
                    self.cfg.add_section("Authentication")
                except DuplicateSectionError:
                    pass
                finally:
                    self.cfg.set("Authentication", "username", username.get_text())
                    self.cfg.set("Authentication", "password", b64encode(password.get_text()))
                    self.cfg.set("DEFAULT", "api", Piote.api_url)
                try:
                    self.cfg.write(open("piote.cfg", "w"))
                except IOError:
                    print "Cannot write to piote.cfg!"

    def __api_changed(self, widget, api):
        if widget.get_active():
            Piote.api_url = api
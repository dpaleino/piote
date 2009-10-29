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
import sys, string

from ConfigParser import SafeConfigParser, DuplicateSectionError, NoSectionError, NoOptionError

import Piote
from Piote.AboutDialog import AboutDialog
from Piote.OsmApi import OsmApi
from Piote.Utils import *

from collections import defaultdict
from base64 import b64encode, b64decode

class Main():
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Piote %s" % Piote.version)
        self.obj = ""
        self.api_url = "api.openstreetmap.org"
        self.makegui(self.window)
        self.connect_signals()

        # OSM username and password
        self.cfg = SafeConfigParser()
        if not self.cfg.read("piote.cfg"):
            self.pref_clicked(None)
        self.api = OsmApi(api=self.cfg.get("DEFAULT", "api"),
                          username=self.cfg.get("Authentication", "username"),
                          password=b64decode(self.cfg.get("Authentication", "password")),
                          appid="Piote/%s" % Piote.version)

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def search_id(self, widget):
        self.obj = self.combobox.get_active_text()

        # FIXME: this is here, instead of connect_signals(), because otherwise self.obj is ""
        self.savebutton.connect("clicked", self.set_changeset_msg, self.obj.lower(), self.tagsview.get_model())

        self.id = self.entry.get_text()

        if not self.obj:
            # no object has been chosen
            print "Foo!"
        else:
            try:
                self.get(self.obj.lower(), int(self.id))
            except ValueError:
                print "Bar!"
            except:
                raise

    def show_about(self, widget):
        about = AboutDialog()
        about.run()
        about.destroy()

    def cell_edited(self, cell, path, new_text, selection):
        (model, _iter) = selection.get_selected()
        print repr(model)
        print repr(_iter)
        model[_iter][0] = new_text
        # FIXME:     ↑ cambia sempre la prima colonna.. devo trovare COME passare il numero di colonna all'evento
        pass

    def row_activated(self, widget, event, data=None):
        (model, iter) = widget.get_selection().get_selected()
        dlg = gtk.Dialog("Editing tag",
                         None,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.vbox.pack_start(gtk.Label("Key:"))
        key = gtk.Entry()
        key.set_text(model[iter][0])
        dlg.vbox.pack_start(key)
        dlg.vbox.pack_start(gtk.Label("Value:"))
        value = gtk.Entry()
        value.set_text(model[iter][1])
        dlg.vbox.pack_start(value)
        dlg.vbox.show_all()

        key.connect("activate", check_empty, "Key", dlg)
        value.connect("activate", check_empty, "Value", dlg)

        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(key, "Key") and check_empty(key, "Value"):
                model[iter][0] = key.get_text()
                model[iter][1] = value.get_text()

    def api_changed(self, widget, api):
        if widget.get_active():
            self.api_url = api

    def pref_clicked(self, widget):
        # try to load the configuration
        dlg = gtk.Dialog("Preferences",
                         None,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.set_resizable(False)
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
        dlg.vbox.pack_start(frame)

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
        dlg.vbox.pack_start(frame)

        username.connect("activate", check_empty, "Username", dlg)
        password.connect("activate", check_empty, "Password", dlg)

        api.connect("toggled", self.api_changed, "api.openstreetmap.org")
        api06dev.connect("toggled", self.api_changed, "api06.dev.openstreetmap.org")

        # populate fields
        try:
            username.set_text(self.cfg.get("Authentication", "username"))
            password.set_text(b64decode(self.cfg.get("Authentication", "password")))
        except NoSectionError, NoOptionError:
            pass

        dlg.vbox.show_all()
        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(username, "Username") and check_empty(password, "Password"):
                try:
                    self.cfg.add_section("Authentication")
                except DuplicateSectionError:
                    pass
                finally:
                    self.cfg.set("Authentication", "username", username.get_text())
                    self.cfg.set("Authentication", "password", b64encode(password.get_text()))
                    self.cfg.set("DEFAULT", "api", self.api_url)
                    try:
                        self.cfg.write(open("piote.cfg", "w"))
                    except IOError:
                        print "Cannot write to piote.cfg!"

    def add_tag(self, widget):
        dlg = gtk.Dialog("Adding tag",
                         None,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.vbox.pack_start(gtk.Label("Key:"))
        key = gtk.Entry()
        dlg.vbox.pack_start(key)
        dlg.vbox.pack_start(gtk.Label("Value:"))
        value = gtk.Entry()
        dlg.vbox.pack_start(value)
        dlg.vbox.show_all()

        key.connect("activate", check_empty, "Key", dlg)
        value.connect("activate", check_empty, "Value", dlg)

        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(key, "Key") and check_empty(value, "Value"):
                key = key.get_text()
                value = value.get_text()
                for row in self.tags:
                    if row[0] == key:
                        row[1] = value
                        return True
                self.tags.append(None, [key, value])

    def del_tag(self, widget, selection):
        (store, iter) = selection.get_selected()
        store.remove(iter)

    def get(self, obj, id):
        # Clear the previous data
        self.tags.clear()

        if obj == "node":
            f = self.api.NodeGet
        elif obj == "way":
            f = self.api.WayGet
        elif obj == "relation":
            f = self.api.RelationGet
        self.data = f(id)
        tags = self.data["tag"]

        for key in tags:
            self.tags.append(None, [key, tags[key]])

        # set sensitivity
        self.addbutton.set_flags(gtk.SENSITIVE)
        self.delbutton.set_flags(gtk.SENSITIVE)
        self.savebutton.set_flags(gtk.SENSITIVE)

    def put(self, msg, obj, model):
        changeset = self.api.ChangesetCreate({u"comment": unicode(msg)})
        tags = defaultdict(str)

        for row in model:
            tags[unicode(row[0])] = unicode(row[1])

        self.data["tag"] = tags

        if obj == "node":
            f = self.api.NodeUpdate
        elif obj == "way":
            f = self.api.WayUpdate
        elif obj == "relation":
            f = self.api.RelationUpdate
        result = f(self.data)
        self.data["version"] = result["version"]

        #self.api.ChangesetUpload([{"type":obj, "action":"modify", "data":self.data}])
        self.api.ChangesetClose()

    def set_changeset_msg(self, widget, obj, model):
        dlg = gtk.Dialog("Uploading changeset",
                         None,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.vbox.pack_start(gtk.Label("Changeset message:"))
        msg = gtk.Entry()
        dlg.vbox.pack_start(msg)
        dlg.vbox.show_all()

        msg.connect("activate", lambda x: dlg.response(gtk.RESPONSE_ACCEPT))

        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(msg, "Message"):
                msg = msg.get_text()
                self.put(msg, obj, model)

    def connect_signals(self):
        self.window.connect("delete_event", self.delete_event)
        self.okbutton.connect("clicked", self.search_id)
        self.prefbutton.connect("clicked", self.pref_clicked)
        self.entry.connect("activate", self.search_id)
        self.aboutbutton.connect("clicked", self.show_about)
        self.tagsview.connect("row-activated", self.row_activated)
        self.addbutton.connect("clicked", self.add_tag)
        self.delbutton.connect("clicked", self.del_tag, self.tagsview.get_selection())
        #self.cell.connect("edited", self.cell_edited, self.tagsview.get_selection())

    def makegui(self, window):
        window.set_border_width(10)
        window.set_geometry_hints(max_height = 400)

        vbox = gtk.VBox(False, 0)
        hbox = gtk.HBox(False, 0)
        buttonbox = gtk.HBox(False, 0)
        savebox = gtk.HBox(False, 0)
        self.combobox = gtk.combo_box_new_text()
        self.entry = gtk.Entry()

        self.okbutton = gtk.Button(stock="gtk-ok")
        self.okbutton.set_use_underline(True)
        self.addbutton = gtk.Button(stock="gtk-add")
        self.addbutton.set_use_underline(True)
        self.delbutton = gtk.Button(stock="gtk-remove")
        self.delbutton.set_use_underline(True)
        self.prefbutton = gtk.Button(stock="gtk-preferences")
        self.prefbutton.set_use_underline(True)
        self.aboutbutton = gtk.Button(stock="gtk-about")
        self.aboutbutton.set_use_underline(True)
        self.savebutton = gtk.Button(stock="gtk-save")
        self.savebutton.set_use_underline(True)

        for obj in ["Node", "Way", "Relation"]:
            self.combobox.append_text(obj)

        hbox.pack_start(self.combobox, True, True, 0)
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(self.okbutton, True, False, 0)
        hbox.pack_start(self.prefbutton, True, False, 0)
        hbox.pack_start(self.aboutbutton, True, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        self.addbutton.unset_flags(gtk.SENSITIVE)
        buttonbox.pack_start(self.addbutton, True, True, 0)
        self.delbutton.unset_flags(gtk.SENSITIVE)
        buttonbox.pack_start(self.delbutton, True, True, 0)
        vbox.pack_start(buttonbox, False, False, 0)

        self.tags = gtk.TreeStore(str, str)
        #self.tags.append(None, None)
        self.tagsview = gtk.TreeView(self.tags)

        col = gtk.TreeViewColumn("Key")
        self.cell = gtk.CellRendererText()
        #self.cell.set_property("editable", True)
        col.pack_start(self.cell, True)
        col.add_attribute(self.cell, "text", 0)
        col.set_sort_column_id(0)
        self.tagsview.append_column(col)

        col = gtk.TreeViewColumn("Value")
        col.pack_start(self.cell, True)
        col.add_attribute(self.cell, "text", 1)
        self.tagsview.append_column(col)

        self.tagsview.set_search_column(0)
        vbox.pack_start(self.tagsview, True, True, 0)

        self.savebutton.unset_flags(gtk.SENSITIVE)
        savebox.pack_start(self.savebutton, True, False, 0)
        vbox.pack_start(savebox, False, False, 0)
        self.window.add(vbox)

        vbox.show_all()
        self.window.show()

if __name__ == "__main__":
    Main()
    gtk.main()

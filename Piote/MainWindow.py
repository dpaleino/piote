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
from OsmWrapper import OsmWrapper
from TagDialog import AddTagDialog
from PreferencesDialog import PreferencesDialog
from AboutDialog import AboutDialog
from ChangesetDialog import ChangesetDialog

class MainWindow():
    def __init__(self):
        self.obj = ""
        Piote.API = OsmWrapper()

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Piote %s" % Piote.version)
        window.set_border_width(10)
        window.set_geometry_hints(max_height = 400)
        window.connect("delete_event", self.__delete_event)

        vbox = gtk.VBox(False, 0)
        window.add(vbox)

        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)

        buttonbox = gtk.HBox(False, 0)
        vbox.pack_start(buttonbox, False, False, 0)

        self.tags = gtk.TreeStore(str, str)
        #tags.append(None, None)
        self.tagsview = gtk.TreeView(self.tags)
        vbox.pack_start(self.tagsview, True, True, 0)

        savebox = gtk.HBox(False, 0)
        vbox.pack_start(savebox, False, False, 0)

        self.status = gtk.Statusbar()
        vbox.pack_start(self.status, False, False, 0)

        self.combobox = gtk.combo_box_new_text()
        for obj in ["Node", "Way", "Relation"]:
            self.combobox.append_text(obj)
        hbox.pack_start(self.combobox, True, True, 0)

        self.entry = gtk.Entry()
        self.entry.connect("activate", self.__search_id)
        hbox.pack_start(self.entry, True, True, 0)

        okbutton = gtk.Button(stock="gtk-ok")
        okbutton.set_use_underline(True)
        okbutton.connect("clicked", self.__search_id)
        hbox.pack_start(okbutton, True, False, 0)

        self.addbutton = gtk.Button(stock="gtk-add")
        self.addbutton.set_use_underline(True)
        self.addbutton.unset_flags(gtk.SENSITIVE)
        #self.addbutton.connect("clicked", AddTagDialog, self.tags)
        buttonbox.pack_start(self.addbutton, True, True, 0)

        self.delbutton = gtk.Button(stock="gtk-remove")
        self.delbutton.set_use_underline(True)
        self.delbutton.unset_flags(gtk.SENSITIVE)
        self.delbutton.connect("clicked", self.__del_tag, self.tagsview.get_selection())
        buttonbox.pack_start(self.delbutton, True, True, 0)

        prefbutton = gtk.Button(stock="gtk-preferences")
        prefbutton.set_use_underline(True)
        prefbutton.connect("clicked", PreferencesDialog)
        hbox.pack_start(prefbutton, True, False, 0)

        aboutbutton = gtk.Button(stock="gtk-about")
        aboutbutton.set_use_underline(True)
        aboutbutton.connect("clicked", AboutDialog)
        hbox.pack_start(aboutbutton, True, False, 0)

        col = gtk.TreeViewColumn("Key")
        cell = gtk.CellRendererText()
        self.addbutton.connect("clicked", self.__add_tag, (col, cell))
        cell.set_property("editable", True)
        cell.set_property("weight", 800)
        cell.connect("edited", self.__cell_edited, self.tagsview.get_selection(), 0)

        col.pack_start(cell, True)
        col.add_attribute(cell, "text", 0)
        col.set_sort_column_id(0)
        self.tagsview.append_column(col)

        col = gtk.TreeViewColumn("Value")
        cell = gtk.CellRendererText()
        cell.set_property("editable", True)
        cell.connect("edited", self.__cell_edited, self.tagsview.get_selection(), 1)

        col.pack_start(cell, True)
        col.add_attribute(cell, "text", 1)

        self.tagsview.append_column(col)

        self.tagsview.set_search_column(0)

        self.savebutton = gtk.Button(stock="gtk-save")
        self.savebutton.set_use_underline(True)
        self.savebutton.unset_flags(gtk.SENSITIVE)
        savebox.pack_start(self.savebutton, True, False, 0)

        vbox.show_all()
        window.show()

    def __delete_event(widget, event, data=None):
        gtk.main_quit()
        return False

    def __search_id(self, widget):
        self.obj = self.combobox.get_active_text()

        # FIXME: this is here, instead of connect_signals(), because otherwise self.obj is ""
        self.savebutton.connect("clicked", ChangesetDialog, self.obj.lower(), self.tagsview.get_model())

        if not self.obj:
            # no object has been chosen
            self.status.push(0, "No object has been chosen!")
        else:
            try:
                # Clear the previous data
                self.tags.clear()
                tags = Piote.API.Get(self.obj.lower(), int(self.entry.get_text()))
                for key in tags:
                    self.tags.append(None, [key, tags[key]])

                    # set sensitivity
                    self.addbutton.set_flags(gtk.SENSITIVE)
                    self.delbutton.set_flags(gtk.SENSITIVE)
                    self.savebutton.set_flags(gtk.SENSITIVE)
            except ValueError:
                self.status.push(0, "No valid ID has been entered!")

    def __add_tag(self, widget, data):
        self.new_row_iter = self.tags.append(None, ["",""])
        # FIXME: the usage of __len__() - 1 seems quite hackish.
        self.tagsview.set_cursor_on_cell(self.tags.__len__() - 1, focus_column=data[0], focus_cell=data[1], start_editing=True)

    def __del_tag(self, widget, selection):
        (store, iter) = selection.get_selected()
        store.remove(iter)

    def __cell_edited(self, cell, path, new_text, selection, column):
        (model, _iter) = selection.get_selected()
        if column == 0:
            # i.e. if it's the Key column the one being edited
            for row in model:
                keyfound = False
                if row[0] == new_text:
                    # i.e. the newly entered key is already present
                    # FIXME: should get a <path> somehow
                    #self.tagsview.set_cursor_on_cell(<path>, focus_cell=<value>, start_editing=True)
                    keyfound = True
                    model.remove(self.new_row_iter)
                    self.status.push(0, "Key already existing!")
                    break

            if not keyfound:
                model[_iter][column] = new_text
        else:
            model[_iter][column] = new_text

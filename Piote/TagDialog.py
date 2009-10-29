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

from Utils import *

class TagDialog(gtk.Dialog):
    def __init__(self, mode, widget, tags):
        if mode == "new":
            title = "Adding tag"
            model = None
            key_text = ""
            value_text = ""
        elif mode == "edit":
            title = "Editing tag"
            model, iter = widget.get_selection().get_selected()
            key_text = model[iter][0]
            value_text = model[iter][1]

        gtk.Dialog.__init__(self,
                            title,
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.vbox.pack_start(gtk.Label("Key:"))
        key = gtk.Entry()
        key.set_text(key_text)
        self.vbox.pack_start(key)

        self.vbox.pack_start(gtk.Label("Value:"))
        value = gtk.Entry()
        value.set_text(value_text)
        self.vbox.pack_start(value)

        self.vbox.show_all()

        key.connect("activate", check_empty, "Key", self)
        value.connect("activate", check_empty, "Value", self)

        response = self.run()
        self.destroy()

        already_key = False
        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(key, "Key") and check_empty(value, "Value"):
                self.key = key.get_text()
                self.value = value.get_text()

                if model:
                    model[iter][0] = self.key
                    model[iter][1] = self.value
                else:
                    for row in tags:
                        if row[0] == self.key:
                            already_key = True
                            row[1] = self.value

                    if not already_key:
                        tags.append(None, [self.key, self.value])

class AddTagDialog(TagDialog):
    def __init__(self, tags):
        TagDialog.__init__(self, "new", None, tags)

class EditTagDialog(TagDialog):
    def __init__(self, widget, tags):
        TagDialog.__init__(self, "edit", widget, tags)
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

class ChangesetDialog(gtk.Dialog):
    def __init__(self, widget, obj, model):
        gtk.Dialog.__init__(self,
                            "Uploading changeset",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.vbox.pack_start(gtk.Label("Changeset message:"))
        msg = gtk.Entry()
        self.vbox.pack_start(msg)
        self.vbox.show_all()

        msg.connect("activate", lambda x: dlg.response(gtk.RESPONSE_ACCEPT))

        response = self.run()
        self.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if check_empty(msg, "Message"):
                msg = msg.get_text()
                osm = OsmWrapper()
                osm.Put(msg, obj, model)
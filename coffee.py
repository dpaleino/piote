#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import time
import base64
import httplib, urllib
from lxml import etree
from StringIO import StringIO

version = "0.0alpha2"

# This should be your username or e-mail address
user = "d.paleino@gmail.com"

# Put here your password
password = ""

class Coffee():
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.obj = ""
        self.makegui(self.window)
        self.connect_signals()

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def search_id(self, widget):
        self.obj = self.combobox.get_active_text()

        # FIXME: this is here, instead of connect_signals(), because otherwise self.obj is ""
        self.savebutton.connect("clicked", self.putxml, self.obj.lower(), self.tagsview.get_model())

        self.id = self.entry.get_text()

        if not self.obj:
            print "Foo!"
        else:
            try:
                self.getxml(self.obj.lower(), int(self.id))
            except ValueError:
                print "Bar!"
            except:
                raise

    def show_about(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("Coffee")
        about.set_version(version)
        about.set_copyright("© 2009, David Paleino <d.paleino@gmail.com>")
        about.set_license("""Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""")
        about.set_wrap_license(True)
        about.run()
        about.destroy()

    def cell_edited(self, cell, path, new_text, selection):
        (model, _iter) = selection.get_selected()
        print repr(model)
        print repr(_iter)
        model[_iter][0] = new_text
        # FIXME:     ↑ cambia sempre la prima colonna.. devo trovare COME passare il numero di colonna all'evento
        pass

    def check_empty(self, widget, field):
        print repr(widget)
        print repr(widget.get_text())
        if widget.get_text() == "":
            warn = gtk.Dialog("Error",
                              None,
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                              (gtk.STOCK_OK, gtk.RESPONSE_REJECT))
            warn.vbox.pack_start(gtk.Label("Cannot leave %s empty" % field))
            warn.vbox.show_all()
            warn.run()
            warn.destroy()
            return False
        else:
            return True

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

        key.connect("activate", self.check_empty, "Key")
        value.connect("activate", self.check_empty, "Value")

        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if self.check_empty(key, "Key") and self.check_empty(key, "Value"):
                model[iter][0] = key.get_text()
                model[iter][1] = value.get_text()

    def pref_clicked(self, widget):
        id = self.open_changeset("my test changeset")
        print repr(id)
        self.close_changeset(id)
        print repr("Changeset %d" % id)

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

        key.connect("activate", self.check_empty, "Key")
        value.connect("activate", self.check_empty, "Value")

        response = dlg.run()
        dlg.destroy()

        if response == gtk.RESPONSE_ACCEPT:
            if self.check_empty(key, "Key") and self.check_empty(value, "Value"):
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

    def getxml(self, obj, id):
        host = "api.openstreetmap.org"
        query = "/api/0.6/%s/%d" % (obj, id)

        conn = httplib.HTTPConnection(host)
        conn.request("GET", query)
        res = conn.getresponse()
        self.tags.clear()
        if res.status == 200:
            self.xml = res.read()
            parser = etree.XMLParser()
            tree = etree.parse(StringIO(self.xml), parser)
            for tag in tree.iter(tag="tag"):
                print repr("%s %s" % (tag.get("k"), tag.get("v")))
                self.tags.append(None, [tag.get("k"), tag.get("v")])

    def open_changeset(self, comment):
        conn = httplib.HTTP("api.openstreetmap.org")
        conn.putrequest("PUT", "/api/0.6/changeset/create")
        xml = """<osm version='0.6' generator='Coffee'>
  <changeset visible='true'>
    <tag k='created_by' v='Coffee/%s' />
    <tag k='comment' v='%s' />
  </changeset>
</osm>""" % (version, comment)
        conn.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        conn.putheader("Host", "www.openstreetmap.org")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Authorization", "Basic " + string.strip(base64.encodestring(user + ":" + password)))
        conn.putheader("Content-Length", str(len(xml)))
        conn.endheaders()
        conn.send(xml)

        print repr(conn.getreply())
        return conn.getfile().read()

    def close_changeset(self, id):
        conn = httplib.HTTP("api.openstreetmap.org")
        conn.putrequest("PUT", "/api/0.6/changeset/%s/close" % id)
        conn.putheader("Host", "www.openstreetmap.org")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Authorization", "Basic " + string.strip(base64.encodestring(email + ":" + password)))
        conn.endheaders()
        statuscode, statusmessage, header = conn.getreply()

    def putxml(self, widget, primitive, model):
        parser = etree.XMLParser()
        tree = etree.parse(StringIO(self.xml), parser)
        changeset = self.open_changeset("comment")
        #changeset = "foo"
        tags = {}
        f = StringIO()

        # let's fix general attributes
        for osm in tree.iter(tag="osm"):
            osm.set("generator", "Coffee %s" % version)
        for obj in tree.iter(tag=primitive):
            # <way id="123" visible="true" timestamp="2009-03-31T09:35:43Z" version="7" changeset="872162" user="saftl" uid="7989">
            objectid = obj.get("id")
            #obj.set("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
            #obj.set("version", str(int(obj.get("version")) + 1))
            obj.set("changeset", changeset)

            for tag in tree.iter(tag="tag"):
                obj.remove(tag)
            for row in model:
                    print repr("%s %s" % (unicode(row[0]), unicode(row[1])))
                    obj.append(etree.Element("tag", attrib={"k": unicode(row[0]), "v": unicode(row[1])}))

        print repr("Object: %s" % objectid)
        tree.write(f, encoding="UTF-8", xml_declaration=True)
        f.seek(0)
        xml = f.read()
        f.close()
        print repr(xml)
        conn = httplib.HTTP("api.openstreetmap.org")
        conn.putrequest("PUT", "/api/0.6/%s/%s" % (primitive, objectid))
        conn.putheader("Host", "www.openstreetmap.org")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Authorization", "Basic " + string.strip(base64.encodestring(email + ":" + password)))
        conn.putheader("Content-Length", str(len(xml)))
        conn.endheaders()
        conn.send(xml)
        reply = conn.getreply()
        print repr(reply)
        print repr(conn.getfile().read())
        self.close_changeset(changeset)
        print repr("Changeset: %s" % changeset)

    def connect_signals(self):
        self.window.connect("delete_event", self.delete_event)
        self.okbutton.connect("clicked", self.search_id)
        #self.prefbutton.connect("clicked", self.pref_clicked)
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
        self.addbutton = gtk.Button(stock="gtk-add")
        self.delbutton = gtk.Button(stock="gtk-remove")
        self.prefbutton = gtk.Button(stock="gtk-preferences")
        self.aboutbutton = gtk.Button(stock="gtk-about")
        self.savebutton = gtk.Button(stock="gtk-save")

        for obj in ["Node", "Way", "Relation"]:
            self.combobox.append_text(obj)

        hbox.pack_start(self.combobox, True, True, 0)
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(self.okbutton, True, False, 0)
        hbox.pack_start(self.prefbutton, True, False, 0)
        hbox.pack_start(self.aboutbutton, True, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        buttonbox.pack_start(self.addbutton, True, True, 0)
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

        savebox.pack_start(self.savebutton, True, False, 0)
        vbox.pack_start(savebox, False, False, 0)
        self.window.add(vbox)

        vbox.show_all()
        self.window.show()

if __name__ == "__main__":
    Coffee()
    gtk.main()

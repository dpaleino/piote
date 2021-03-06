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

from base64 import b64decode
from Config import Config, NoOptionError
from OsmApi import OsmApi
from collections import defaultdict

import Piote

class OsmWrapper():
    def __init__(self, url=None, api=None):
        self.cfg = Config()
        if url:
            self.url = url
        else:
            try:
                self.url = self.cfg.get("DEFAULT", "api")
            except NoOptionError:
                self.url = "api.openstreetmap.org"

        if not api:
            self.api = OsmApi(api=self.url,
                          username=self.cfg.get("Authentication", "username"),
                          password=b64decode(self.cfg.get("Authentication", "password")),
                          appid="Piote/%s" % Piote.version)
        else:
            self.api = api

    def Get(self, obj, id):
        if obj == "node":
            f = self.api.NodeGet
        elif obj == "way":
            f = self.api.WayGet
        elif obj == "relation":
            f = self.api.RelationGet
        Piote.data = f(id)
        self.data = Piote.data
        return Piote.data["tag"]

    def Put(self, msg, obj, model, data=None):
        changeset = self.api.ChangesetCreate({u"comment": unicode(msg, "utf-8")})
        tags = defaultdict(str)

        for row in model:
            tags[unicode(row[0], "utf-8")] = unicode(row[1], "utf-8")

        if data:
            data["tag"] = tags
        else:
            Piote.data["tag"] = tags

        if obj == "node":
            f = self.api.NodeUpdate
        elif obj == "way":
            f = self.api.WayUpdate
        elif obj == "relation":
            f = self.api.RelationUpdate

        if data:
            result = f(data)
            data["version"] = result["version"]
        else:
            result = f(Piote.data)
            Piote.data["version"] = result["version"]

        #self.api.ChangesetUpload([{"type":obj, "action":"modify", "data":self.data}])
        self.api.ChangesetClose()

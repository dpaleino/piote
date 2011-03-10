#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
from bottle import *
from Piote.OsmWrapper import OsmWrapper
from Piote.OsmApi import OsmApi
import Piote

@route("/")
def index():
    bottle.TEMPLATES.clear()
    return template("index")

@route('/static/:filename')
def static_file(filename):
    import datetime
    from time import strftime, gmtime
    time = gmtime()
    # expire after one week
    time = (datetime.datetime(*time[:6]) + datetime.timedelta(7)).timetuple()
    response.header["Expires"] = strftime("%a, %d %b %Y %H:%M:%S GMT", time)
    send_file(filename, root="static")

@route('/slippy/:object/:id')
@validate(object=str, id=int)
def get_slippymap(object, id):
    response.header["Pragma"] = "no-cache"
    response.header["Expires"] = "-1"
    response.content_type = "text/javascript"
    script = """OpenLayers.Lang.setCode("it");

function makemap() {
    var map = createMap("small_map", {
    controls: [ new OpenLayers.Control.Navigation() ]
    });

    var obj_type = "%s";
    var obj_id = %s;
    var url = "/api/0.6/%s/%s";

    if (obj_type != "node") {
        url += "/full";
    }

    addObjectToMap(url, true, function(extent) {
        $("loading").innerHTML = "";

        if (extent) {
            extent.transform(map.getProjectionObject(), map.displayProjection);
            $("area_larger_map").href = '/?minlon='+extent.left+'&minlat='+extent.bottom+'&maxlon='+extent.right+'&maxlat='+extent.top;
            $("area_larger_map").innerHTML = "View area on larger map";
            $("object_larger_map").href = '/?%s=%s';
            $("object_larger_map").innerHTML = "View way on larger map";
        } else {
            $("small_map").style.display = "none";
        }
    });
}""" % (object, id, object, id, object, id)

    return script

@route("/api/0.6/:object/:id")
@route("/api/0.6/:object/:id/:full")
@validate(object=str, id=int)
def get_xml(object, id, full=None):
    from urllib2 import urlopen
    response.content_type = "text/xml"
    url = "http://www.openstreetmap.org/api/0.6/%s/%s%s"
    if full:
        return urlopen(url % (object, id, "/full")).fp.readlines()
    else:
        return urlopen(url % (object, id, "")).fp.readlines()

@route("/:object/:id")
@validate(object=str, id=int)
def get_object(object, id):
    if object not in ["node", "way", "relation"]:
        abort(400, "The only accepted primitives are <b>node</b>, <b>way</b> and <b>relation</b>.")

    myapi = OsmApi(api="api06.dev.openstreetmap.org", appid="Piote/%s (web)" % Piote.version)
    osm = OsmWrapper(api=myapi)

    try:
        tags = osm.Get(object,id)
    except Exception:
        print repr(Exception)
        return {"piote_status" : "notfound"}

    Piote.data = osm.data

    if not tags:
        return {"piote_status" : "notags"}
    else:
        return tags

@route("/put/:object/:id", method="POST")
@validate(object=str, id=int)
def upload_object(object, id):
    if object not in ["node", "way", "relation"]:
        abort(403, "The only accepted primitives are <b>node</b>, <b>way</b> and <b>relation</b>.")

    changeset = request.POST["changeset"]
    username = request.POST["email"]
    password = request.POST["password"]

    tags = []
    keys = {}
    values = {}
    # do a first pass to store keys
    for key, value in request.POST.iteritems():
        m = re.match("key_(\d+)", key)
        if m:
            keys[m.group(1)] = request.POST["key_%s" % m.group(1)]
        m = re.match("value_(\d+)", key)
        if m:
            print repr(value)
            values[m.group(1)] = request.POST["value_%s" % m.group(1)]

    # do a second pass to make it the real thing
    i = 0
    while i < len(keys):
        tags.append((keys[str(i)], values[str(i)]))
        i += 1

    print repr(tags)
    myapi = OsmApi(api="api06.dev.openstreetmap.org",
                username=username,
                password=password,
                appid="Piote/%s (web)" % Piote.version)
    osm = OsmWrapper(api=myapi)
    osm.Put(changeset, object, tags, data=Piote.data)
    return []

if __name__ == "__main__":
    bottle.debug(True)
    #bottle.default_app().autojson = False
    run(host='192.168.1.33', port=80, reloader=True)

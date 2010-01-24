var epsg4326 = new OpenLayers.Projection("EPSG:4326");
var map;
var markers;
var vectors;
var popup;

function createMap(divName, options) {
   options = options || {};

   map = new OpenLayers.Map(divName, {
      controls: options.controls || [
         new OpenLayers.Control.ArgParser(),
         new OpenLayers.Control.Attribution(),
         new OpenLayers.Control.LayerSwitcher(),
         new OpenLayers.Control.Navigation(),
         new OpenLayers.Control.PanZoom(),
         new OpenLayers.Control.PanZoomBar()
      ],
      units: "m",
      maxResolution: 156543.0339,
      numZoomLevels: 20,
      displayProjection: new OpenLayers.Projection("EPSG:4326")
   });

   var mapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik", {
      displayOutsideMaxExtent: true,
      wrapDateLine: true
   });
   map.addLayer(mapnik);

   var numZoomLevels = mapnik.numZoomLevels;

   markers = new OpenLayers.Layer.Markers("Markers", {
      displayInLayerSwitcher: false,
      numZoomLevels: numZoomLevels,
      maxExtent: new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508),
      maxResolution: 156543,
      units: "m",
      projection: "EPSG:900913"
   });
   map.addLayer(markers);

   return map;
}

function getArrowIcon() {
   var size = new OpenLayers.Size(25, 22);
   var offset = new OpenLayers.Pixel(-30, -27);
   var icon = new OpenLayers.Icon("/images/arrow.png", size, offset);

   return icon;
}

function addMarkerToMap(position, icon, description) {
   var marker = new OpenLayers.Marker(position.clone().transform(epsg4326, map.getProjectionObject()), icon);

   markers.addMarker(marker);

   if (description) {
      marker.events.register("click", marker, function() { openMapPopup(marker, description) });
   }

   return marker;
}

function addObjectToMap(url, zoom, callback) {
   var layer = new OpenLayers.Layer.GML("Objects", url, {
      format: OpenLayers.Format.OSM,
      style: {
          strokeColor: "blue",
          strokeWidth: 3,
          strokeOpacity: 0.5,
          fillOpacity: 0.2,
          fillColor: "lightblue",
          pointRadius: 6
      },
      projection: new OpenLayers.Projection("EPSG:4326"),
      displayInLayerSwitcher: false
   });

   layer.events.register("loadend", layer, function() {
      var extent;

      if (this.features.length) {
         extent = this.features[0].geometry.getBounds();

         for (var i = 1; i < this.features.length; i++) {
            extent.extend(this.features[i].geometry.getBounds());
         }

         if (zoom) {
            if (extent) {
               this.map.zoomToExtent(extent);
            } else {
               this.map.zoomToMaxExtent();
            }
         }
      }

      if (callback) {
         callback(extent);
      }
   });

   map.addLayer(layer);

   layer.loadGML();
}

function addBoxToMap(boxbounds) {
   if (!vectors) {
     // Be aware that IE requires Vector layers be initialised on page load, and not under deferred script conditions
     vectors = new OpenLayers.Layer.Vector("Boxes", {
        displayInLayerSwitcher: false
     });
     map.addLayer(vectors);
   }
   var geometry = boxbounds.toGeometry().transform(epsg4326, map.getProjectionObject());
   var box = new OpenLayers.Feature.Vector(geometry, {}, {
      strokeWidth: 2,
      strokeColor: '#ee9900',
      fillOpacity: 0
   });

   vectors.addFeatures(box);

   return box;
}

function openMapPopup(marker, description) {
   closeMapPopup();

   popup = new OpenLayers.Popup.AnchoredBubble("popup", marker.lonlat, null,
                                               description, marker.icon, true);
   popup.setBackgroundColor("#E3FFC5");
   popup.autoSize = true;
   map.addPopup(popup);

   return popup;
}

function closeMapPopup() {
   if (popup) {
      map.removePopup(popup);
      delete popup;
   }
}

function removeMarkerFromMap(marker){
   markers.removeMarker(marker);
}

function removeBoxFromMap(box){
   vectors.removeFeature(box);
}

function getMapCenter() {
   return map.getCenter().clone().transform(map.getProjectionObject(), epsg4326);
}

function setMapCenter(center, zoom) {
   zoom = parseInt(zoom);
   var numzoom = map.getNumZoomLevels();
   if (zoom >= numzoom) zoom = numzoom - 1;
   map.setCenter(center.clone().transform(epsg4326, map.getProjectionObject()), zoom);
}

function setMapExtent(extent) {
   map.zoomToExtent(extent.clone().transform(epsg4326, map.getProjectionObject()));
}

function getMapExtent() {
   return map.getExtent().clone().transform(map.getProjectionObject(), epsg4326);
}

function getMapZoom() {
   return map.getZoom();
}

function getEventPosition(event) {
   return map.getLonLatFromViewPortPx(event.xy).clone().transform(map.getProjectionObject(), epsg4326);
}

function getMapLayers() {
   var layerConfig = "";

   for (var layers = map.getLayersBy("isBaseLayer", true), i = 0; i < layers.length; i++) {
      layerConfig += layers[i] == map.baseLayer ? "B" : "0";
   }

   for (var layers = map.getLayersBy("isBaseLayer", false), i = 0; i < layers.length; i++) {
      layerConfig += layers[i].getVisibility() ? "T" : "F";
   }

   return layerConfig;
}

function setMapLayers(layerConfig) {
   var l = 0;

   for (var layers = map.getLayersBy("isBaseLayer", true), i = 0; i < layers.length; i++) {
      var c = layerConfig.charAt(l++);

      if (c == "B") {
         map.setBaseLayer(layers[i]);
      }
   }

   while (layerConfig.charAt(l) == "B" || layerConfig.charAt(l) == "0") {
      l++;
   }

   for (var layers = map.getLayersBy("isBaseLayer", false), i = 0; i < layers.length; i++) {
      var c = layerConfig.charAt(l++);

      if (c == "T") {
         layers[i].setVisibility(true);
      } else if(c == "F") {
         layers[i].setVisibility(false);
      }
   }
}

function scaleToZoom(scale) {
   return Math.log(360.0/(scale * 512.0)) / Math.log(2.0);
}

<html>
<head>
<title>Piote WebApp - Openstreetmap Italia</title>

<script src="/static/jquery.tools.min.js"></script>
<script>
<!--
var loader = "<div id='message'><img src='/static/ajax-loader.gif' alt='Loading data...' /></div>";
var notags = "<div id='message' class='message warning'>The selected object does not have any associated tag.</div>";
var notfound = "<div id='message' class='message error'>The selected object does not exist!</div>";
var emptyform = "<form id='tags'></form>";
var mapjs = "<script src='/static/OpenLayers.js' type='text/javascript'/><script src='/static/OpenStreetMap.js' type='text/javascript'/><script src='/static/map.js' type='text/javascript'/>";

$(function() {
    $("#upload").hide();
    $("#message").replaceWith(loader);
    $("#message").hide();
    $("#slippy").hide();
    $("#slippyscript").hide();

    $("#query").submit(function() {
        var obj = $("#object").val();
        var id = $("#id").val();

        $("#message").replaceWith(loader);
        $("#message").fadeIn("normal");
        $("#slippy").fadeOut("fast");
        $("#tags").fadeOut("fast");
        $("#upload").fadeOut("fast");

        $.getJSON("/"+obj+"/"+id, function(data) {
            $("#tags").replaceWith(emptyform);
            $("#loader").fadeOut("fast");
            var i = 0;
            var err = false;
            $.each(data, function(key, value) {
                $("#message").replaceWith("<div id='message'></div>")
                if (key == "piote_status") {
                    if (value == "notags") {
                        $("#message").replaceWith(notags);
                        $("#tags").replaceWith(emptyform);
                        $("#tags").append("<input /> <input /> <a class='addrow' href='#'>+</a> <a class='delrow' href='#'>-</a><br />")
                    } else if (value == "notfound") {
                        $("#message").replaceWith(notfound);
                    }
                    $("#upload").fadeOut("fast");
                    err = true;
                    return false;
                } else {
                    $("#tags").append("<input name='key_"+i+"' class='key' value='"+key+"'/> <input name='value_"+i+"'class='value' value='"+value+"'/> " +
                                    "<a class='addrow' onClick='addrow()'>+</a> <a class='delrow' href='#'>-</a><br />");
                    i++;
                }
            });
            $("#tags").append("<input type='hidden' name='object' value='"+obj+"'/>");
            $("#tags").append("<input type='hidden' name='id' value='"+id+"'/>");

            if (!err) {
                $("#slippy").fadeIn("normal");
                $("#slippyscript").replaceWith("<script src='/slippy/"+obj+"/"+id+"' type='text/javascript'></script><script type='text/javascript'>makemap();</script>");
                $("#upload").fadeIn("normal");
            }
        });
        return false;
    });

    $("#upload").submit(function() {
        var obj = $("#object").val();
        var id = $("#id").val();

        $.post("/put/"+obj+"/"+id, $("form").serialize(), function(data){
            alert(data);
        });
        return false;
    });

    $(".addrow").click(addrow);
});

function addrow(form) {
    alert("Foo!");
}
//-->
</script>
<style type="text/css">
.key {
    font-weight: bold;
    text-align: right;
}

.message {
    display: table-cell;
    width: 500px;
    height: 60px;
    vertical-align: middle;
}

.warning {
    border: 1px dashed;
    background-color: #00ff00;
}

.error {
    border: 1px solid;
    background-color: red;
    font-weight: bold;
}
</style>
</head>
<body>
<div align="center"><h1><u>P</u>iote <u>I</u>s an <u>O</u>SM <u>T</u>ag <u>E</u>ditor</h1>
<p>This is an attempt to provide a text-only tag editor for Openstreetmap, carried on by Openstreetmap Italy.</p>
<form id="query">
<select id="object">
<option value="node">Node</option>
<option value="way">Way</option>
<option value="relation">Relation</option>
</select>
<input type="text" id="id" />
</form>

<div id="message"></div>
<br />

<script src='/static/OpenLayers.js' type='text/javascript'/></script>

<script src='/static/OpenStreetMap.js' type='text/javascript'></script>
<script src='/static/map.js' type='text/javascript'></script>
<div id="slippy" style="width: 250px; margin: auto; text-align: right">
<div id="small_map" style="width:250px; height: 300px; border: solid 1px black"></div>
<a id="area_larger_map" href=""></a><br />
<a id="object_larger_map" href=""></a>
</div>
<div id="slippyscript"></div>

<br />
<form id="tags"></form>

<div>
<form id="upload">
<label><i>Changeset</i>: <input type="text" name="changeset"/></label><br />
<br />
<label><b>E-mail</b>: <input type="text" name="email"/></label><br />
<label><b>Password</b>: <input type="password" name="password"/></label><br />
<br />
<input type="submit" value="Upload"/>
</form>
</div>

</div>
</body>
</html>
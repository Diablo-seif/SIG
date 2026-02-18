var replaceDigits = function () {
    var map = [
        "&\#1632;", "&\#1633;", "&\#1634;", "&\#1635;", "&\#1636;",
        "&\#1637;", "&\#1638;", "&\#1639;", "&\#1640;", "&\#1641;"
    ];
    document.body.innerHTML = document.body.innerHTML.replace(/\d(?=[^<>]*(<|$))/g, function ($0) {
        return map[$0]
    });
}

var hiddenInLastPage = function () {
    var vars = {};
    var x = document.location.search.substring(1).split('&');
    for (var i in x) {
        var z = x[i].split('=', 2);
        vars[z[0]] = unescape(z[1]);
    }

    if (vars['page'] == vars['topage']) {
        var hidden_nodes = document.getElementsByClassName("hide-last-page");
        for (i = 0; i < hidden_nodes.length; i++) {
            hidden_nodes[i].style.visibility = "hidden";
        }
    }
}

function startup() {
    replaceDigits();
    hiddenInLastPage();
}

window.onload = startup;


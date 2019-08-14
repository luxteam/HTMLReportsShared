
//$.extend($.expr[':'], {
//  'containsCI': function(elem, i, match, array)
//  {
//    return (elem.textContent || elem.innerText || '').toLowerCase()
//    .indexOf((match[3] || "").toLowerCase()) >= 0;
//  }
//});

function openModalWindow(id) {
    var modal = document.getElementById(id);
    modal.style.display = "flex";

    var diffCanvas = document.getElementById('imgsDiffTable');
    var imagesTable = document.getElementById("imgsCompareTable");

    if (diffCanvas && diffCanvas.style.display == "block") {
        imagesTable.style.display = "";
        diffCanvas.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

function closeModalWindow(id) {
    document.getElementById(id).style.display = "none";
}

function increaseImgSize() {
    var step = 3.5;
    var imagesSelectorList = [['#imgsDifferenceCanvas', step * 4], ['#renderedImgPopup', step], ['#baselineImgPopup', step]];

    imagesSelectorList.forEach(function(item) {
        $(item[0]).css("width", function( index, value ) {
	        return parseInt(value, 10) + document.documentElement.clientWidth / 100 * item[1];
        });
    });
}

function reduceImgSize() {
    var step = 3.5;
    var imagesSelectorList = [['#imgsDifferenceCanvas', step * 4], ['#renderedImgPopup', step], ['#baselineImgPopup', step]];

    imagesSelectorList.forEach(function(item) {
        $(item[0]).css("width", function( index, value ) {
	        return parseInt(value, 10) - document.documentElement.clientWidth / 100 * item[1];
        });
    });
}

function infoBox(message, bgcolor = false) {
    $("#infoBox").html("<p>" + message + "</p>");
    $("#infoBox").fadeIn('slow');
    if (bgcolor) {
        $("#infoBox").css({
            "background-color": bgcolor,
            "opacity": 0.4
            });
    }

    setTimeout(function(){$("#infoBox").fadeOut('slow');} , 2000);
}

function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if(pair[0] === variable) {
            return pair[1];
        }
    }
    return(false);
}

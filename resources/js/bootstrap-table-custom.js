jQuery(document).ready( function() {
    var searchText = getQueryVariable('searchText');
    if (searchText) {
        $('.jsTableWrapper [id]').bootstrapTable('resetSearch', searchText);
    }
});

window.openFullImgSize = {
    'click img': function(e, value, row, index) {
        var renderImg = document.getElementById('renderedImgPopup');
        var baselineImg = document.getElementById('baselineImgPopup');

        renderImg.src = "";
        baselineImg.src = "";

        var src_prefixes = ["thumb64_", "thumb256_"];
        renderImg.src = row.rendered_img.split('"')[1];

        if (row.baseline_img.includes("img")) {
            baselineImg.src = row.baseline_img.split('"')[1];
        }
        for (var i in src_prefixes) {
            renderImg.src = renderImg.src.replace(src_prefixes[i], "");
            if (row.baseline_img.includes("img")) {
                baselineImg.src = baselineImg.src.replace(src_prefixes[i], "");
            }
        }

        document.getElementById("imgsCompareTable").style.display = "";
        document.getElementById("imgsDiffTable").style.display = "none";

        openModalWindow('imgsModal');
    }
}

function metaAJAX(value, row, index, field) {
    return value.replace('data-src', 'src');
}

window.copyTestCaseName = {
    'click button': function(e, value, row, index) {

        try {
            var node = document.createElement('input');
            var current_url = window.location.href;
            var url_parser = new URL(current_url);
            if (url_parser.searchParams.get("searchText")) {
                url_parser.searchParams.delete("searchText");
            }
            url_parser.searchParams.set("searchText", row.test_case);

            // duct tape for clipboard correct work
            node.setAttribute('value', url_parser.toString());
            document.body.appendChild(node);
            node.select();
            document.execCommand('copy');
            node.remove();
            // popup with status for user
            infoBox("Link copied to clipboard.")
        } catch(e) {
            infoBox("Can't copy to clipboard.")
        }
    }
}

function timeFormatter(value, row, index, field) {
    var time = new Date(null);
    time.setSeconds(value);
    return time.toISOString().substr(11, 8);
}
function renderCanvasData(baselineId, renderId, diffCanvasId, thresholdValue) {

    var diffCanvas = document.getElementById(diffCanvasId);

    var img1 = document.getElementById(baselineId);
    var img2 = document.getElementById(renderId);

    diffCanvas.width = img1.naturalWidth;
    diffCanvas.height = img1.naturalHeight;

    var ctx = diffCanvas.getContext("2d");
    ctx.clearRect(0, 0, diffCanvas.width, diffCanvas.height);

    ctx.drawImage(img1, 0, 0);
    var imgData1 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);
    ctx.drawImage(img2, 0, 0);
    var imgData2 = ctx.getImageData(0, 0, diffCanvas.width, diffCanvas.height);

    var diff = ctx.createImageData(diffCanvas.width, diffCanvas.height);
    pixelmatch(imgData1.data, imgData2.data, diff.data, diffCanvas.width, diffCanvas.height, {threshold: thresholdValue, includeAA: true});
    ctx.putImageData(diff, 0, 0);
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitImgLoadAndRenderCanvasData(baselineId, renderId, diffCanvasId, thresholdValue) {
    var loaded = false;
    var i = 0;
    while(i < 1000) {
        console.log(document.getElementById(baselineId).complete && document.getElementById(renderId).complete);
        if (document.getElementById(baselineId).complete && document.getElementById(renderId).complete) {
            console.log("Imgs loaded");
            renderCanvasData(baselineId, renderId, diffCanvasId, thresholdValue);
            return;
        }
        else {
            i++;
            await sleep(1000);
            console.log("Imgs not loaded");
        }
    }
}
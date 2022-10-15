import * as SporthDiagram from "./sporthdiagram.js";
import * as ShaderFig from "./shaderfig.js";

function initVideos(ele)
{
	var allVideoFigs = ele.querySelectorAll(".figure.video");
	allVideoFigs.forEach(function(ele) {
		var fig = {
			ele: ele,
			video: ele.querySelector("video"),
			cover: ele.querySelector("img")
		};
		fig.cover.addEventListener("click", function() {
			fig.ele.classList.add("started");
			fig.video.style.display = "block";
			fig.video.play();
		});
	});
}

window.addEventListener('load', function(){
	var figLock = {runningFig: null};
	SporthDiagram.init(document, figLock);
	ShaderFig.init(document, figLock);
	initVideos(document);
});

renderMathInElement(document.body, {delimiters: [
	{left: "$$", right: "$$", display: true},
	{left: "$", right: "$", display: false},
]});

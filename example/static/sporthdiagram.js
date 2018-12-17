import * as SporthParams from "./sporthparams.js";
import SporthAL from './sporthal.js'
var lock;

var sporth = {gotError: false};
SporthAL().then(function(mod) {
	mod.cwrap('sporthal_init', 'number')();
	sporth.compile = mod.cwrap('sporthal_compile', 'number', ['string']);
	sporth.start = mod.cwrap('sporthal_start', 'number');
	sporth.stop = mod.cwrap('sporthal_stop', 'number');
	sporth.getp = mod.cwrap('sporthal_getp', 'number', ['number']);
	sporth.setp = mod.cwrap('sporthal_setp', 'number', ['number', 'number']);
	mod["printErr"] = function(text) {
		alert(text);
		gotError = true;
	};
});

function setPlayingStyle(ele, playing)
{
	ele.querySelector(".figRun, .figStop").className = playing ? "figStop" : "figRun";
	var allRanges = ele.querySelectorAll("input[type='range']");
	allRanges.forEach(function(range) {
		range.disabled = !playing;
	});
	ele.querySelector(".figSliders").classList.toggle("off", !playing);
}

function runFig(fig)
{
	if (lock.runningFig != null) {
		stopFig(lock.runningFig);
	}
	sporth.gotError = false;
	SporthParams.setPvalues(fig.code, fig.values);
	sporth.compile(fig.code.replace(/\t/g , " "));
	if (sporth.gotError) return;
	sporth.start();
	lock.runningFig = fig;
	setPlayingStyle(fig.ele, true);
}

function stopFig(fig)
{
	sporth.stop();
	lock.runningFig = null;
	setPlayingStyle(fig.ele, false);
}

export function createAll(ele, figLock)
{
	lock = figLock;
	SporthParams.init(sporth);
	var allSporthDiagrams = ele.querySelectorAll(".sporthDiagram");
	allSporthDiagrams.forEach(function(ele) {
		var fig = {
			ele: ele,
			code: ele.querySelector(".figCode").value,
			slidersDiv: ele.querySelector(".figSliders"),
			runButton: ele.querySelector(".figRun"),
			editLink: ele.querySelector(".figEdit"),
		};
		fig.values = SporthParams.createSliders(fig.slidersDiv, fig.code);
		fig.runButton.addEventListener("click", function(e) {
			if (lock.runningFig == fig)
				stopFig(fig);
			else
				runFig(fig);
		});
		fig.editLink.href = "https://audiomasher.org/new?script="+encodeURIComponent(fig.code);
		fig.editLink.target = "_blank";
		setPlayingStyle(ele, lock.runningFig == fig);
	});
}



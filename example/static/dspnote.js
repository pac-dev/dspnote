var gotError;
var Module = {
	print: function(text) {
	},
	printErr: function(text) {
		alert(text);
		gotError = true;
	},
	onRuntimeInitialized: function () {
		cwrap('sporthal_init', 'number')();
		sporthal_compile = cwrap('sporthal_compile', 'number', ['string']);
		sporthal_start = cwrap('sporthal_start', 'number');
		sporthal_stop = cwrap('sporthal_stop', 'number');
		sporthal_getp = cwrap('sporthal_getp', 'number', ['number']);
		sporthal_setp = cwrap('sporthal_setp', 'number', ['number', 'number']);
		Module.print("ready.")
		// todo maybe: replace run button style [loading] -> [run]
	},
};

function setPlayingStyle(ele, playing)
{
	ele.querySelector(".figRun, .figStop").className = playing ? "figStop" : "figRun";
	var allRanges = ele.querySelectorAll("input[type='range']");
	allRanges.forEach(function(range) {
		range.disabled = !playing;
	});
	ele.querySelector(".figSliders").classList.toggle("off", !playing);
}

var runningFig = null;

function runFig(fig)
{
	if (runningFig != null) {
		stopFig(runningFig);
	}
	gotError = false;
	sporthParam_setPvalues(fig.code, fig.values);
	sporthal_compile(fig.code.replace(/\t/g , " "));
	if (gotError) return;
	sporthal_start();
	runningFig = fig;
	setPlayingStyle(fig.ele, true);
}

function stopFig(fig)
{
	sporthal_stop();
	runningFig = null;
	setPlayingStyle(fig.ele, false);
}

//document.addEventListener('DOMContentLoaded', function() {
window.addEventListener('load', function(){
	var allSporthDiagrams = document.querySelectorAll(".sporthDiagram");
	allSporthDiagrams.forEach(function(ele) {
		var fig = {
			ele: ele,
			code: ele.querySelector(".figCode").value,
			slidersDiv: ele.querySelector(".figSliders"),
			runButton: ele.querySelector(".figRun"),
			editLink: ele.querySelector(".figEdit"),
		};
		fig.values = sporthParam_createSliders(fig.slidersDiv, fig.code);
		fig.runButton.addEventListener("click", function(e) {
			if (runningFig == fig)
				stopFig(fig);
			else
				runFig(fig);
		});
		fig.editLink.href = "https://audiomasher.org/new?script="+encodeURIComponent(fig.code);
		fig.editLink.target = "_blank";
		setPlayingStyle(ele, runningFig == fig);
	});
});

renderMathInElement(document.body, {delimiters: [
	{left: "$$", right: "$$", display: true},
	{left: "$", right: "$", display: false},
]});

/*
MathJax.Hub.Config({
	config: ["MMLorHTML.js"],
	jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
	extensions: ["MathMenu.js", "MathZoom.js"]
});
*/


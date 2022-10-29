var lock;


var vertexCode = `
	attribute vec2 vertPos;
	varying vec2 iUV;
	void main() {
		gl_Position = vec4(vertPos, 0.0, 1.0);
		iUV = vertPos * 0.5 + 0.5;
	}
`
/*
var vertexCode = `#version 300 es
	in vec2 vertPos;
	out vec2 iUV;
	void main() {
		gl_Position = vec4(vertPos, 0.0, 1.0);
		iUV = vertPos * 0.5 + 0.5;
	}
`
*/

function compileShader(gl, code, type) {
	var shader = gl.createShader(type);
	gl.shaderSource(shader, code);
	gl.compileShader(shader);
	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		console.log(`Error compiling ${type === gl.VERTEX_SHADER ? "vertex" : "fragment"} shader:`);
		console.log(gl.getShaderInfoLog(shader));
	}
	return shader;
}

function buildShaderProgram(gl, shaderInfo) {
	var program = gl.createProgram();
	shaderInfo.forEach(function(desc) {
		var shader = compileShader(gl, desc.code, desc.type);
		if (shader) gl.attachShader(program, shader);
	});
	gl.linkProgram(program)
	if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		console.log("Error linking shader program:");
		console.log(gl.getProgramInfoLog(program));
	}
	return program;
}

function initFigGL(fig)
{
	// prevent blockiness on hi-DPI:
	fig.canvas.width = fig.canvas.offsetWidth;
	fig.canvas.height = fig.canvas.offsetHeight;
	
	var gl = fig.canvas.getContext("webgl");
	gl.getExtension('OES_standard_derivatives');
	//var gl = fig.canvas.getContext("webgl2");

	// todo check if we got the context and show error message

	var shaderInfo = [
		{type: gl.VERTEX_SHADER, code: vertexCode},
		{type: gl.FRAGMENT_SHADER, code: fig.code}
	];
	fig.shaderProgram = buildShaderProgram(gl, shaderInfo);
	var vertexArray = new Float32Array([
		-1, 1, 1, 1, 1, -1,
		-1, 1, 1, -1, -1, -1
	]);
	fig.vertexBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, fig.vertexBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, vertexArray, gl.STATIC_DRAW);
	fig.vertexCount = vertexArray.length/2;
	fig.gl = gl;
	
	fig.timeLoc = gl.getUniformLocation(fig.shaderProgram, 'iTime');
	fig.resLoc = gl.getUniformLocation(fig.shaderProgram, 'iRes');
	for (const [k, v] of Object.entries(fig.params)) {
		v.loc = gl.getUniformLocation(fig.shaderProgram, v.name);
	}
}

function renderFrame(fig)
{
	fig.canvas.width = fig.canvas.offsetWidth;
	fig.canvas.height = fig.canvas.offsetHeight;

	var gl = fig.gl;
	gl.viewport(0, 0, fig.canvas.width, fig.canvas.height);
	gl.clearColor(0.8, 0.9, 1.0, 1.0);
	gl.clear(gl.COLOR_BUFFER_BIT);
	gl.useProgram(fig.shaderProgram);
	
	gl.bindBuffer(gl.ARRAY_BUFFER, fig.vertexBuffer);
	var vertPos = gl.getAttribLocation(fig.shaderProgram, "vertPos");
	gl.enableVertexAttribArray(vertPos);
	gl.vertexAttribPointer(vertPos, 2, gl.FLOAT, false, 0, 0);
	
	gl.uniform1f(fig.timeLoc, fig.time*0.001);
	gl.uniform2f(fig.resLoc, fig.canvas.width, fig.canvas.height);
	for (const [k, v] of Object.entries(fig.params)) {
		if (v.type == "f") gl.uniform1f(v.loc, v.value);
		if (v.type == "i") gl.uniform1i(v.loc, v.value);
	}
	
	gl.drawArrays(gl.TRIANGLES, 0, fig.vertexCount);
}

function prettyParamName(s)
{
	s = s.replace(/_/g, ' ');
	s = s.replace(/\brho\b/g, 'ρ');
	s = s.replace(/\btheta\b/g, 'θ');
	s = s.replace(/\bphi\b/g, 'φ');
	return s;
}

var num = String.raw`(-?\d+(?:\.\d+)?)`;
var sliderRe = new RegExp(String.raw`^\s*uniform float ([\w]+); //dspnote param: ${num} - ${num},? ?${num}?$`, 'gm');
var dropdownRe = new RegExp(String.raw`^\s*uniform int ([\w]+); //dspnote param: ((?:[\w]+(?: \| )?)+)$`, 'gm');
function createSlider(fig, match)
{
	var param = {
		type: "f",
		name: match[1],
		min: match[2],
		max: match[3],
	};
	if (match[4] !== undefined)
		param.value = match[4];
	else
		param.value = param.min;

	fig.params[param.name] = param;
	
	var paramDiv = document.createElement("div");
	paramDiv.className = "sliderOut";
	
	var label = document.createElement("div");
	label.innerHTML = prettyParamName(param.name) + ":";
	label.className = "sliderLabel";
	paramDiv.appendChild(label);
	
	var slider = document.createElement("input");
	slider.type = "range";
	slider.min = param.min;
	slider.max = param.max;
	slider.step = (param.max - param.min) / 1000;
	slider.className = "sliderRange";
	paramDiv.appendChild(slider);
	
	var displ = document.createElement("div");
	displ.innerHTML = param.value;
	displ.className = "sliderDispl";
	paramDiv.appendChild(displ);
	
	fig.slidersDiv.appendChild(paramDiv);
	
	slider.addEventListener('input', function(event) {
		activateFig(fig);
		param.value = slider.value;
		displ.innerHTML = slider.value;
		fig.dirty = true;
	});
	
	slider.value = param.value;
}

function createDropdown(fig, match)
{
	var param = {
		type: "i",
		name: match[1],
		optionString: match[2],
		value: 0,
	};

	fig.params[param.name] = param;
	
	var paramDiv = document.createElement("div");
	paramDiv.className = "sliderOut";
	var label = document.createElement("div");
	label.innerHTML = prettyParamName(param.name) + ":";
	label.className = "sliderLabel";
	paramDiv.appendChild(label);
	var options = param.optionString.split("|").map(s => s.trim());
	var select = document.createElement("select");
	for (let [optN, optString] of Object.entries(options)) {
		var option = document.createElement("option");
		option.value = optN;
		option.innerText = optString;
		select.appendChild(option);
	}
	paramDiv.appendChild(select);
	// space filler:
	paramDiv.appendChild(document.createElement("div"));
	fig.slidersDiv.appendChild(paramDiv);
	
	select.addEventListener('change', function(event) {
		activateFig(fig);
		param.value = Number(select.value);
		fig.dirty = true;
	});
	
	select.value = param.value;
}

function createSliders(fig)
{
	fig.slidersDiv.innerHTML = '';
	// uniform int object_mode; //dspnote param: haha | huhu
	while(true) {
		var match = dropdownRe.exec(fig.code);
		if (!match) break;
		createDropdown(fig, match);
	}
	// uniform float vari; //dspnote param: 0 - 1
	while(true) {
		var match = sliderRe.exec(fig.code);
		if (!match) break;
		createSlider(fig, match);
	}
}

function isElementInViewport(el) {
    var rect = el.getBoundingClientRect();
    return (
		rect.bottom > 10 && rect.right > 10 &&
        rect.left < (window.innerWidth || document.documentElement.clientWidth)-10 &&
		rect.top < (window.innerHeight || document.documentElement.clientHeight)-10
	);
}

function animate(fig) {
	if (isElementInViewport(fig.canvas) && (lock.runningFig == fig || fig.dirty)) {
		fig.dirty = false;
		fig.time += fig.timeDiff;
		renderFrame(fig);
	}
	requestAnimationFrame(function(currentTime) {
		fig.timeDiff = (lock.runningFig == fig) ? currentTime - fig.previousTime : 0;
		fig.previousTime = currentTime;
		animate(fig);
	});
}

function runFig(fig)
{
	activateFig(fig);
	if (lock.runningFig != null) {
		stopFig(lock.runningFig);
	}
	lock.runningFig = fig;
	setPlayingStyle(fig.ele, true);
}

function stopFig(fig)
{
	lock.runningFig = null;
	setPlayingStyle(fig.ele, false);
}

function setPlayingStyle(ele, playing)
{
	ele.querySelector(".figRun, .figStop").className = playing ? "figStop" : "figRun";
}

function setFull(fig)
{
	activateFig(fig);
	var fullParent = document.getElementById("fullParent");
	fullParent.classList.toggle("fullEnabled", true);
	fullParent.prepend(fig.canvas);
	var fullOff = function() {
		fig.ele.prepend(fig.canvas);
		fullParent.classList.toggle("fullEnabled", false);
		fullParent.removeEventListener("click", fullOff);
		fig.dirty = true;
	}
	fullParent.addEventListener("click", fullOff);
	fig.dirty = true;
}

function activateFig(fig)
{
	if (fig.activated) return;
	fig.activated = true;
	var ele = fig.ele;
	var i = ele.querySelector("img");
	var c = document.createElement('canvas');
	c.attributes["data-img"] = i.attributes["src"].value;
	ele.replaceChild(c, i);
	fig.canvas = ele.querySelector("canvas");
	fig.previousTime = performance.now();
	initFigGL(fig);
	animate(fig);
}

function initFig(ele)
{
	var fig = {
		ele: ele,
		code: ele.querySelector(".figCode").value,
		slidersDiv: ele.querySelector(".figSliders"),
		runButton: ele.querySelector(".figRun"),
		fullLink: ele.querySelector(".figFull"),
		time: 0,
		timeDiff: 0,
		params: { },
		dirty: true,
		activated: false
	};
	fig.runButton.addEventListener("click", function(e) {
		if (lock.runningFig == fig)
			stopFig(fig);
		else
			runFig(fig);
	});
	fig.fullLink.addEventListener("click", function(e) {
		e.preventDefault();
		setFull(fig, true);
	});
	window.addEventListener("resize", function(e) {
		fig.dirty = true;
	});
	setPlayingStyle(ele, lock.runningFig == fig);
	createSliders(fig);
	ele.data_fig = fig;
	if (ele.querySelector("canvas")) {
		fig.activated = true;
		fig.canvas = ele.querySelector("canvas");
		fig.previousTime = performance.now();
		initFigGL(fig);
		animate(fig);
	}
}

function activateAll(ele, figLock)
{
	var article = document.getElementsByClassName('article')[0];
	var figEles = document.querySelectorAll(".shaderFig");
	article.replaceChildren(...figEles);
	for (var ele of figEles) {
		activateFig(ele.data_fig);
	}
	function* fullscreenFigs() {
		var allCanvases = document.querySelectorAll(".shaderFig canvas");
		document.documentElement.classList.add("fullScreen");
		for (var ele of allCanvases) {
			if ("data-img" in ele.attributes === false)
				continue;
			ele.classList.add("fullScreen");
			window.dispatchEvent(new Event('resize'));
			yield ele.attributes["data-img"];
			ele.classList.remove("fullScreen");
		}
		document.documentElement.classList.remove("fullScreen");
	}
	window.fullscreenFig = fullscreenFigs();
}

export function init(ele, figLock)
{
	lock = figLock;
	var allFigs = ele.querySelectorAll(".shaderFig");
	allFigs.forEach(initFig);
	window.activateAllShaderFigs = function() { activateAll(ele, figLock); };
}

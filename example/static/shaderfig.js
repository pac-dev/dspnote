var lock;

var vertexCode = `
	attribute vec2 vertPos;
	varying vec2 fragPos;
	void main() {
		gl_Position = vec4(vertPos, 0.0, 1.0);
		fragPos = vertPos;
	}
`

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

function initFig(fig)
{
	// prevent blockiness on hi-DPI:
	fig.canvas.width = fig.canvas.offsetWidth;
	fig.canvas.height = fig.canvas.offsetHeight;
	
	var gl = fig.canvas.getContext("webgl");
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
	
	fig.timeLoc = gl.getUniformLocation(fig.shaderProgram, 'time');
	fig.resLoc = gl.getUniformLocation(fig.shaderProgram, 'res');
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
		gl.uniform1f(v.loc, v.value);
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
var re = new RegExp(String.raw`^uniform float ([\w]+); //dspnote param: ${num} - ${num},? ?${num}?$`, 'gm');
function createSlider(fig, match)
{
	var param = {
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
		param.value = slider.value;
		displ.innerHTML = slider.value;
		fig.dirty = true;
	});
	
	slider.value = param.value;
}

function createSliders(fig)
{
	// uniform float vari; //dspnote param: 0 - 1
	fig.slidersDiv.innerHTML = '';
	while(true) {
		var match = re.exec(fig.code);
		if (!match) break;
		createSlider(fig, match);
	}
}

function animate(fig) {
	if (lock.runningFig == fig || fig.dirty) {
		fig.dirty = false;
		fig.time += fig.timeDiff;
		renderFrame(fig);
	}
	window.requestAnimationFrame(function(currentTime) {
		fig.timeDiff = (lock.runningFig == fig) ? currentTime - fig.previousTime : 0;
		fig.previousTime = currentTime;
		animate(fig);
	});
}

function runFig(fig)
{
	if (lock.runningFig != null) {
		stopFig(lock.runningFig);
	}
	
	//...
	
	lock.runningFig = fig;
	setPlayingStyle(fig.ele, true);
}

function stopFig(fig)
{
	//...
	
	lock.runningFig = null;
	setPlayingStyle(fig.ele, false);
}

function setPlayingStyle(ele, playing)
{
	ele.querySelector(".figRun, .figStop").className = playing ? "figStop" : "figRun";
}

export function createAll(ele, figLock)
{
	lock = figLock;
	var allFigs = ele.querySelectorAll(".shaderFig");
	allFigs.forEach(function(ele) {
		var fig = {
			ele: ele,
			code: ele.querySelector(".figCode").value,
			slidersDiv: ele.querySelector(".figSliders"),
			runButton: ele.querySelector(".figRun"),
			canvas: ele.querySelector("canvas"),
			time: 0,
			previousTime: performance.now(),
			timeDiff: 0,
			params: { },
			dirty: true
		};
		fig.runButton.addEventListener("click", function(e) {
			if (lock.runningFig == fig)
				stopFig(fig);
			else
				runFig(fig);
		});
		setPlayingStyle(ele, lock.runningFig == fig);
		createSliders(fig);
		initFig(fig);
		animate(fig);
	});
}



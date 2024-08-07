Title: DSPNote Example Note
Author: Test Man <testman@example.com>
Created: November 2018

# DSPNote Example

Content is written in [Markdown](https://daringfireball.net/projects/markdown/syntax), with some extra features. Examples of these features are given below. Note: when viewing the source file on Github, it's better to look at the [raw file](https://raw.githubusercontent.com/pac-dev/dspnote/master/example/content/exampleNote.md).


## Audio Scripts

Example of a SporthDiagram:

figure: sporthDiagram
diagram: delayLine.svg
code:
```
	_exciter_type 9 palias # 0 - 1
	_delay_length 10 palias # 1 - 10, 5 (ms)
	_feedback 11 palias # -1 - 1, 0.7
	_tik var tick _tik set
	
	# feedback scale: (tanh(x*2)*5+x)*0.171818
	_fb var _feedback get dup 2 * tanh 5 * + 0.1718 * _fb set
	
	# exciter
	0.3 noise 1000 butlp
	dup 2 metro 0 0.001 0.01 tenv * _exciter_type get cf
	
	# delay and feedback
	(_fb get) (_delay_length get 0.001 * _tik get 0.03 tport) 0.1 vdelay
```


## Math Typesetting

Math typesetting is done with [MathJax](https://www.mathjax.org/):

$$
y(n) = x(n-d) + ay(n-d)
$$

#### where:

- $y$ is a function representing the output signal, eg. $y(n)$ is the output sample at time $n$
- $x$ is a function representing the input (exciter) signal, eg. $x(n)$ the input sample at time $n$
- $n$ is the current time
- $d$ is the delay length
- $a$ is the feedback


## WebGL Shaders

Example of a ShaderFig:

figure: shaderFig
caption: Log-polar tiling in 2D. Controls perform translation before mapping. Red axis: $\rho$, green axis: $\theta$
code:
```
	precision mediump float;
	#define M_PI 3.1415926535897932384626433832795
	
	// Inputs
	varying vec2 iUV;
	uniform float iTime;
	uniform vec2 iRes;
	
	// These lines are parsed by dspnote to generate sliders
	uniform int style; //dspnote param: disk | ring
	uniform float rho_offset; //dspnote param: 0 - 1
	uniform float theta_offset; //dspnote param: 0 - 1
	
	vec2 logPolar(vec2 p) {
		p = vec2(log(length(p)), atan(p.y, p.x));
		return p;
	}
	float disk(vec2 pos, float aaSize) {
		return 1.0-smoothstep(0.3-aaSize, 0.3+aaSize, length(pos));
	}
	float ring(vec2 pos, float aaSize) {
		return 1.0-smoothstep(0.08-aaSize, 0.08+aaSize, abs(length(pos)-0.25));
	}
	vec3 logPolarPolka(vec2 p) {
		p *= 1.5;
		float aaSize = length(logPolar(p) - logPolar(p+1.0/iRes)) * 3.5;
		p = logPolar(p);
		p *= 6.0/M_PI;
		vec2 tile = p - vec2(rho_offset, theta_offset)*3.0;
		tile = fract(tile) * 2.0 - 1.0;
		float shape;
		if (style == 0) shape = disk(tile, aaSize);
		else shape = ring(tile, aaSize);
		return mix(vec3(1.0), vec3(0.4, 0.4, 0.3), shape);
	}
	void main() {
		vec2 p = iUV*2.-1.;
		p.x *= iRes.x/iRes.y;
		vec3 ret = logPolarPolka(p);
		gl_FragColor = vec4(ret, 1.0);
	}
```

The code can also be in an external GLSL file, for an example, see the source of [Log-spherical Mapping in SDF Raymarching](https://github.com/pac-dev/notes/tree/master/content).

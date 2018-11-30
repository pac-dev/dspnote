Title: DSPnote Example Note
Author: Test Man <testman@example.com>
Created: November 28, 2018

# DSPnote Example

Content is written in markdown with DSPnote extensions. The following sections describe the extensions.


## SporthDiagrams

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

Another way of representing this type of model is with a [difference equation][], which can be useful during implementation, as an intermediate step or as reference. In this case the difference equation is:

$$
y(n) = x(n-d) + ay(n-d)
$$

#### where:

- $y$ is a function representing the output signal, eg. $y(n)$ is the output sample at time $n$
- $x$ is a function representing the input (exciter) signal, eg. $x(n)$ the input sample at time $n$
- $n$ is the current time
- $d$ is the delay length
- $a$ is the feedback



[Sporth]: https://paulbatchelor.github.io/proj/sporth.html
[learn sporth]: https://audiomasher.org/learn
[difference equation]: https://en.wikipedia.org/wiki/Linear_difference_equation


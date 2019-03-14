# DSPnote: Create Notebooks with Interactive Figures

Demo articles:

- [Log-spherical Mapping in SDF Raymarching](https://www.osar.fr/notes/logspherical/)
- [Notes on Waveguide Synthesis](https://www.osar.fr/notes/waveguides/)

DSPnote is a static site generator specialized in creating notebooks with interactive figures. It's mostly implemented as an extension to [python-markdown](https://github.com/Python-Markdown/markdown). It currently supports the following types of figures:

- *SporthDiagram*: an audio processing block diagram, accompanied by a user-defined Sporth script that can be run in-browser, and parameter sliders to control the script
- *ShaderFig*: a WebGL fragment shader, with an optional "play" button and parameter sliders to control variables in the script
- *Image*: an image with a caption


## Installing and Using

For development installation, clone or extract the dspnote repository, and run this in the resulting folder:

	pip3 install -e .

This installs the tool `dspnote-gen`, which takes a single argument: a directory containing a dspnote project.

	dspnote-gen example

To create a project, copy the `example` folder and modify it.


## Prior Art

- http://jupyter.org/
- https://observablehq.com/
- https://syntopia.github.io/Polytopia/polytopes.html
- https://www.a1k0n.net/2018/11/13/fast-line-following.html

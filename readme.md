# DSPnote: Create Notebooks with Interactive Figures

DSPnote is a static site generator specialized in creating notebooks with interactive figures. It's mostly implemented as an extension to [python-markdown](https://github.com/Python-Markdown/markdown). It currently supports the following types of figures:

- *SporthDiagram*: an audio processing block diagram, accompanied by a user-defined Sporth script that can be run in-browser, and parameter sliders to control the script.


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

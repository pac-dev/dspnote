# DSPNote: Create Notebooks with Interactive Figures

Demo articles:

- [Log-spherical Mapping in SDF Raymarching](https://www.osar.fr/notes/logspherical/)
- [Notes on Waveguide Synthesis](https://www.osar.fr/notes/waveguides/)

DSPNote is a static site generator specialized in creating notebooks with interactive figures. Some features:

- *Generative audio scripts with parameters*: scripts written in [Sporth](https://paulbatchelor.github.io/proj/sporth.html) can be included directly in the text, with an optional block diagram, and run in-browser with sliders to control variables
- *WebGL shaders with parameters*: GLSL ES fragment shaders can be included, with auto-generated image fallbacks
- *Math typesetting*; *code blocks* with syntax highlighting

## Installing and Using

DSPNote requires Python 3.9 or above. The following commands should work similarly on all platforms. Clone or download the repository (master branch), and in the resulting folder, run the command:

	pip install --editable .

This installs `dspnote` along with its dependencies. The `dspnote` command can `build` or `serve` a project containing markdown pages. An example project is included to show the structure expected by DSPNote.

```bash
# Assuming "example" is the correct path the example project:
dspnote serve example # serves locally for development and testing
dspnote build example # builds according to example/config.yml
dspnote figshot example # generates shader image fallbacks (requires Selenium)
```

For a more complex project using DSPNote, see [pac-dev/notes](https://github.com/pac-dev/notes).

To create a new project, copy the `example` folder and modify it. Each Markdown file in the `content` subfolder will generate an article. Assets for each article (eg. GLSL sources, images) are in a folder of the same name alongside the Markdown file.


## Prior Art

- http://jupyter.org/
- https://observablehq.com/
- https://syntopia.github.io/Polytopia/polytopes.html
- https://www.a1k0n.net/2018/11/13/fast-line-following.html

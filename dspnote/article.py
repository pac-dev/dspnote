import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util
from html import escape

from .figure import SporthDiagram, ShaderFig, Image

log = logging.getLogger(__name__)

def renderFigureMatch(match):
	src = match.group()
	figureType = re.search( r'^figure:\s(.*?)$', src, re.M|re.S).group(1)
	if (figureType == 'sporthDiagram'):
		fig = SporthDiagram(src)
	if (figureType == 'shaderFig'):
		fig = ShaderFig(src)
	if (figureType == 'image'):
		fig = Image(src)
	return '\n' + fig.render() + '\n'

class FigurePreprocessor(Preprocessor):
	def run(self, lines):
		content = "\n".join(lines)
		content = re.sub(r'^figure:\s(.*?)\n\n', renderFigureMatch, content, 0, re.M|re.S)
		return content.split("\n")

class FigureExtension(markdown.Extension):
	def extendMarkdown(self, md, md_globals):
		md.preprocessors.register(FigurePreprocessor(self), 'figures', 100)

class Article:
	def __init__(self, config, path):
		self.srcpath = pathlib.Path(path)
		self.config = config
		self.basename = self.srcpath.stem
		self.src = self.srcpath.read_text()
		self.outDir = pathlib.Path(config["outDir"]) / self.basename
		self.outPath = self.outDir / "index.html"
	
	def generate(self):
		md = markdown.Markdown(extensions = ['meta', 'extra', FigureExtension()])
		content = md.convert(self.src)
		md.Meta["author"][0] = escape(md.Meta["author"][0])
		templateEnv = jinja2.Environment(loader = jinja2.FileSystemLoader(str(self.config["templateDir"])))
		template = templateEnv.get_template("article.jinja")
		templateData = {
			"content": content,
			"meta": {k : v[0] for k, v in  md.Meta.items()},
			"res": self.config["publicResPath"],
			"config": self.config,
		}
		self.outDir.mkdir(parents=True, exist_ok=True)
		index = codecs.open(self.outPath, 'w+', "utf-8")
		index.write(template.render(templateData))
		index.close()
		assetsDir = self.srcpath.parent / self.basename
		if assetsDir.is_dir():
			dir_util.copy_tree(str(assetsDir), str(self.outDir))

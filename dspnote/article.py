import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util

from .figure import SporthDiagram, Image

log = logging.getLogger(__name__)

def nextFigure(content):
	start = content.find('\nfigure: ')
	end = content.find('\n\n', start)
	if (start == -1 or end == -1):
		return False
	src = content[start : end]
	figureType = re.search( r'^figure:\s(.*?)$', src, re.M|re.S).group(1)
	if (figureType == 'sporthDiagram'):
		return SporthDiagram(src, start, end)
	if (figureType == 'image'):
		return Image(src, start, end)

def withRenderedFigure(content, figure):
	return content[0:figure.start] + figure.render() + content[figure.end:]

class FigurePreprocessor(Preprocessor):
	def run(self, lines):
		content = "\n".join(lines)
		while (True):
			figure = nextFigure(content)
			if (figure):
				content = withRenderedFigure(content, figure)
			else:
				break
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
		md = markdown.Markdown(extensions = ['meta', FigureExtension()])
		content = md.convert(self.src)
		templateEnv = jinja2.Environment(loader = jinja2.FileSystemLoader(str(self.config["templateDir"])))
		template = templateEnv.get_template("article.jinja")
		templateData = {
			"content": content,
			"title": md.Meta["title"][0],
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

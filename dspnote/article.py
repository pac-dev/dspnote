import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util
from html import escape
from selenium import webdriver

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
		ShaderFig.imgctr = 0
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
		self.assetsDir = self.srcpath.parent / self.basename
	
	def generate(self):
		md = markdown.Markdown(extensions = ['meta', 'extra', FigureExtension()])
		content = md.convert(self.src)
		self.numShaderFigs = ShaderFig.imgctr
		md.Meta["author"][0] = escape(md.Meta["author"][0])
		def renderFileMatch(match):
			match = match.group(1)
			return (self.assetsDir / match).read_text()
		content = re.sub(r'\(\(file:\s(.*?)\)\)', renderFileMatch, content)
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
		if self.assetsDir.is_dir():
			dir_util.copy_tree(str(self.assetsDir), str(self.outDir))
	
	def makeFigshots(self):
		if all([os.path.isfile(self.outDir / ('shaderfig_'+str(n+1)+'.png')) for n in range(self.numShaderFigs)]): return
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		browser = webdriver.Chrome(executable_path=self.config["chromeDriver"], chrome_options=options)
		browser.set_window_size(700, 445)
		browser.get('http://localhost:8033/notes/' + self.basename)
		browser.execute_script("activateAllShaderFigs()")
		while(True):
			img = browser.execute_script("return fullscreenFig.next()")
			if (img['done']): break
			browser.save_screenshot(str(self.outDir / img['value']))
		browser.quit()

import  __main__
from .figure import SporthDiagram, ShaderFig, Image, Video
import os, re, pathlib, html, codecs, logging, distutils.dir_util
import markdown, jinja2, selenium.webdriver as webdriver

log = logging.getLogger(__name__)

def renderFigureMatch(match, md):
	src = match.group()
	figureType = re.search( r'^figure:\s(.*?)$', src, re.M|re.S).group(1)
	if (figureType == 'sporthDiagram'):
		fig = SporthDiagram(src, md)
	if (figureType == 'shaderFig'):
		fig = ShaderFig(src, md)
	if (figureType == 'image'):
		fig = Image(src, md)
	if (figureType == 'video'):
		fig = Video(src, md)
	return '\n' + fig.render() + '\n'

class FigurePreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		content = "\n".join(lines)
		content = re.sub(r'^figure:\s(.*?)(code:\n```\n+(.*?)```)?(jscode:\n```\n+(.*?)```)?\n\n', lambda m: renderFigureMatch(m, self.md), content, 0, re.M|re.S)
		return content.split("\n")

class MathPreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		content = "\n".join(lines)
		content = re.sub(r'(?<!\\)(\$\$.+?\$\$)', lambda m: self.md.htmlStash.store(m.group()), content, 0, re.M|re.S)
		return content.split("\n")

class FigurePostprocesor(markdown.postprocessors.Postprocessor):
	def run(self, text):
		text = re.sub('<p>Fig-(\u0002[a-z]*?:[0-9]*?\u0003)</p>', r'\1', text)
		return text

class FigureExtension(markdown.Extension):
	def __init__(self, article):
		self.article = article
	def extendMarkdown(self, md):
		self.htmlStash = md.htmlStash
		md.preprocessors.register(MathPreprocessor(self), 'maths', 28)
		md.preprocessors.register(FigurePreprocessor(self), 'figures', 29)
		md.postprocessors.register(FigurePostprocesor(self), 'figures', 31)

class Article:
	def __init__(self, config, path):
		self.srcpath = pathlib.Path(path)
		self.config = config
		self.basename = self.srcpath.stem
		self.outDir = pathlib.Path(config["outDir"]) / self.basename
		self.outPath = self.outDir / "index.html"
		self.assetsDir = self.srcpath.parent / self.basename
		self.urlPath = config['urlPrefix'] + self.basename + '/'
	
	def render(self):
		print('rendering '+self.basename)
		md = markdown.Markdown(extensions = ['meta', 'extra', 'codehilite', 'admonition', 'toc', FigureExtension(self)])
		self.numImageFallbacks = 0
		src = self.srcpath.read_text('utf-8')
		content = md.convert(src)
		self.meta = {k : v[0] for k, v in  md.Meta.items()}
		self.meta["author"] = html.escape(self.meta["author"])
		def renderFileMatch(match):
			match = match.group(1)
			return (self.assetsDir / match).read_text()
		content = re.sub(r'\(\(file:\s(.*?)\)\)', renderFileMatch, content)
		templateEnv = jinja2.Environment(loader = jinja2.FileSystemLoader(str(self.config["templateDir"])))
		template = templateEnv.get_template("article.jinja")
		templateData = {
			"content": content,
			"meta": self.meta,
			"res": self.config["publicResPath"],
			"config": self.config,
		}
		return template.render(templateData)
	
	def generate(self):
		rendered = self.render()
		self.outDir.mkdir(parents=True, exist_ok=True)
		index = codecs.open(self.outPath, 'w+', "utf-8")
		index.write(rendered)
		index.close()
		if self.assetsDir.is_dir():
			distutils.dir_util.copy_tree(str(self.assetsDir), str(self.outDir))
	
	def makeFigshots(self):
		if all([os.path.isfile(self.outDir / ('shaderfig_'+str(n+1)+'.png')) for n in range(self.numImageFallbacks)]): return
		options = webdriver.ChromeOptions()
		options.add_argument('--headless=chrome')
		browser = webdriver.Chrome(options=options)
		browser.set_window_size(700, 445)
		browser.get('http://localhost:8033/notes/' + self.basename)
		browser.execute_script("activateAllShaderFigs()")
		while(True):
			img = browser.execute_script("return fullscreenFig.next()")
			if (img['done']): break
			browser.save_screenshot(str(self.outDir / img['value']))
		browser.quit()

import  __main__
from .figure import SporthDiagram, ShaderFig, Image
import os, re, pathlib, html, codecs, logging, distutils.dir_util
import markdown, jinja2, selenium.webdriver as webdriver

log = logging.getLogger(__name__)

def renderFigureMatch(match, article):
	src = match.group()
	figureType = re.search( r'^figure:\s(.*?)$', src, re.M|re.S).group(1)
	if (figureType == 'sporthDiagram'):
		fig = SporthDiagram(src, article)
	if (figureType == 'shaderFig'):
		fig = ShaderFig(src, article)
	if (figureType == 'image'):
		fig = Image(src, article)
	return '\n' + fig.render() + '\n'

class FigurePreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		content = "\n".join(lines)
		content = re.sub(r'^figure:\s(.*?)\n\n', lambda m: renderFigureMatch(m, self.md.article), content, 0, re.M|re.S)
		return content.split("\n")

class FigureExtension(markdown.Extension):
	def __init__(self, article):
		self.article = article
	def extendMarkdown(self, md):
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
		md = markdown.Markdown(extensions = ['meta', 'extra', 'codehilite', FigureExtension(self)])
		self.numImageFallbacks = 0
		content = md.convert(self.src)
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
		self.outDir.mkdir(parents=True, exist_ok=True)
		index = codecs.open(self.outPath, 'w+', "utf-8")
		index.write(template.render(templateData))
		index.close()
		if self.assetsDir.is_dir():
			distutils.dir_util.copy_tree(str(self.assetsDir), str(self.outDir))
	
	def makeFigshots(self):
		if all([os.path.isfile(self.outDir / ('shaderfig_'+str(n+1)+'.png')) for n in range(self.numImageFallbacks)]): return
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

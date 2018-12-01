import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util

log = logging.getLogger(__name__)

globalFigs = []

sporthDiagramTemplate = """

<div class="figure sporthDiagram">
	<textarea class="figCode">{code}</textarea>
	<div class="figDiagram"><img src="{diagram}"></div>
	<div class="figSubPanel">
		<div class="figRun"></div>
		<div class="figSliders off">
		{placeholders}
		</div>
		<a href="{url}" class="figEdit">[edit]</a>
	</div>
</div>
<div class="figCaption">
	{caption}
</div>

"""

placeholderTemplate = """
<div class="sliderOut">
	<div class="sliderLabel"> </div>
	<input type="range" class="sliderRange" disabled="">
	<div class="sliderDispl"> </div>
</div>
"""

def nextFigure(content):
	ret = { }
	ret['start'] = content.find('\nfigure: ')
	ret['end'] = content.find('\n\n', ret['start'])
	if (ret['start'] == -1 or ret['end'] == -1):
		return False
	src = content[ret['start'] : ret['end']]
	ret['figureType'] = re.search( r'^figure:\s(.*?)$', src, re.M|re.S).group(1)
	if (ret['figureType'] == "sporthDiagram"):
		ret['code'] = re.search( r'^code:\n```\n(.*?)\n```', src, re.M|re.S).group(1)
		ret['code'] = textwrap.dedent(ret['code'])
		ret['placeholders'] = placeholderTemplate * ret['code'].count('palias')
		ret['diagram'] = re.search( r'^diagram:\s(.*?)$', src, re.M|re.S).group(1)
		ret['url'] = re.search( r'(?:^url:\s(.*?)$|$)', src, re.S).group(1) or "#"
		ret['caption'] = re.search( r'(?:\ncaption:\s(.*?)\n|$)', src, re.S).group(1) or ""
	return ret

def renderFigure(figure):
	return sporthDiagramTemplate.format(**figure)

def withRenderedFigure(content, figure):
	return content[0:figure['start']] + renderFigure(figure) + content[figure['end']:]

def withStashedFigure(content, figure):
	globalFigs.append(renderFigure(figure))
	return content[0:figure['start']] + "\n\n\n<div>\n\t__STASHED__\n</div>\n\n\n" + str(len(globalFigs) - 1) + content[figure['end']:]

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

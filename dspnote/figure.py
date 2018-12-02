import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util

class SporthDiagram:
	def __init__(self, src, start, end):
		self.start = start
		self.end = end
		self.data = {
			'diagram': re.search( r'^diagram:\s(.*?)$', src, re.M|re.S).group(1),
			'url': re.search( r'(?:^url:\s(.*?)$|$)', src, re.S).group(1) or "#",
			'caption': re.search( r'(?:\ncaption:\s(.*?)\n|$)', src, re.S).group(1) or "",
			'code': re.search( r'^code:\n```\n(.*?)\n```', src, re.M|re.S).group(1),
		}
		self.data['code'] = textwrap.dedent(self.data['code'])
		self.data['placeholders'] = self.placeholder * self.data['code'].count('palias')

	def render(self):
		return self.template.format(**self.data)

	template = """

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

	placeholder = """
<div class="sliderOut">
	<div class="sliderLabel"> </div>
	<input type="range" class="sliderRange" disabled="">
	<div class="sliderDispl"> </div>
</div>
	"""


class Image:
	def __init__(self, src, start, end):
		self.start = start
		self.end = end
		self.data = {
			'image': re.search( r'^image:\s(.*?)$', src, re.M|re.S).group(1),
			'caption': re.search( r'(?:\ncaption:\s(.*?)$|$)', src, re.S).group(1) or "",
		}

	def render(self):
		return self.template.format(**self.data)

	template = """

<div class="figure image">
	<div class="figDiagram"><img src="{image}"></div>
</div>
<div class="figCaption">
	{caption}
</div>

	"""



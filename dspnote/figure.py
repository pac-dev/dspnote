import sys, os, re, pathlib, codecs, __main__, logging, markdown, jinja2, textwrap
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from string import Template
from distutils import dir_util

class SporthDiagram:
	def __init__(self, src):
		self.data = {
			'diagram': re.search( r'^diagram:\s(.*?)$', src, re.M|re.S).group(1),
			'url': re.search( r'(?:\nurl:\s(.*?)\n|$)', src, re.S).group(1) or "#",
			'caption': re.search( r'(?:\ncaption:\s(.*?)\n|$)', src, re.S).group(1) or "",
			'code': re.search( r'^code:\n```\n(.*?)\n```', src, re.M|re.S).group(1),
		}
		self.data['code'] = textwrap.dedent(self.data['code'])
		self.data['placeholders'] = self.placeholder * self.data['code'].count('palias')

	def render(self):
		return self.template.format(**self.data)

	template = """

<div class="figure runnable sporthDiagram">
	<textarea class="figCode">{code}</textarea>
	<div class="figDiagram"><img src="{diagram}"></div>
	<div class="figSubPanel">
		<div class="figRun"></div>
		<div class="figSliders off">
		{placeholders}
		</div>
		<div class="cornerControls">
			<a href="{url}" target="_blank" class="figEdit">[edit]</a>
		</div>
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

class ShaderFig:
	def __init__(self, src):
		self.data = {
			'caption': re.search( r'(?:\ncaption:\s(.*?)\n|$)', src, re.S).group(1) or "",
			'runnable': re.search( r'(?:\nrunnable:\s(.*?)\n|$)', src, re.S).group(1) or "false",
			'url': re.search( r'(?:\nurl:\s(.*?)\n|$)', src, re.S).group(1) or "#",
		}
		cmatch = re.search( r'\ncode:\n```\n(.*?)\n```', src, re.M|re.S)
		if (cmatch):
			self.data['code'] = cmatch.group(1)
		else:
			srcFile = re.search( r'\ncode:\s(.*?)\n', src).group(1)
			self.data['code'] = "((file: " + srcFile + "))"
			if (self.data['url'] == '#'):
				self.data['url'] = srcFile
		self.data['placeholders'] = self.placeholder * self.data['code'].count('dspnote param: ')
		self.data['runnableClass'] = 'runnable' if self.data['runnable']=='true' else ""

	def render(self):
		return self.template.format(**self.data)

	template = """

<div class="figure shaderFig {runnableClass}">
	<textarea class="figCode">{code}</textarea>
	<canvas>canvas</canvas>
	<div class="figSubPanel">
		<div class="figRun"></div>
		<div class="figSliders">
		{placeholders}
		</div>
		<div class="cornerControls">
			<a href="{url}" target="_blank" class="figEdit">[source]</a>
			<a href="#" class="figFull">[full]</a>
		</div>
	</div>
</div>
<div class="figCaption">
	{caption}
</div>

	"""

	placeholder = """
<div class="sliderOut">
	<div class="sliderLabel"> </div>
	<input type="range" class="sliderRange">
	<div class="sliderDispl"> </div>
</div>
	"""


class Image:
	def __init__(self, src):
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



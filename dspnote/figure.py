import __main__, re, logging

log = logging.getLogger(__name__)

def trimLines(txt: str):
	txt = txt.splitlines()
	txt = [line.strip() for line in txt]
	return '\n'.join(txt)

class Figure:
	def __init__(self):
		self.data = { }

	def render(self):
		ret = self.md.htmlStash.store(self.figTemplate.format(**self.data))
		ret += self.capTemplate.format(**self.data)
		return ret

	figTemplate = ''
	capTemplate = """

<div class="figCaption" markdown="span">
{caption}
</div>

"""

class SporthDiagram(Figure):
	def __init__(self, src, md):
		self.md = md
		self.data = {
			'diagram': re.search( r'^diagram:\s(.*?)$', src, re.M|re.S).group(1),
			'url': re.search( r'(?:\nurl:\s(.*?)\n|$)', src, re.S).group(1) or "#",
			'caption': re.search( r'(?:\ncaption:\s(.*?)\n|$)', src, re.S).group(1) or "",
			'code': re.search( r'^code:\n```\n(.*?)\n```', src, re.M|re.S).group(1),
		}
		self.data['code'] = trimLines(self.data['code'])
		self.data['placeholders'] = self.placeholder * self.data['code'].count('palias')

	figTemplate = """

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

	"""

	placeholder = """
<div class="sliderOut">
	<div class="sliderLabel"> </div>
	<input type="range" class="sliderRange" disabled="">
	<div class="sliderDispl"> </div>
</div>
	"""


class ShaderFig(Figure):
	def __init__(self, src, md):
		self.md = md
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
		# todo this obviously does not work:
		self.data['placeholders'] = self.placeholder * self.data['code'].count('dspnote param: ')
		self.data['runnableClass'] = 'runnable' if self.data['runnable']=='true' else ""
		fallback = re.search( r'(?:\nfallback:\s(.*?)\n|$)', src, re.S).group(1) or 'true'
		fallback = (fallback == 'true')
		if (fallback):
			md.article.numImageFallbacks += 1
			self.data['figElement'] = '<img src="shaderfig_' + str(md.article.numImageFallbacks) + '.png">'
		else:
			self.data['figElement'] = '<canvas>canvas</canvas>'

	figTemplate = """

<div class="figure shaderFig {runnableClass}">
	<textarea class="figCode">{code}</textarea>
	{figElement}
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

	"""

	placeholder = """
<div class="sliderOut">
	<div class="sliderLabel"> </div>
	<input type="range" class="sliderRange">
	<div class="sliderDispl"> </div>
</div>
	"""


class Image(Figure):
	def __init__(self, src, md):
		self.md = md
		self.data = {
			'image': re.search( r'^image:\s(.*?)$', src, re.M|re.S).group(1),
			'caption': re.search( r'(?:\ncaption:\s(.*?)$|$)', src, re.S).group(1) or "",
		}

	figTemplate = """

<div class="figure image">
	<div class="figDiagram"><img src="{image}"></div>
</div>

	"""


class Video(Figure):
	def __init__(self, src, md):
		self.md = md
		self.data = {
			'video': re.search( r'^video:\s(.*?)$', src, re.M|re.S).group(1),
			'poster': re.search( r'^poster:\s(.*?)$', src, re.M|re.S).group(1),
			'caption': re.search( r'(?:\ncaption:\s(.*?)$|$)', src, re.S).group(1) or "",
		}

	figTemplate = """

<div class="figure video">
	<div class="figDiagram">
		<img src="{poster}">
		<video loop allowfullscreen onclick="this.paused?this.play():this.pause()">
			<source src="{video}" type="video/mp4">
		</video>
	</div>
</div>

	"""



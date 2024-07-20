from .article import Article
from .server import RangeHandler
import os, pathlib, logging, socketserver, threading, http.server, distutils.dir_util
import yaml
from urllib.parse import urlparse

log = logging.getLogger(__name__)

class Project:
	def __init__(self, source_dir):
		self.source_dir = pathlib.Path(source_dir)
		self.config_file_path = self.source_dir / "config.yml"
		self.config = self.parseConfig()
		self.config["publicResPath"] = self.config["urlPrefix"] + "static/"
		artPaths = self.config["contentDir"].glob("*.md")
		self.arts = [Article(self.config, path) for path in artPaths]
	
	def parseConfig(self):
		configFile = open(self.config_file_path)
		config = yaml.safe_load(configFile)
		configFile.close()
		config["templateDir"] = self.source_dir / config["templateDir"]
		config["contentDir"] = self.source_dir / config["contentDir"]
		config["staticDir"] = self.source_dir / config["staticDir"]
		config["outDir"] = self.source_dir / config["outDir"]
		return config
	
	def generate(self):
		distutils.dir_util.copy_tree(
			str(self.config["staticDir"]), 
			str(self.config["outDir"] / "static")
		)
		for art in self.arts: art.export()
	
	def getServer(self):
		arts = self.arts
		config = self.config
		class NoteHandler(RangeHandler):
			def do_GET(self):
				parsed = urlparse(self.path).path.removeprefix(config['urlPrefix'])
				if (len(parsed) < 2):
					return self.serve_html('<br>'.join(
						[f'<a href="{a.urlPath}">{a.basename}</a>' for a in arts]
					))
				art = next((a for a in arts if a.basename == parsed.strip('/')), None)
				if art is not None: return self.serve_html(art.render())
				super().do_GET()
			def translate_path(self, path):
				parsed = urlparse(self.path).path.removeprefix(config['urlPrefix'])
				split = parsed.strip('/').split('/')
				ret = super().translate_path(path)
				if len(split) < 2: return ret
				if split[0] == 'static':
					ret = str(config['staticDir'].joinpath(*split[1:]))
				for art in arts:
					if split[0] == art.basename:
						ret = str(config['contentDir'].joinpath(*split))
				# print(f'translate: {path} ==> {ret}')
				return ret
			def serve_html(self, html):
				self.send_response(200)
				self.send_header('Content-type','text/html; charset=utf-8')
				self.end_headers()
				self.wfile.write(bytes(html, 'utf-8'))

		print('Please disable cache in the browser console.') # or send no-cache headers...
		print('Serving on http://localhost:8081')
		httpd = http.server.HTTPServer(('localhost', 8081), NoteHandler)
		return httpd
	
	def makeFigshots(self):
		for art in self.arts: art.render()
		httpd = self.getServer()
		thread = threading.Thread(target=httpd.serve_forever)
		thread.start()
		for art in self.arts: art.makeFigshots()
		httpd.shutdown()

	def serve(self):
		httpd = self.getServer()
		httpd.serve_forever()
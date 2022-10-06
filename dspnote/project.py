from .article import Article
import os, pathlib, logging, socketserver, threading, http.server, distutils.dir_util
import yaml

log = logging.getLogger(__name__)

class Project:
	def __init__(self, sourceDir):
		self.sourceDir = pathlib.Path(sourceDir)
		self.configFilePath = self.sourceDir / "config.yml"
		self.config = self.parseConfig()
		self.config["publicResPath"] = self.config["urlPrefix"] + "static/"
		artPaths = self.config["contentDir"].glob("*.md")
		self.arts = [Article(self.config, path) for path in artPaths]
	
	def parseConfig(self):
		configFile = open(self.configFilePath)
		config = yaml.safe_load(configFile)
		configFile.close()
		config["templateDir"] = self.sourceDir / config["templateDir"]
		config["contentDir"] = self.sourceDir / config["contentDir"]
		config["staticDir"] = self.sourceDir / config["staticDir"]
		config["outDir"] = self.sourceDir / config["outDir"]
		return config
	
	def startLocalServer(self):
		os.chdir(pathlib.Path(self.config["outDir"]).parent)
		self.httpd = socketserver.TCPServer(("", 8033), http.server.SimpleHTTPRequestHandler)
		thread = threading.Thread(target=self.httpd.serve_forever)
		thread.start()
	
	def generate(self):
		distutils.dir_util.copy_tree(
			str(self.config["staticDir"]), 
			str(self.config["outDir"] / "static")
		)
		for art in self.arts:
			art.generate()
		self.startLocalServer()
		for art in self.arts:
			art.makeFigshots()
		self.httpd.shutdown()

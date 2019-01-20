import sys, os, re, pathlib, yaml
from .article import Article
from distutils import dir_util

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
		config = yaml.load(configFile)
		configFile.close()
		config["templateDir"] = self.sourceDir / config["templateDir"]
		config["contentDir"] = self.sourceDir / config["contentDir"]
		config["staticDir"] = self.sourceDir / config["staticDir"]
		config["outDir"] = self.sourceDir / config["outDir"]
		return config
	
	def generate(self):
		dir_util.copy_tree(str(self.config["staticDir"]), str(self.config["outDir"] / "static"))
		for art in self.arts:
			art.generate()

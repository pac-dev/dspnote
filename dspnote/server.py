import os, re, urllib.parse, shutil, http.server
from http import HTTPStatus

RANGE_REGEX_PATTERN = re.compile(r'bytes=(\d*)-(\d*)$')

class RangeHandler(http.server.SimpleHTTPRequestHandler):
	""" Based on https://github.com/python/cpython/issues/86809
	"""
	def parse_range(self):
		"""Return a tuple of (start, end) representing the range header in
		the HTTP request. If the range header is missing or not resolvable,
		None is returned. This only supports single part ranges.
		"""
		range_header = self.headers.get('range')
		if not range_header:
			return None
		m = RANGE_REGEX_PATTERN.match(range_header)
		if not m:
			return None
		start = int(m.group(1)) if m.group(1) else None
		end = int(m.group(2)) if m.group(2) else None
		if start is None and end is None:
			return None
		if start is not None and end is not None and start > end:
			return None
		return start, end
	
	def send_head(self):
		"""Modified send_head to support range requests
		"""
		path = self.translate_path(self.path)
		f = None
		self.range = self.parse_range()
		if os.path.isdir(path):
			parts = urllib.parse.urlsplit(self.path)
			if not parts.path.endswith('/'):
				# redirect browser - doing basically what apache does
				self.send_response(HTTPStatus.MOVED_PERMANENTLY)
				new_parts = (parts[0], parts[1], parts[2] + '/',
							 parts[3], parts[4])
				new_url = urllib.parse.urlunsplit(new_parts)
				self.send_header("Location", new_url)
				self.end_headers()
				return None
			for index in "index.html", "index.htm":
				index = os.path.join(path, index)
				if os.path.exists(index):
					path = index
					break
			else:
				return self.list_directory(path)
		ctype = self.guess_type(path)
		if path.endswith("/"):
			self.send_error(HTTPStatus.NOT_FOUND, "File not found")
			return None
		try:
			f = open(path, 'rb')
		except OSError:
			self.send_error(HTTPStatus.NOT_FOUND, "File not found")
			return None
		try:
			fs = os.fstat(f.fileno())
			if self.range:
				start, end = self.range
				if start is None:
					# `end` here means suffix length
					start = max(0, fs.st_size - end)
					end = fs.st_size - 1
				if start >= fs.st_size:
					# 416 REQUESTED_RANGE_NOT_SATISFIABLE means that none of the range values overlap the extent of the resource
					f.close()
					self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
					return None
				if end is None or end >= fs.st_size:
					end = fs.st_size - 1
				self.send_response(HTTPStatus.PARTIAL_CONTENT)
				self.send_header("Content-Range", "bytes %s-%s/%s" % (start, end, fs.st_size))
				self.send_header("Content-Length", str(end - start + 1))

				# Update range to be sent to be used later in copyfile
				self.range = (start, end)
			else:
				self.send_response(HTTPStatus.OK)
				self.send_header("Accept-Ranges", "bytes")
				self.send_header("Content-Length", str(fs[6]))
			self.send_header("Content-type", ctype)
			self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
			self.end_headers()
			return f
		except:
			f.close()
			raise

	def copyfile(self, source, outputfile):
		"""Modified copyfile to support range requests
		"""
		if not self.range:
			shutil.copyfileobj(source, outputfile)
			return
		start, end = self.range
		length = end - start + 1
		source.seek(start)
		while True:
			if length <= 0:
				break
			buf = source.read(min(length, shutil.COPY_BUFSIZE))
			if not buf: break
			length -= len(buf)
			outputfile.write(buf)
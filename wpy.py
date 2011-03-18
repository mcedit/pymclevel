import sys,gzip

from contextlib import closing


PY_VERSION = sys.version_info[0]

def winput(param):
	if PY_VERSION >= 3:
		return input(param)
	else:
		return raw_input(param)

def wprint():
	if PY_VERSION >= 3:
		print()
	else:
		print

def wdecompress(param):
	if PY_VERSION >= 3:
		return gzip.decompress(param)
	else:
		import StringIO
		with closing(gzip.GzipFile(fileobj=StringIO.StringIO(param))) as gz:
			return gz.read();



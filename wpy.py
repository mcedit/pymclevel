import sys,gzip

from contextlib import closing


PY_VERSION = sys.version_info[0]

def winput(param):
	if PY_VERSION >= 3:
		return input(param)
	else:
		return raw_input(param)

def wprint2():
	if PY_VERSION >= 3:
		print()
	else:
		print

def wprint(param1,param2):
	if PY_VERSION >= 3:
		eval("print(param1, file=param2)")
	else:
		print >>param2, param1

def wdecompress(param):
	if PY_VERSION >= 3:
		return gzip.decompress(param)
	else:
		import StringIO
		with closing(gzip.GzipFile(fileobj=StringIO.StringIO(param))) as gz:
			return gz.read();

def unicode_type():
    if PY_VERSION >= 3:
        return str;
    else:
        return unicode;


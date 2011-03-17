#!/usr/bin/env python
import sys, os, optparse;

parser = optparse.OptionParser()
parser.add_option("-L", "--level", help="Run mclevel.py", action="store_const", const="mclevel.py", dest="py", default=False )
parser.add_option("-T", "--test", help="Run run_regression_test.py", action="store_const", const="run_regression_test.py", dest="py", default=False )

def main(argv):
	argv.pop(0);
	options, args = parser.parse_args(argv)
		
	if (sys.version_info[0] >= 3):
		dir="py3k/";
	else:
		dir="py/";
		
	py="mce.py";
	if (options.py):
		py = options.py;
	arguments=""
	
	if (py == "run_regression_test.py"):
		arguments+=" --script "+dir+"mce.py";
	
	for arg in args:
		arguments+=" "+str(arg);
		
	print(sys.executable+" "+dir+py+arguments);
	os.system(sys.executable+" "+dir+py+arguments);
	return 0;


if __name__ == '__main__':
    sys.exit(main(sys.argv));


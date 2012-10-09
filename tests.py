'''
Created on Jul 23, 2011

@author: Rio
'''

import logging

log = logging.getLogger(__name__)
warn, error, info, debug = log.warn, log.error, log.info, log.debug

# logging.basicConfig(format=u'%(levelname)s:%(message)s')
# logging.getLogger().level = logging.INFO

# from mclevel import loadWorldNumber, BoundingBox
# import errorreporting  # annotate tracebacks with call arguments

import unittest


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

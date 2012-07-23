#!/usr/bin/python
import logging
import unittest
import sys
sys.path.append("../src")

logging.basicConfig(level=logging.DEBUG)

import versions
versions.appendToSearchPath("/Users/chambers/src/versions/test/repos")

class TestRequire(unittest.TestCase):
    
    def testRequire(self):
        versions.require("foo", "1.0.0", auto_import=True)

    def testRequireSame(self):
        versions.require("foo", "1.0.0")
        versions.require("foo", "1.0.0")
            
    def testRequireCompatible(self):
        versions.require("foo", "1.0.0")
        versions.require("foo", "1.0.2")

    def testRequireIncompatible(self):
        versions.require("foo", "1.0.0")
        self.assertEquals(None, versions.require("foo", "1.2.0"))
                        
if __name__ == '__main__':	
    unittest.main(verbosity=2)
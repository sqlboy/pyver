#!/usr/bin/python
import logging
import unittest
import sys
import os

sys.path.append("../src")
import pyver


class Tests(unittest.TestCase):
    
    def setUp(self):
        self.ver = pyver.lib.PyVer()
        self.ver.overlay(os.path.dirname(__file__) + "/repos")

    def tearDown(self):
        self.ver.shutdown()

    def testUse(self):
        self.ver.use("foo", "1.0.0")
        import foo

    def testRequireNotEqual(self):
        self.ver.require("foo", "!=1.0.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.0.0")
        self.ver.use("foo", "1.1.0")

    def testRequireEqual(self):
        self.ver.require("foo", "==1.0.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.1.0")
        self.ver.use("foo", "1.0.0")

    def testRequirePartialEqual(self):
        self.ver.require("foo", ">=1")
        self.ver.use("foo", "1.0.0")

    def testRequireGreaterThan(self):
        self.ver.require("foo", ">1.1.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.0.0")
        self.ver.use("foo", "1.2.0")

    def testRequireLessThan(self):
        self.ver.require("foo", "<1.1.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.2.0")
        self.ver.use("foo", "1.0.0")

    def testRequireLessThanOrEq(self):
        self.ver.require("foo", "<=1.1.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.2.0")
        self.ver.use("foo", "1.1.0")

    def testRequireGreaterThanOrEq(self):
        self.ver.require("foo", ">=1.1.0")
        self.assertRaises(pyver.VesionMismatchException, self.ver.use, "foo", "1.0.0")
        self.ver.use("foo", "1.1.0")

if __name__ == '__main__':	
    unittest.main(verbosity=2)

"""
Copyright (c) 2012 Matt Chambers

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import os
import sys
import re
import tempfile
import atexit
import shutil
import logging

__all__ = [ "WARN",
            "ABORT",
            "require",
            "setSearchPath",
            "searchPath",
            "appendToSearchPath"]

logger = logging.getLogger("versions")

"""
Users may choose whether to warn or abort when an 
incompatible version is encountered.
"""
WARN = 0
ABORT = 1

class VesionMismatchException(Exception):
    """
    Thrown when an incompatible version is encoutered, asuming the resolve
    action is ABORT.
    """
    pass

class VersionNotFoundException(Exception):
    """
    Thrown when a version cannot be found.
    """
 
def require(module, version, resolve=WARN, auto_import=False):
    __VM.require(module, version, resolve, auto_import)
        
def setSearchPath(path):
    __VM.setSearchPath(path)

def appendToSearchPath(path):
    __VM.appendToSearchPath(path)

def searchPath():
    return __VM.searchPath()

class VersionManager(object):
    __INSTANCE = None
    
    @classmethod
    def instance(cls):
        if not cls.__INSTANCE:
            cls.__INSTANCE = VersionManager()
        return cls.__INSTANCE

    def __init__(self):
        self.__loaded = { }
        self.__repos = tempfile.mkdtemp("_versions_%d" % os.getpid())
        self.__search_paths = os.environ.get("VERSIONS_PATH", "").split(":")
        
        logger.debug("Intializing versions repostory at: %s" % self.__repos)
        sys.path.insert(0, self.__repos)
  
    def require(self, module, ver_str, resolve=WARN, auto_import=False):
        version = Version(ver_str)        
        if self.__loaded.has_key(module):
            other_ver = self.__loaded[module]["version"]
            if not version.isCompatible(other_ver):
                self.__takeResolveAction(module, version, other_ver, resolve)
            return other_ver
        else:
            for s_path in self.__search_paths:
                path = version.path(s_path, module)
                if os.path.exists(path):
                    os.symlink(path, os.path.join(self.__repos, module))
                    self.__loaded[module] = {"path": path, "version": version}
                    if auto_import:
                        __import__(module)
                    return self.__loaded[module]
            msg = "Unable to find: %s" % version.name(module)
            raise VersionNotFoundException(msg)

    def searchPath(self):
        return self.__search_paths
    
    def setSearchPath(self, paths):
        self.__search_paths = paths
        
    def appendToSearchPath(self, path):
        self.__search_paths.append(path)
    
    def remove(self):
        shutil.rmtree(self.__repos)
    
    def __takeResolveAction(self, module, version, other, resolve):
        if resolve == ABORT:
            self.__abort(module, version, other)
        else:
            self.__warn(module, version, other)
    
    def __abort(self, module, ver, other):
        msg = "Incompatible version, needs %s, already loaded %s (%s)."
        logger.critical(msg % (ver.name(module), 
                               other.name(module),
                               self.__loaded[module]["path"]))
        raise VersionMismatchException(msg)
             
    def __warn(self, module, ver, other):
         msg = "incompatible version, needs %s, already loaded %s (%s)."
         logger.warn(msg % (ver.name(module),
                            other.name(module),
                            self.__loaded[module]["path"]))

class Version(object):
    """
    A class to respresent a semantic version number.
    """
    def __init__(self, ver_str):
        self.__str = ver_str
        self.__ver = tuple([int(v) for v in ver_str.split("-", 1)[0].split(".")])
        self.__branch = None
        try:
            self.__branch = ver_str.split("-", 1)[1]
        except IndexError:
            pass

    @property
    def major(self):
        return self.__ver[0]

    @property
    def minor(self):
        return self.__ver[1]

    @property
    def trivial(self):
        return self.__ver[2]

    def isCompatible(self, other):
        return (self.major == other.major and self.minor == other.minor)
        
    def path(self, base, module):
        return os.path.join(base, module, str(self))
    
    def name(self, module):
        return "%s-%s" % (module, self)
    
    def __iter__(self):
        for v in self.__ver:
            yield v
            
    def __str__(self):
        return self.__str

# Setup the VersionManager sigleton
__VM = VersionManager.instance()
atexit.register(__VM.remove)

        
        
        
        
        
        
        
    
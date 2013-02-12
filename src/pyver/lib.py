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
import inspect

__all__ = [ "WARN",
            "ABORT",
            "VesionMismatchException",
            "VersionNotFoundException",
            "InvalidRequireString",
            "use",
            "require",
            "platform",
            "overlay"]

logger = logging.getLogger("pyver")

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
    pass

class InvalidRequireString(Exception):
    """
    Thrown when a require string is invalid.
    """
    pass

 
def use(module, version):
    """
    Use a specific version of a given module.  The module may be imported
    normally after a use statement.
    """
    _PYVER.use(module, version)

def require(module, *versions):
    """
    Requires specific versions to be imported upstream, but doesn't setup
    the module to be imported.
    """
    _PYVER.require(module, versions)

def platform(name, version):
    """
    Use the given platform and version.
    """
    _PYVER.platform(name, version)

def overlay(path):
    """
    Overlay a new repository on top of the existing search path.
    """
    _PYVER.overlay(path)

class PyVer(object):

    def __init__(self):
        
        self.__use = { }
        self.__require = { }

        self.__local = tempfile.mkdtemp("_pyver_%d" % os.getpid())
        self.__repos = filter(len, os.environ.get("PYVERPATH", "").split(":"))
        sys.path.insert(0, self.__local)

        logger.debug("Intializing pyver repostory at: %s" % self.__repos)

    def use(self, module, version):
        """
        Forces use of a specific version of a specific module.
        """
        ver = Version(version)
        self.check_requires(module, ver)
        try:
            loaded_ver = self.__use[module]
            if loaded_ver != ver:
                msg = "The module %s ver v%s was requested but v%s was already loaded."
                raise VesionMismatchException(msg % (module, version, loaded_ver))
        except KeyError:
            self.__link_module(module, ver)

    def require(self, module, *reqs):
        """
        Require all used modules fall into particular ranges of versions.
        """
        if not self.__require.has_key(module):
            self.__require[module] = []
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])        
        self.__require[module].extend((Require(r, mod.__name__) for r in reqs))

    def shutdown(self):
        shutil.rmtree(self.__local)

    def check_requires(self, module, ver):
        try:
            for req in self.__require[module]:
                if req.is_compatible(ver):
                    return
            msg = "%s-%s is not compatible with %s"
            raise VesionMismatchException(msg % (module, ver, self.__require[module]))

        except KeyError:
            # No versions are loaded yet
            return
        pass

    def overlay(self, path):
        if path.startswith("/"):
            self.__repos.insert(0, path)

    def __link_module(self, module, version):
        """
        Link a parcular module into the local repos.
        """
        for repos in self.__repos:
            path = os.path.join(repos, module, str(version))
            if os.path.exists(path):
                os.symlink(path, os.path.join(self.__local, module))
                self.__use[module] = version
                return
        msg = "Unable to find: %s-%s" % (module, version)
        raise VersionNotFoundException(msg)


class Require(object):

    Types = frozenset(["==", ">>", ">=", "<<", "<=", "!="])

    """
    A class to represent a verison requirement.
    """
    def __init__(self, reqstr, caller):
        if reqstr[0:2] not in self.Types:
            raise InvalidRequireString(reqstr)
        self.__reqstr = reqstr
        self.__op = reqstr[0:2]
        self.__version = Version(reqstr[2:])
        self.__caller = caller

    def is_compatible(self, otherVersion):
        if self.__op == "==":
            return self.__version.tuple() == otherVersion.tuple()
        elif self.__op == "!=":
            return self.__version.tuple() != otherVersion.tuple()
        elif self.__op == ">>":
            return self.__version.tuple() < otherVersion.tuple()
        elif self.__op == "<<":
            return self.__version.tuple() > otherVersion.tuple()
        elif self.__op == ">=":
            return self.__version.tuple() <= otherVersion.tuple()
        elif self.__op == "<=":
            return self.__version.tuple() >= otherVersion.tuple()
        return False

    def __repr__(self):
        return "%s (%s)" % (self.__reqstr, self.__caller)

    def __str__(self):
        return self.__reqstr

class Version(object):
    """
    A class to respresent a semantic version number.
    """
    def __init__(self, ver_str):
        self.__str = ver_str
        version = [0, 0, 0]
        for i, num in enumerate(ver_str.split(".", 2)):
            version[i] = num
        self.__ver = tuple(version)

    @property
    def major(self):
        return self.__ver[0]

    @property
    def minor(self):
        return self.__ver[1]

    @property
    def patch(self):
        return self.__ver[2]

    def tuple(self):
        return self.__ver
            
    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str

# Setup the VersionManager sigleton
_PYVER = PyVer()
atexit.register(_PYVER.shutdown)


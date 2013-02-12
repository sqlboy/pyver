import os
try:
	del os.environ["PYTHONPATH"]
except KeyError:
	pass
finally:
	del os

from lib import *
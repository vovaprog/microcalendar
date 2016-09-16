import sys
sys.path.insert(0, '/home/webuser/applications/microcalendar')

import logging, sys
logging.basicConfig(stream=sys.stderr)

from microcalendar import app as application


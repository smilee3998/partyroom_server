from partyroom_server.base import *

# Override base.py settings here
DEBUG = False
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ("utils.permissions.SafelistPermission",)

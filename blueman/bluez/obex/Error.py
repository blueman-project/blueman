from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

class Error(object):
    def __init__(self):
        pass


class Canceled(Error):
    pass


class Rejected(Error):
    pass

# coding=utf-8


class Error(object):
    def __init__(self):
        pass


class Canceled(Error):
    pass


class Rejected(Error):
    pass

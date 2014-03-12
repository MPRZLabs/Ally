#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging, os

class AllyPage(object):
    def __init__(self, Lines):
        self.logger = logging.getLogger(__name__)
        self.lines = Lines
    def fromfile(Path):
        if os.path.isfile(Path):
            return AllyPage(list(open(Path,'r')))
        else:
            self.logger.error("Supplied path does not lead to a file: %s" % Path)

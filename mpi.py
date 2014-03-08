#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  mpi.py
#  
#  Copyright 2014 Michcioperz <michcioperz@autistici.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

from string import Template

class CDNData(object):
    def __init__(self):
        self.bootstrapcss = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css"
        self.bootstrapjs = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"
        self.jqueryjs = "//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"
        self.commoncss = "css/_global.css"
class MPi(object):
    def __init__(self, sitetitle):
        self.footnotes = ""
        self.stitle = sitetitle
        self.cdn = CDNData()
    def start(self):
        return "<!DOCTYPE html><html>"
    def title(self, Title):
        self.ptitle = Title
    def header(self):
        return Template("""<head>
        <meta charset="UTF-8">
        <title>$ptitle | $stitle</title>
        <link rel="stylesheet" href="$bootstrapcss">
        <link rel="stylesheet" href="$commoncss">
        <link rel="stylesheet" href="$pagecss">
        <script src="$jqueryjs"></script>
        <script src="$bootstrapjs"></script>
        </head><body>""").substitute({'stitle':self.stitle,'commoncss':self.cdn.commoncss,'ptitle':self.ptitle,'bootstrapcss':self.cdn.bootstrapcss,'bootstrapjs':self.cdn.bootstrapjs,'jqueryjs':self.cdn.jqueryjs, 'pagecss':"css/" + self.ptitle + ".css"})
    def end(self):
        return self.footnotes + "</body></html>"

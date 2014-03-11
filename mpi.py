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
import socket, time, datetime

class CDNData(object):
    def __init__(self, Local):
        self.bootstrapcss = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css"
        self.bootstrapjs = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"
        self.jqueryjs = "//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"
        self.galleryjs = "//cdnjs.cloudflare.com/ajax/libs/jquery.colorbox/1.4.33/jquery.colorbox-min.js"
        self.gallerycss = "//cdnjs.cloudflare.com/ajax/libs/jquery.colorbox/1.4.33/example1/colorbox.min.css"
        if Local:
            self.bootstrapcss = "http:" + self.bootstrapcss
            self.bootstrapjs = "http:" + self.bootstrapjs
            self.jqueryjs = "http:" + self.jqueryjs
            self.galleryjs = "http:" + self.galleryjs
            self.gallerycss = "http:" + self.gallerycss
        self.commoncss = "css/_global.css"
        self.incassets = "assets/"
        
class MPi(object):
    def __init__(self, Path):
        self.path = Path
        f = open(Path + "/.allyconfig", "r")
        self.pages = ["index"]
        self.local = False
        self.stitle = None
        for line in f:
            if line.startswith("lokalny "):
                if line[8:len(line)-1] == "1":
                    self.local = True
            if line.startswith("strona "):
                self.pages.append(line[7:len(line)-1])
            if line.startswith("tytuł "):
                self.stitle = line[6:len(line)-1]
        self.footnotes = ""
        self.cdn = CDNData(self.local)
        self.carouselmode = False
        self.carouselelements = 0
        self.carouselid = None
        self.gallerymode = False
        self.galleryelements = 0
        self.galleryid = None
        self.galleryd = False
        self.starttime = time.time()
    def start(self):
        self.starttime = time.time()
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
        <link rel="stylesheet" href="$gallerycss">
        <script src="$jqueryjs"></script>
        <script src="$bootstrapjs"></script>
        </head><body>""").substitute({'stitle':self.stitle,'commoncss':self.cdn.commoncss,'ptitle':self.ptitle,'bootstrapcss':self.cdn.bootstrapcss,'bootstrapjs':self.cdn.bootstrapjs,'jqueryjs':self.cdn.jqueryjs, 'pagecss':"css/" + self.ptitle + ".css", 'gallerycss': self.cdn.gallerycss})
    def include(self, Title, Br=False):
        fl = open(self.path + self.cdn.incassets + Title + ".inc", "r")
        fll = ""
        for line in fl:
            fll = fll+line
            if Br:
                fll = fll+"<br />"
        return fll
    def poem(self, Title):
        fl = open(self.path + self.cdn.incassets + Title + ".poem", "r")
        fll = Template("""<div class="modal fade" id="modal_$title" tabindex="-1" role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button><h4 class="modal-title"><span class="glyphicon glyphicon-book"></span> $title</h4></div><div class="modal-body">""").substitute({'title':Title})
        for line in fl:
            fll = fll+line+"<br />"
        fll = fll+"</div></div></div></div>"
        self.footnotes = self.footnotes + fll
        return Template("""<button data-toggle="modal" data-target="#modal_$title" class="btn btn-info"><span class="glyphicon glyphicon-book"></span> $title</button>""").substitute({'title':Title});
    def end(self):
        rt = self.footnotes + "<footer>Powered by <a href=\"http://github.com/MPRZLabs/Ally\">Michcioperz's Ally language</a>. Brought to you by %s in %f seconds, compiled on %s.</footer></body></html>" % (socket.gethostname(), time.time()-self.starttime, datetime.datetime.utcnow().strftime("%c"))
        self.footnotes = ""
        return rt
    def contstart(self):
        return """<div class="container">"""
    def contend(self):
        return "</div>"
    def jumbostart(self):
        return """<div class="jumbotron">"""+self.contstart()
    def jumboend(self):
        return self.contend()+"</div>"
    def menu(self):
        mn = Template("""<nav class="navbar navbar-fixed-top navbar-default" role="navigation">
        <div class="container-fluid">
        <div class="navbar-header">
        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#menumenumenu-collapse">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span><span class="icon-bar"></span><span class="icon-bar"></span>
        </button>
        <a class="navbar-brand" href="index.html">$stitle</a>
        </div>
        <div class="collapse navbar-collapse" id="menumenumenu-collapse">
        <ul class="nav navbar-nav">""").substitute({'stitle':self.stitle})
        for page in self.pages:
            if page != "index":
                mn = mn+Template("""<li><a href="$title.html">$title</a></li>""").substitute({'title':page})
        mn = mn+"</ul></div></div></nav>"
        return mn
    def gallstart(self, Id):
        self.gallerymode = True
        self.galleryelements = 0
        self.galleryid = Id.strip()
        return """<div class="row">"""
    def gallment(self, Pic):
        self.galleryelements = self.galleryelements + 1
        return """<div class="col-xs-6 col-md-3"><a class="gallery-%s" href="%s" class="thumbnail"><img src="%s" class="img-responsive img-rounded"></a></div>"""%(self.galleryid, Pic, Pic)
    def gallend(self):
        gnd = "</div>"
        if not self.galleryd:
            self.footnotes = self.footnotes + """<script src="%s"></script>""" % self.cdn.galleryjs
        self.footnotes = self.footnotes + """<script>$(document).ready(function(){$(".gallery-%s").colorbox({rel:'%s', transition:"elastic"});});</script>""" % (self.galleryid, self.galleryid)
        self.gallerymode = False
        self.galleryelements = 0
        self.galleryid = None
        return gnd
    def caroustart(self, Id):
        self.carouselmode = True
        self.carouselelements = 0
        self.carouselid = Id.strip()
        return Template("""<div id="carousel-$cid" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">""").substitute({'cid':self.carouselid})
    def caroument(self, Pic, Imp=""):
        self.carouselelements = self.carouselelements + 1
        if Imp != "":
            Imp = """<div class="carousel-caption">"""+Imp+"</div>"
        if self.carouselelements == 1:
            return Template("""<div class="item active"><img src="$image" data-gallery>$imdes</div>""").substitute({'image':Pic,'imdes':Imp})
        else:
            return Template("""<div class="item"><img src="$image">$imdes</div>""").substitute({'image':Pic,'imdes':Imp})
    def carouend(self):
        cnd = "</div>"
#        if self.carouselelements > 1:
#            cnd =cnd+Template("""<a class="left carousel-control" href="#carousel-$cid" data-slide="prev">
#            <span class="glyphicon glyphicon-chevron-left"></span>
#            </a>
#            <a class="right carousel-control" href="#carousel-$cid" data-slide="next">
#            <span class="glyphicon glyphicon-chevron-right"></span>
#            </a>
#            <ol class="carousel-indicators">""").substitute({'cid':self.carouselid})
#            first=""" class="active" """
#            for num in range(self.carouselelements):
#                cnd=cnd+Template("""<li data-target="#carousel-$cid" data-slide-to="$nm" $ins></li>""").substitute({'cid':self.carouselid, 'nm':num,'ins':first})
#                first=""
#            cnd=cnd+"</ol>"
        cnd=cnd+"</div>"
        self.carouselmode = False
        self.carouselelements = 0
        self.carouselid = None
        return cnd

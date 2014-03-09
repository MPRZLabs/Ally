#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  ally.py
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

import sys, mpi, os, string, logging, SimpleHTTPServer, SocketServer

logging.basicConfig(level=logging.DEBUG)

def parse(f):
    ret = ""
    logging.debug("Parsing %s" % f)
    for line in open(f, "r"):
        if line.startswith("start"):
            ret=ret+m.start()
        if line.startswith("tytuł "):
            m.title(line[7:len(line)-1])
        if line.startswith("góra"):
            ret=ret+m.header()
        if line.startswith("koniec"):
            ret=ret+m.end()
        if line.startswith("import "):
            ret=ret+m.include(line[7:len(line)-1])
        if line.startswith("import! "):
            ret=ret+m.include(line[8:len(line)-1], True)
        if line.startswith("wiersz "):
            ret=ret+m.poem(line[7:len(line)-1])
        if line.startswith("środek("):
            ret=ret+m.contstart()
        if line.startswith(")środek"):
            ret=ret+m.contend()
        if line.startswith("jumbo("):
            ret=ret+m.jumbostart()
        if line.startswith(")jumbo"):
            ret=ret+m.jumboend()
        if line.startswith("menu"):
            ret=ret+m.menu()
    return ret

def printhelp():
    print "You need to specify filename as an argument"

def main():
    global m
    if len(sys.argv) < 2:
        print("Specify action")
        return 1
    if len(sys.argv) < 3:
        path = "."
    else:
        path = sys.argv[2]
    if sys.argv[1] == "build" or sys.argv[1] == "serve":
        if os.path.isdir(path):
            cfgpth = string.rstrip(path, "/") + "/" + ".allyconfig"
            if os.path.isfile(cfgpth):
                m = mpi.MPi(cfgpth)
                for page in m.pages:
                    with open(m.path[0:len(m.path)-12] + "/" + page + ".html", "w") as target:
                        target.write(parse(m.path[0:len(m.path)-12] + "/" + page + ".ally"))
            else:
                logging.error("Config file is not a file: %s" % cfgpth)
                return 3
        else:
            logging.error("Not a directory")
            return 2
    if sys.argv[1] == "serve":
        PORT = 8000
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", PORT), Handler)
        print "serving at port", PORT
        httpd.serve_forever()
if __name__ == '__main__':
    main()

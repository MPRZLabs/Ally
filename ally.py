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

import sys, mpi, os, string, logging

logging.basicConfig(level=logging.DEBUG)

def parse(f):
    logging.debug("Parsing %s" % f)
    for line in open(f, "r"):
        if line.startswith("start"):
            print(m.start())
        if line.startswith("tytuł "):
            m.title(line[7:len(line)-1])
        if line.startswith("góra"):
            print(m.header())
        if line.startswith("koniec"):
            print(m.end())
        if line.startswith("import "):
            print(m.include(line[7:len(line)-1]))
        if line.startswith("import! "):
            print(m.include(line[8:len(line)-1]), True)
        if line.startswith("wiersz "):
            print(m.poem(line[7:len(line)-1]))

def printhelp():
    print "You need to specify filename as an argument"

def main():
    global c
    if len(sys.argv) < 2:
        printhelp()
        return 1
    else:
        if os.path.isdir(sys.argv[1]):
            cfgpth = string.rstrip(sys.argv[1], os.pathsep) + os.pathsep + ".allyconfig"
            if os.path.isfile(cfgpth):
                m = mpi.MPi(cfgpth)
                for page in m.pages:
                    parse(m.path[0:len(m.path)-12] + os.pathsep + page)

if __name__ == '__main__':
    main()

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

import sys, mpi

m = mpi.MPi("Aleja Gwiazd")

def parse(f):
    for line in open(f, "r"):
        if line.startswith("start"):
            print(m.start())
        if line.startswith("tytuł "):
            tehpagetitle = line[7:len(line)-1]
            m.title(tehpagetitle)
        if line.startswith("góra"):
            print(m.header())
        if line.startswith("koniec"):
            print(m.end())
    return 0

def printhelp():
    print "You need to specify filename as an argument"

def main():
    try:
        return parse(sys.argv[1])
    except IndexError:
        printhelp()
        return 1

if __name__ == '__main__':
    main()

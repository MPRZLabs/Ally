#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging, os, argparse, sys, threading

logger = logging.getLogger("Ally")
logger.setLevel(logging.INFO)
loggerh = logging.StreamHandler()
loggerh.setLevel(logging.INFO)
loggerf = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
loggerh.setFormatter(loggerf)
logger.addHandler(loggerh)

def get_logger():
    global logger
    return logger
def get_logger_handler():
    global loggerh
    return loggerh
def gtl():
    return get_logger()
    
class AllyConfig(object):
    def __init__(self, Path):
        self.cdn = {}
        self.path = Path
        self.title = os.path.basename(Path)

class AllyPage(object):
    def __init__(self, Lines):
        self.lines = Lines
    def fromfile(Path):
        if os.path.isfile(Path):
            return AllyPage(list(open(Path,'r')))
        else:
            get_logger().error("Supplied path does not lead to a file: %s" % Path)
            
class AllySimpleServer():
    def __init__(self, Port=80):
        self.port = Port
        self.handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.TCPServer.allow_reuse_address = True
        self.httpd = SocketServer.TCPServer(("", self.port), self.handler)
        self.online = True
    def run(self):
        try:
            while self.online:
                httpd.handle_request()
        except KeyboardInterrupt:
            self.online = False
            
class AllySite(object):
    pass

class AllyInterface(object):
    def new_argp(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('path', type=str, help='path to the site directory or .allyconfig file')
        parser.add_argument('-v', '--verbose', help="increase logging level", action="store_true")
        parser.add_argument('-s', '--serve', help="launch a built-in HTTP server after compiling", action="store_true")
        parser.add_argument('--version', help="print version and exit", action="version", version='%(prog)s 2.0')
        return parser
    def serve(self, Directory):
        olddir = os.getcwdu()
        os.chdir(Directory)
        AllySimpleServer().run()
        os.chdir(olddir)
    def find_path(self, Path):
        gtl().debug("Parsing path: %s" % Path)
        dir_gotten = os.path.realpath(Path)
        if os.path.isdir(dir_gotten):
            gtl().info("Found path: %s" % dir_gotten)
            return dir_gotten
        else:
            gtl().error("Path not found: %s, even after trying it as %s" % (Path, dir_gotten))
            return None
    def find_config(self, Path):
        gtl().debug("Looking for config file in path %s" % Path)
        cfgpath = os.path.join(Path, ".allyconfig")
        if os.path.isfile(cfgpath):
            gtl().info("Config file found")
            gtl().debug("Config file path: %s" % cfgpath)
            return open(cfgpath, "r")
        else:
            gtl().warning("Config file not found. Using default config.")
            return None
    def find_files(self, Path, CalledFromInside=False):
        gtl().debug("Looking for Ally code in path %s" % Path)
        files = []
        for f in os.listdir(Path):
            if f.endswith(".ally"):
                gtl().debug("Found Ally file %s" % os.path.abspath(f))
                files.append(os.path.abspath(f))
            elif os.path.isdir(f):
                for subf in self.find_files(f, True):
                    files.append(subf)
        if not CalledFromInside:
            gtl().info("Found %i Ally files" % len(files))
        return files
    def main(self):
        args = self.new_argp().parse_args()
        if args.verbose:
            get_logger().setLevel(logging.DEBUG)
            get_logger_handler().setLevel(logging.DEBUG)
        path = self.find_path(args.path)
        if path == None:
            return 1
        else:
            cfg = self.find_config(path)
            files = self.find_files(path) 

if __name__ == '__main__':
    AllyInterface().main()

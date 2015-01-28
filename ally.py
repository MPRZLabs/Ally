#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from string import Template
import logging, os, argparse, shutil, socketserver, http.server, random, webbrowser, socket, datetime, time

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

class AllyConfigReactor(object):
    def getLineStart(self):
        return "#"
    def do(self, Config, Line):
        pass
        
class ACRPage(AllyConfigReactor):
    def getLineStart(self):
        return "strona "
    def do(self, Config, Line):
        page = Line[7:len(Line)-1]
        gtl().debug("Adding page %s to menu" % page)
        Config.menupages.append(page)

class ACRTitle(AllyConfigReactor):
    def getLineStart(self):
        return "tytuł "
    def do(self, Config, Line):
        title = Line[6:len(Line)-1]
        gtl().info("Setting site title: %s" % title)
        Config.title = title
        
class AllyConfigParser(object):
    def __init__(self):
        self.reactors = {}
        self.register(ACRPage())
        self.register(ACRTitle())
    def register(self, Reactor):
        self.reactors[Reactor.getLineStart()] = Reactor
    def parse(self, Config, Path):
        gtl().info("Parsing config file")
        for s in open(Path, "r"):
            for r in list(self.reactors.values()):
                if s.strip().startswith(r.getLineStart()):
                    r.do(Config, s)
    
class AllyPageReactor(object):
    def getLineStart(self):
        return "#"
    def render(self, Page, Line):
        return ""

#class AllyPageComponent(object):
#    def 

class APRStart(AllyPageReactor):
    def getLineStart(self):
        return "start"
    def render(self, Page, Line):
        gtl().debug("Starting file")
        return "<!DOCTYPE html><html>"

class APRTitle(AllyPageReactor):
    def getLineStart(self):
        return "tytuł "
    def render(self, Page, Line):
        gtl().debug("Defining title")
        title = Line[6:len(Line)-1]
        Page.title = title
        return ""

class APRDescription(AllyPageReactor):
    def getLineStart(self):
        return "opis "
    def render(self, Page, Line):
        gtl().debug("Defining description")
        description = Line[5:len(Line)-1].strip()
        Page.description = description
        return ""

class APRHeader(AllyPageReactor):
    def getLineStart(self):
        return "góra"
    def render(self, Page, Line):
        gtl().debug("Building header")
        try:
            Page.description
        except AttributeError:
            desctag = ""
        except IndexError:
            desctag = ""
        else:
            desctag = """<meta name="description" content="%s">"""%Page.description
            
        return Template("""<head><meta charset="UTF-8"><title>$ptitle | $stitle</title>$description
        <link rel="stylesheet" href="$bootstrapcss">
        <link rel="stylesheet" href="$sitecss">
        <link rel="stylesheet" href="$pagecss">
        <link rel="stylesheet" href="$gallerycss">
        <script src="$jqueryjs"></script>
        <script src="$bootstrapjs"></script>
        </head><body>""").substitute({'ptitle':Page.title, 'description':desctag, 'stitle':Page.site.config.title, 'bootstrapcss':Page.site.config.cdn['bootstrapcss'],'sitecss':Page.site.config.cdn['sitecss'],'pagecss':Page.css,'gallerycss':Page.site.config.cdn['gallerycss'],'bootstrapjs':Page.site.config.cdn['bootstrapjs'],'jqueryjs':Page.site.config.cdn['jqueryjs']})

class APRNavbar(AllyPageReactor):
    def getLineStart(self):
        return "menu"
    def render(self, Page, Line):
        gtl().debug("Inserting navbar template")
        mn = Template("""<nav class="navbar navbar-static-top navbar-inverse" role="navigation">
        <div class="container-fluid">
        <div class="navbar-header">
        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#menumenumenu-collapse">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span><span class="icon-bar"></span><span class="icon-bar"></span>
        </button>
        <a class="navbar-brand" href="/">$stitle</a>
        </div>
        <div class="collapse navbar-collapse" id="menumenumenu-collapse">
        <ul class="nav navbar-nav">""").substitute({'stitle':Page.site.config.title})
        for page in Page.site.config.menupages:
            if page != "index":
                gtl().debug("Adding page %s to navbar" % page)
                mn = mn+Template("""<li><a href="/$title">$title</a></li>""").substitute({'title':page})
        gtl().debug("Closing navbar")
        mn = mn+"</ul></div></div></nav>"
        return mn
        
class APRCarouselStart(AllyPageReactor):
    def getLineStart(self):
        return "karuzela( "
    def render(self, Page, Line):
        gtl().debug("Starting a carousel")
        Page.cnm = 0
        Page.cid = Line.split(" ", 1)[1].strip()
        return Template("""<div id="$cid-carousel" class="carousel slide" data-interval="2000" data-ride="carousel">
        <div class="carousel-inner">""").substitute({'cid':Page.cid})

class APRCarouselPart(AllyPageReactor):
    def getLineStart(self):
        return "element "
    def render(self, Page, Line):
        Page.cnm = Page.cnm + 1
        img = Line.split(" ")[1]
        try:
            txt = Line.split(" ")[2]
            if txt != "":
                txt = """<div class="carousel-caption">"""+Page.site.include(txt)+"</div>"
        except IndexError:
            txt = ""
        if Page.cnm == 1:
            return Template("""<div class="item active"><img src="$image" data-gallery>$imdes</div>""").substitute({'image':img,'imdes':txt})
        else:
            return Template("""<div class="item"><img src="$image">$imdes</div>""").substitute({'image':img,'imdes':txt})

class APRCarouselEnd(AllyPageReactor):
    def getLineStart(self):
        return ")karuzela"
    def render(self, Page, Line):
        gtl().debug("Closing a carousel")
        if Page.cnm > 1:
            tckrs = """<a class="left carousel-control" href="#%s-carousel" data-slide="prev"><span class="glyphicon glyphicon-chevron-left"></span></a><a class="right carousel-control" href="#%s-carousel" data-slide="next"><span class="glyphicon glyphicon-chevron-right"></span></a>""" % (Page.cid, Page.cid)
        else:
            tckrs = ""
        ttl = Page.cnm
        cntrs = ""
        while Page.cnm > 0:
            ctr = Page.cnm
            Page.cnm = Page.cnm - 1
            cntrs = """<li data-target="#%s-carousel" data-slide-to="%i"></li>"""%(Page.cid, ctr - 1)+cntrs
        if cntrs != "":
            cntrs = """<ol class="carousel-indicators">"""+cntrs+"</ol>"
        return """</div>%s%s</div>""" % (cntrs, tckrs)

class APRGalleryStart(AllyPageReactor):
    def getLineStart(self):
        return "galeria("
    def render(self, Page, Line):
        gtl().debug("Starting a gallery")
        Page.gid = Line.split(" ", 1)[1]
        return """<div class="row gallanonyme">"""

class APRGalleryPerson(AllyPageReactor):
    def getLineStart(self):
        return "osoba "
    def render(self, Page, Line):
        person = Line.split(" ",1)[1].strip()
        avatar = os.path.join(Page.site.config.cdn['cssdir'], person + "-avatar.jpg")
        Page.site.reqasset(avatar)
        return """<a href="/%s"><div class="col-xs-6 col-md-4"><div class="showcase-person"><img src="%s" class="img-responsive img-rounded"></div><h3>%s</h3></a></div>"""%(person, avatar, person)

class AllyImageReactor(object):
    def getLineStart(self):
        return "#"
    def render(self, Page, URL):
        return ""

class AIRDirect(object):
    def getLineStart(self):
        return "--"
    def render(self, Page, URL):
        return """<div class="col-xs-6 col-md-3 gallerian"><a class="gallery-%s" href="%s" class="thumbnail"><img src="%s" class="img-responsive img-rounded"></a></div>"""%(Page.gid.strip(), URL.strip(), URL.strip())

class AIRTrovebox(object):
    def getLineStart(self):
        return "tb"
    def render(self, Page, URL):
        trovepic = "http://awesomeness.openphoto.me/" + URL + "_870x870.jpg"
        trovenail = "http://awesomeness.openphoto.me/" + URL + "_960x180.jpg"
        return """<div class="col-xs-6 col-md-3 gallerian"><a class="gallery-%s" href="%s" class="thumbnail"><img src="%s" class="img-responsive img-rounded"></a></div>"""%(Page.gid.strip(), trovepic, trovenail)

class APRGalleryPart(AllyPageReactor):
    def __init__(self):
        self.reactors = {}
        self.stats = {}
        self.register(AIRDirect())
        self.register(AIRTrovebox())
    def register(self, Reactor):
        self.reactors[Reactor.getLineStart()] = Reactor
        self.stats[Reactor.getLineStart()] = 0
    def getLineStart(self):
        return "zdjęcie "
    def render(self, Page, Line):
        Rea = Line.split(" ", 2)[1]
        Pic = Line.split(" ", 2)[2]
        for r in list(self.reactors.values()):
            if Rea.strip().startswith(r.getLineStart()):
                gtl().debug("Embedding image %s with %s" % (Pic.strip(), r.__class__.__name__))
                self.stats[r.getLineStart()] = self.stats[r.getLineStart()] + 1
                return r.render(Page, Pic)        

class APRGalleryEnd(AllyPageReactor):
    def getLineStart(self):
        return ")galeria"
    def render(self, Page, Line):
        gtl().debug("Closing a gallery")
        Page.footnote("""<script>$(document).ready(function(){$(".gallery-%s").colorbox({rel:'%s', transition:"elastic"});});</script>"""%(Page.gid.strip(), Page.gid.strip()))
        return "</div>"

class APREnd(AllyPageReactor):
    def getLineStart(self):
        return "koniec"
    def render(self, Page, Line):
        return "%s<footer>Powered by <a href=\"http://github.com/MPRZLabs/Ally\">Michcioperz's Ally language</a>. Brought to you by %s in %f seconds, compiled on %s UTC.</footer></body></html>" % (Page.deployfootnotes(),socket.gethostname(), time.time()-Page.starttime, datetime.datetime.utcnow().strftime("%c"))

class APRContainerStart(AllyPageReactor):
    def getLineStart(self):
        return "środek("
    def render(self, Page, Line):
        return """<div class="container">"""

class APRContainerEnd(AllyPageReactor):
    def getLineStart(self):
        return ")środek"
    def render(self, Page, Line):
        return "</div>"

class APRJumbotronStart(AllyPageReactor):
    def getLineStart(self):
        return "jumbo("
    def render(self, Page, Line):
        return """<div class="jumbotron">"""

class APRJumbotronEnd(AllyPageReactor):
    def getLineStart(self):
        return ")jumbo"
    def render(self, Page, Line):
        return "</div>"

class APRImport(AllyPageReactor):
    def getLineStart(self):
        return "import "
    def render(self, Page, Line):
        t = Line.split(" ",1)[1]
        return Page.site.include(t)

class APRImportBr(AllyPageReactor):
    def getLineStart(self):
        return "import! "
    def render(self, Page, Line):
        t = Line.split(" ",1)[1]
        return Page.site.include(t, True)

class APRPoem(AllyPageReactor):
    def getLineStart(self):
        return "wiersz "
    def render(self, Page, Line):
        t = Line.split(" ",1)[1]
        fl = open(os.path.join(Page.site.config.path, Page.site.config.cdn['cssdir'], t.strip() + ".poem"), "r")
        fll = Template("""<div class="modal fade" id="modal_$title" tabindex="-1" role="dialog"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button><h4 class="modal-title"><span class="glyphicon glyphicon-book"></span> $title</h4></div><div class="modal-body">""").substitute({'title':t})
        for line in fl:
            fll = fll+line+"<br />"
        fll = fll+"</div></div></div></div>"
        Page.footnote(fll)
        return Template("""<button data-toggle="modal" data-target="#modal_$title" class="btn btn-info"><span class="glyphicon glyphicon-book"></span> $title</button>""").substitute({'title':t});

class APRHTML(AllyPageReactor):
    def getLineStart(self):
        return "o_O "
    def render(self, Page, Line):
        return Line.split(" ",1)[1]

class APRRequire(AllyPageReactor):
    def getLineStart(self):
        return "potrzebuję "
    def render(self, Page, Line):
        Page.site.reqasset(os.path.join(Page.site.config.cdn['cssdir'], Line.split(" ",1)[1].strip()))
        return ""

class AllyVideoReactor(object):
    def getLineStart(self):
        return "#"
    def render(self, URL):
        return ""

class AVRYouTube(AllyVideoReactor):
    def getLineStart(self):
        return "yt"
    def render(self, URL):
        return """<iframe class="youtube-player" type="text/html" width="640" height="385" src="//www.youtube.com/embed/%s" allowfullscreen frameborder="0"></iframe>""" % URL

class AVRPopcorn(AllyVideoReactor):
    def getLineStart(self):
        return "popcorn"
    def render(self, URL):
        return """<iframe type="text/html" width="640" height="385" src="//popcorn.webmadecontent.org/%s_" allowfullscreen frameborder="0"></iframe>""" % URL

class AVRIframe(AllyVideoReactor):
    def getLineStart(self):
        return "iframe"
    def render(self, URL):
        return """<iframe type="text/html" width="640" height="385" src="//%s" allowfullscreen frameborder="0"></iframe>""" % URL

class APRVideo(AllyPageReactor):
    def __init__(self):
        self.reactors = {}
        self.stats = {}
        self.register(AVRYouTube())
        self.register(AVRPopcorn())
        self.register(AVRIframe())
    def register(self, Reactor):
        self.reactors[Reactor.getLineStart()] = Reactor
        self.stats[Reactor.getLineStart()] = 0
    def getLineStart(self):
        return "wideo "
    def render(self, Page, Line):
        t = Line.split(" ",2)[1]
        v = Line.split(" ",2)[2]
        for r in list(self.reactors.values()):
            if t.strip().startswith(r.getLineStart()):
                gtl().debug("Embedding video %s with %s" % (v.strip(), r.__class__.__name__))
                self.stats[r.getLineStart()] = self.stats[r.getLineStart()] + 1
                return r.render(v)

class AllyPageParser(object):
    def __init__(self):
        self.reactors = {}
        self.validators = []
        self.stats = {}
        self.register_reactor(APRStart())
        self.register_reactor(APRTitle())
        self.register_reactor(APRDescription())
        self.register_reactor(APRHeader())
        self.register_reactor(APRNavbar())
        self.register_reactor(APRCarouselStart())
        self.register_reactor(APRCarouselPart())
        self.register_reactor(APRCarouselEnd())
        self.register_reactor(APRGalleryStart())
        self.register_reactor(APRGalleryPart())
        self.register_reactor(APRGalleryEnd())
        self.register_reactor(APRContainerStart())
        self.register_reactor(APRContainerEnd())
        self.register_reactor(APRJumbotronStart())
        self.register_reactor(APRJumbotronEnd())
        self.register_reactor(APRImport())
        self.register_reactor(APRImportBr())
        self.register_reactor(APRPoem())
        self.register_reactor(APRHTML())
        self.register_reactor(APRRequire())
        self.register_reactor(APRGalleryPerson())
        self.register_reactor(APREnd())
        self.register_reactor(APRVideo())
        self.register_validator(APVStartEnd())
        self.register_validator(APVContainer())
        self.register_validator(APVJumbotron())
        self.register_validator(APVGallery())
        self.register_validator(APVCarousel())
    def register_reactor(self, Reactor):
        self.reactors[Reactor.getLineStart()] = Reactor
        self.stats[Reactor.getLineStart()] = 0
    def register_validator(self, Validator):
        self.validators.append(Validator)
    def parse(self, Page, Path):
        gtl().info("Parsing page %s" % Path)
        Page.starttime = time.time()
        for s in open(Path, "r"):
            for r in list(self.reactors.values()):
                if s.strip().startswith(r.getLineStart()):
                    gtl().debug("Parsing %s with %s" % (s.strip(), r.__class__.__name__))
                    self.stats[r.getLineStart()] = self.stats[r.getLineStart()] + 1
                    Page.stuff.append(r.render(Page, s.strip()))
        for v in self.validators:
            if v.validate(self):
                gtl().debug("Page %s validated successfully with %s" % (Path, v))
            else:
                gtl().error("Error validating page %s with validator %s" % (Path, v))

class AllyPageValidator(object):
    def startAPR(self):
        return None
    def endAPR(self):
        return None
    def validate(self, APP):
        return APP.stats[self.startAPR().getLineStart()] == APP.stats[self.endAPR().getLineStart()]

class APVStartEnd(AllyPageValidator):
    def startAPR(self):
        return APRStart()
    def endAPR(self):
        return APREnd()

class APVContainer(AllyPageValidator):
    def startAPR(self):
        return APRContainerStart()
    def endAPR(self):
        return APRContainerEnd()

class APVJumbotron(AllyPageValidator):
    def startAPR(self):
        return APRJumbotronStart()
    def endAPR(self):
        return APRJumbotronEnd()

class APVGallery(AllyPageValidator):
    def startAPR(self):
        return APRGalleryStart()
    def endAPR(self):
        return APRGalleryEnd()

class APVCarousel(AllyPageValidator):
    def startAPR(self):
        return APRCarouselStart()
    def endAPR(self):
        return APRCarouselEnd()
class AllyConfig(object):
    def __init__(self, Path):
        self.cdn = {}
        self.cdn['bootstrapcss'] = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css"
        self.cdn['bootstrapjs'] = "//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"
        self.cdn['jqueryjs'] = "//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"
        self.cdn['galleryjs'] = "//cdnjs.cloudflare.com/ajax/libs/jquery.colorbox/1.4.33/jquery.colorbox-min.js"
        self.cdn['gallerycss'] = "//cdnjs.cloudflare.com/ajax/libs/jquery.colorbox/1.4.33/example1/colorbox.min.css"
        self.cdn['cssdir'] = "assets"
        self.cdn['sitecss'] = os.path.join("/","assets", "_global.css")
        self.path = Path
        self.title = os.path.basename(Path)
        self.menupages = []
    def loadfromfile(self, Path):
        if os.path.isfile(Path):
            AllyConfigParser().parse(self, Path)

class AllyPage(object):
    def __init__(self, Path, Site):
        self.path = Path
        self.site = Site
        self.reltoroot = os.path.relpath(Path, Site.config.path)
        self.title = os.path.basename(Path)[0:len(os.path.basename(Path))-5]
        self.stuff = []
        self.css = os.path.join(self.site.config.cdn['cssdir'], self.title+".css")
        self.site.reqasset(self.css)
        self.cfirst = False
        self.footnotes = ""
        self.footnote("""<script src="%s"></script>""" % self.site.config.cdn['galleryjs'])
    def footnote(self, ish):
        self.footnotes = self.footnotes + ish
    def deployfootnotes(self):
        ftn = self.footnotes
        self.footnotes = ""
        return ftn
    def link(self):
        gtl().debug("Linking page content up")
        result = ""
        for f in self.stuff:
            result=result+f
        return result

class AllySimpleServer():
    def __init__(self, Port=random.randint(8000,9000)):
        self.port = Port
        self.handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", self.port), self.handler)
        self.online = True
        address = "http://127.0.0.1:%i/"%self.port
        gtl().info("NOW ONLINE AT %s" % address)
        webbrowser.open(address)
    def run(self):
        try:
            while self.online:
                self.httpd.handle_request()
        except KeyboardInterrupt:
            self.online = False
            
class AllySite(object):
    def __init__(self, Config, Files):
        self.config = Config
        self.files = Files
        self.assets = []
        self.reqasset(os.path.join(self.config.cdn['cssdir'],"_global.css"))
    def include(self, Title, Br=False):
        fl = open(os.path.join(self.config.path, self.config.cdn['cssdir'], Title.strip() + ".inc"), "r")
        fll = ""
        for line in fl:
            fll = fll+line
            if Br:
                fll = fll+"<br />"
        return fll
    def reqasset(self, Path):
        gtl().debug("Adding %s to requested assets" % Path)
        self.assets.append(Path)
    def render(self):
        if os.path.isdir(os.path.join(self.config.path, "_site")):
            gtl().debug("Removing old _site dir")
            shutil.rmtree(os.path.join(self.config.path, "_site"))
        gtl().debug("Making _site dir")
        os.mkdir(os.path.join(self.config.path, "_site"))
        gtl().debug("Making assets dir")
        os.mkdir(os.path.join(self.config.path, "_site", self.config.cdn['cssdir']))
        for f in self.files:
            parser = AllyPageParser()
            gtl().info("Building page %s" % f)
            p = AllyPage(f, self)
            parser.parse(p, f)
            gtl().info("Saving page %s" % f)
            pth = os.path.basename(p.path)[0:len(os.path.basename(p.path))-5]
            fl = None
            if pth != "index":
                os.mkdir(os.path.join(self.config.path, "_site", pth))
                fl = open(os.path.join(self.config.path, "_site", pth ,"index.html"), "w")
                fl.write(p.link())
                fl.close()
                os.mkdir(os.path.join(self.config.path, "_site", pth + ".html"))
                fl = open(os.path.join(self.config.path, "_site", pth + ".html" ,"index.html"), "w")
                fl.write(p.link())
                fl.close()
            else:
                fl = open(os.path.join(self.config.path, "_site", "index.html"), "w")
                fl.write(p.link())
                fl.close()
        for a in self.assets:
            gtl().debug("Copying file %s" % a)
            shutil.copy(a, os.path.join(self.config.path, "_site", self.config.cdn['cssdir']))
        gtl().info("Done.")
            

class AllyInterface(object):
    def new_argp(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('path', type=str, help='path to the site directory or .allyconfig file')
        parser.add_argument('-v', '--verbose', help="increase logging level", action="store_true")
        parser.add_argument('-s', '--serve', help="launch a built-in HTTP server after compiling", action="store_true")
        parser.add_argument('--version', help="print version and exit", action="version", version='%(prog)s 2.0')
        return parser
    def serve(self, Directory):
        olddir = os.getcwd()
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
            return cfgpath
        else:
            gtl().warning("Config file not found. Using default config.")
            return None
    def find_files(self, Path, CalledFromInside=False):
        gtl().debug("Looking for Ally code in path %s" % Path)
        files = []
        for f in os.listdir(Path):
            if f.endswith(".ally"):
                gtl().debug("Found Ally file %s" % os.path.abspath(os.path.join(Path,f)))
                files.append(os.path.abspath(os.path.join(Path,f)))
            elif os.path.isdir(f):
                for subf in self.find_files(f, True):
                    files.append(os.path.join(f,subf))
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
            config = AllyConfig(path)
            if cfg != None:
                config.loadfromfile(cfg)
            files = self.find_files(path)
            site = AllySite(config, files)
            site.render()
            if args.serve:
                self.serve(os.path.join(site.config.path, "_site"))
if __name__ == '__main__':
    AllyInterface().main()

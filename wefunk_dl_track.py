#!/usr/bin/python

import sys
from HTMLParser import HTMLParser
import urllib2
import urlparse
import argparse
import logging


__version__ = '0.6'
__author__ = 'Sam'

class FunkError( Exception ): pass

def geturl(url):
    # Get a file-like object for the Python Web site's home page.
    f = urllib2.urlopen(url)
    # Read from the object, storing the page's contents in 's'.
    s = f.read()
    f.close()
    return s

def download_media(url, save_as = False):
    media_info = dict()
    file_name = url.split('/')[-1]
    if not save_as:
        save_as = file_name
    u = urllib2.urlopen(url)
    f = open(save_as, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()

    media_info['size']    = file_size
    media_info['url']     = url
    media_info['save_as'] = save_as
    media_info['http']    = u.getcode()
    return media_info

class TrackList(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.playlist = False
        self.track_id = track_id

    def handle_starttag(self, tag, attrs):
        if tag == 'ul':
            if 'id' in dict(attrs) and dict(attrs)['id'] == 'playlist':
                self.playlist = True
        if self.playlist and tag == 'a':
            if 'href' in dict(attrs):
                link = dict(attrs)['href']
                if link.startswith('/explore'):
                    self.links.append(link)

class TrackData(HTMLParser):
    data = dict()
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            if 'property' in dict(attrs) and 'content' in dict(attrs):
                self.data[dict(attrs)['property']] = dict(attrs)['content']


def track_id(url):
    return url[url.rindex("/")+1:]

def wefunk_track_info(url):

    # step 0: get current host
    o = urlparse.urlsplit(url)
    host = o[0] + '://' + o[1]

    # step 0: get the track code (last 2 chars)
    track_code = url[-2:]

    # step 1: get trackinfo list
    html = geturl(url)
    parser = TrackList()
    parser.feed(html)
    trackinfo_links = parser.links

    # find our trackinfo page
    trackinfo_link = None
    for link in parser.links:
        if link.endswith(track_code):
            trackinfo_link = link

    if not trackinfo_link:
        raise FunkError("Page %s is not good" % (url))
        #print >> sys.stderr, "Can't find the track %s on page %s." % (track_code, url)

    # prepend host if link without host
    l = urlparse.urlsplit(trackinfo_link)
    if not l[0]:
        trackinfo_link = urlparse.urljoin(host, trackinfo_link)

    # step 2: get file link from track info page
    html = geturl(trackinfo_link)

    # step 3: download and parse the html file
    parser = TrackData()
    parser.feed(html)

    # step 4: return parser.data

    track = {
        'url'   : parser.data['og:audio'],
        'title' : parser.data['og:audio:title'],
        'artist': parser.data['og:audio:artist']
    }

    return track


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_arguments():
    """Try to parse the command line arguments given by the user"""
    global __author__
    global __version__

    version_string = "%(prog)s version %(version)s by %(author)s" % \
                     {"prog": "%(prog)s", "version": __version__, \
                     "author": __author__}


    parser = MyParser(
        description='Download a track on the WeFunk website: \
        The best webradio you could ever find on the Internet.',
        epilog='Website: https://github.com/samyboy/wefunk_dl_track'
    )

    parser.add_argument('-v', '--verbose', action='append_const', const=1,
                        help='Verbose mode. -vv enables debug.')
    parser.add_argument('-V', '--version', action='version',
                        help="shows program version", version=version_string)
    parser.add_argument('url', nargs=1, help='The track\'s URL')
    parser.add_argument('--original', '--keep-name', '-o', help='Use original filename',action='store_true')

    return parser.parse_args()

def save_name(keep_name, track):
    if keep_name:
        return None
    url=track['url']
    extension = url[url.rindex("."):]
    return track['artist'] + " - " + track['title'] + extension

def create_logger(verbose_level):
    """ http://inventwithpython.com/blog/2012/04/06/stop-using-print-for-debugging-a-5-minute-quickstart-guide-to-pythons-logging-module/
    """
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    logger = logging.getLogger()
    if verbose_level > 1:
        #logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.setLevel(logging.DEBUG)
    if verbose_level == 1:
        logger.setLevel(logging.INFO)
    return logger


if __name__=="__main__":

    args = parse_arguments()

    url = args.url[0]
    keep_name = args.original

    # manage verbose stuff
    verbose_level = 0 if args.verbose is None else sum(args.verbose)
    logger = create_logger(verbose_level)

    # main program
    try:
        track_info = wefunk_track_info(url)
        filename = save_name(keep_name, track_info)
        download_result = download_media(track_info['url'], filename)
    except FunkError as e:
        print >> sys.stderr, "Error: %s" % e
        sys.exit(1)
    print "Saved as", download_result['save_as']
    sys.exit()

### EOF ###

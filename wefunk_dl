#!/usr/bin/python

import sys
import re
from HTMLParser import HTMLParser
import urllib2
import urlparse
import argparse
import logging


__version__ = '0.6'
__author__ = 'Sam'

class FunkError( Exception ): pass

def geturl(url):
    logger.debug('HTTP GET {}'.format(url))
    # Get a file-like object for the Python Web site's home page.
    f = urllib2.urlopen(url)
    # Read from the object, storing the page's contents in 's'.
    s = f.read()
    info = f.info()
    code = f.getcode()
    f.close()
    print info
    logger.debug('Return code: {}'.format(code))
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






class ShowParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.show_name = None


    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            if 'href' in dict(attrs):
                link = dict(attrs)['href']
                if link.startswith('/playlaunch/WeFunk_Show'):
                    self.show_name = link.replace('/playlaunch/', '')


class WeFunkShow():

    def __init__(self, show_id):
        logger.debug("Creating new WeFunk show number {}".format(show_id))
        self.name = None
        self.url = 'http://www.wefunkradio.com/show/{}'.format(show_id)
        self.show_id = show_id
        self.fetch_data()

    def fetch_data(self):
        logger.debug('Getting URL {}'.format(self.url))
        html = geturl(self.url)
        parser = ShowParser()
        parser.feed(html)
        self.filename = parser.show_name + '.mp3'


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
    parser.add_argument('plid', nargs=1, help='The track or show ID')
    parser.add_argument('--original', '--keep-name', '-o', help='Use original filename',action='store_true')

    return parser.parse_args()


def create_logger(verbose_level):
    """ http://inventwithpython.com/blog/2012/04/06/stop-using-print-for-debugging-a-5-minute-quickstart-guide-to-pythons-logging-module/
    """
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    logger = logging.getLogger()
    if verbose_level > 1:
        logger.setLevel(logging.DEBUG)
    if verbose_level == 1:
        logger.setLevel(logging.INFO)
    return logger

if __name__=="__main__":

    args = parse_arguments()

    keep_name = args.original

    # manage verbose stuff
    verbose_level = 0 if args.verbose is None else sum(args.verbose)
    logger = create_logger(verbose_level)

    # main program
    logger.debug("wanted data: {}".format(args.plid))
    plid = args.plid[0]

    if '_' in plid:
        show_id = plid.split("_")[0]
        track_number = plid.split("_")[1]
        logger.debug('Trying to find track {} of show {}'.format(track_number, show_id))
        track = WeFunkTrack(plid)
        print track.__dict__
    else:
        show_id = plid
        logger.debug('Trying to download entire show {}'.format(show_id))
        show = WeFunkShow(show_id)
        logger.debug('show file name is {}'. format(show.filename ))

    shows_location = 'http://wefunk.xcrit.com/partial.php?file='
    media_location = shows_location + show.filename
    try:
        download_result = download_media(media_location, show.filename)
    except FunkError as e:
        print >> sys.stderr, "Error: %s" % e
        sys.exit(1)
    print "Saved as", download_result['save_as']
    sys.exit()

### EOF ###

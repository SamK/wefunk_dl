#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Download a WeFunk show
"""

import sys
from html.parser import HTMLParser
import urllib.request
import argparse
import logging


__version__ = '2.0.0'
__author__ = ['Sam']


class FunkError(Exception):
    """ This error happens when the FUNK makes an error
    """
    pass


def geturl(url):
    """ Return the content of a url
    """
    LOG.debug('HTTP GET %s', url)
    # Get a file-like object for the Python Web site's home page.
    with urllib.request.urlopen(url) as http_connection:
        # Read from the object, storing the page's contents in 's'.
        url_content = http_connection.read()
        return_code = http_connection.getcode()
    LOG.debug('Return code: %s', return_code)
    return url_content


def download_media(url, save_as=None):
    """ Download a big file from the "url" and save it as "save_as".
        If "save_as" is not provided, save as the original file.
    """
    media_info = dict()
    file_name = url.split('/')[-1]
    if not save_as:
        save_as = file_name
    print(f"Downloading from: {url}")
    with urllib.request.urlopen(url) as http_connection:
        with open(save_as, 'wb') as fhandler:
            meta = http_connection.info()
            file_size = int(meta.get("Content-Length"))

            block_sz = 8192
            LOG.debug('Starting download of "%s".', url)
            while True:
                buffer_chunk = http_connection.read(block_sz)
                if not buffer_chunk:
                    break
                fhandler.write(buffer_chunk)

    media_info['size'] = file_size
    media_info['url'] = url
    media_info['save_as'] = save_as
    media_info['http'] = http_connection.getcode()
    return media_info


class ShowParser(HTMLParser):  # pylint: disable=R0904
    """ HTML parser for a WeFunk show
    """

    def __init__(self):
        super().__init__()
        self.show_name = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            if 'href' in attrs_dict:
                link = attrs_dict['href']
                if link.lower().startswith('/playlaunch/wefunk_show'):
                    self.show_name = link.replace('/playlaunch/', '')


class WeFunkShow(object):  # pylint: disable=R0903
    """ This is a WeFunk show
    """

    website = 'http://www.wefunkradio.com'
    shows_storage = 'http://wefunk.xcrit.com/'

    def __init__(self, show_id):
        LOG.debug('Creating new WeFunk show number %s', show_id)
        self.name = None
        self.location = None
        self.filename = ''
        self.show_id = show_id
        self.url = f'{self.website}/show/{show_id}'
        self.fetch_data()

    def fetch_data(self):
        """ Get the available informations from the show on the wefunk website
        """
        LOG.debug('Getting html info from %s', self.url)
        html = geturl(self.url).decode('utf-8')
        parser = ShowParser()
        parser.feed(html)
        if parser.show_name is None:
            # The show does not seem to exist or something went wrong.
            # GTFO of here.
            raise FunkError(f'Cannot find show "{self.show_id}".')
        self.filename = parser.show_name + '.mp3'
        self.location = f'{self.shows_storage}{self.filename}'


class MyParser(argparse.ArgumentParser):
    """ Extend argparse: I want an "error()" method that writes the help message
    """

    def error(self, message):
        sys.stderr.write(f'error: {message}\n')
        self.print_help()
        sys.exit(2)


def parse_arguments():
    """Try to parse the command line arguments given by the user"""

    version_string = f"%(prog)s version {__version__} by {__author__}"

    parser = MyParser(
        description='Download a show on the WeFunk website: \
        The best webradio you could ever find on the Internet.',
        epilog='Website: https://github.com/SamK/wefunk_dl'
    )

    parser.add_argument('-v', '--verbose', action='append_const', const=1,
                        help='Verbose mode. -vv enables debug.')
    parser.add_argument('-V', '--version', action='version',
                        help="shows program version", version=version_string)
    parser.add_argument('show', nargs=1, help='The show ID')

    return parser.parse_args()


def create_logger(verbose_level):
    """ Search Google: Stop Using "print" for Debugging: A 5 Minute
        Quickstart Guide to Python’s logging Module
    """
    logging.basicConfig(level=logging.WARNING,
                        format='%(levelname)s: %(message)s')
    logger = logging.getLogger()
    if verbose_level > 1:
        logger.setLevel(logging.DEBUG)
    if verbose_level == 1:
        logger.setLevel(logging.INFO)
    return logger


def download_show(show_id):
    """ download (or try to) download a show based on its ID
    """
    LOG.info('Trying to download show %s.', show_id)
    try:
        show = WeFunkShow(show_id)
    except FunkError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    try:
        download_media(show.location, show.filename)
    except urllib.error.HTTPError as e:
        LOG.critical(e)
        sys.exit(1)

    LOG.info('Show saved as "%s"', show.filename)


def main():
    """ The so-called "main" function
    """
    LOG.debug('wanted data: %s', ARGUMENTS.show)
    show_id = ARGUMENTS.show[0]
    download_show(show_id)


if __name__ == "__main__":
    ARGUMENTS = parse_arguments()
    # manage verbose stuff
    VERBOSE_LEVEL = 0 if ARGUMENTS.verbose is None else sum(ARGUMENTS.verbose)
    LOG = create_logger(VERBOSE_LEVEL)
    main()

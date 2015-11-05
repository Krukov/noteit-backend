#!/usr/bin/env python
from __future__ import print_function

import argparse
import base64
import getpass
import os
import platform
import sys
import traceback

try: 
    import urllib2 as request  # Py<=3
    from urllib import urlencode
except ImportError:
    import urllib.request as request  # Py>=3
    from urllib.parse import urlencode


__DEBUG = True
__VERSION__ = '0.0.1'
_ANONYMOUS_USER_AGENT = 'anonymous'
_USER_AGENT = '{}'
_HOST = 'http://127.0.0.1:8000'
_TOKEN_PATH = '~/.noteit/noteit.tkn'

_USER_AGENT_HEADER = 'UserAgent'
_AUTH_HEADER = 'Authorization'
_TOKEN_HEADER = 'Authorization'
_TOKEN_HEADER_IN_RESPONSE = ''
GET, POST, PUT = 'GET', 'POST', 'PUT'
_URLS_MAP = {
    'create_note': '',
    'drop_tokens': 'drop_tokens',
    'get_notes': '',
    'get_note': '{i}',
    'report': 'report',
}


def get_options_parser():
    parser = argparse.ArgumentParser(description='note some messages for share it throw machenes')
    parser.add_argument('note', metavar='NOTE', type=str, nargs='*',
                        help='New Note')
    
    parser.add_argument('-u', '--user', help='username', type=str)
    parser.add_argument('-p', '--password', help='password', type=str)
    parser.add_argument('--host', default=_HOST, help='host (default: %s)' % _HOST, type=str)
    
    parser.add_argument('-l', '--last', help='display only last note',
                        action='store_true')
    parser.add_argument('-n', '--num-note', help='display only note with given number', type=int)
    parser.add_argument('-d', '--drop-tokens', help='make all you tokens invalid',
                        action='store_true')
    
    parser.add_argument('-s', '--save', help='enable to save token locally',
                        action='store_true')    
    parser.add_argument('-c', '--color', help='enable colorized output',
                        action='store_true')
    
    parser.add_argument('-a', '--anonymous', help='do not add OS and other info to agent header',
                        action='store_true')
    parser.add_argument('--report', help='report error', action='store_true')
    
    parser.add_argument('-v', '--version', help='displays the current version of noteit',
                        action='store_true')
    return parser


def get_options():
    return get_options_parser().parse_args()


def main():
    options = get_options()
    try:
        if options.version:
            display(get_version())
            _exit()
        if not _get_token_from_system():
            if not options.user:
                display('You mast set "--user" option to use service')
                get_options_parser().print_help()
                _exit()
        if options.drop_tokens:
            out = drop_tokens()

        if options.num_note:
            out = get_note(options.num_note)
        elif options.last:
            out = get_last_note()
        elif options.note:
            out = create_note(options.note)
        else:
            out = get_notes_list()
        display(out.decode('ascii'))
    except Exception as e:
        if __DEBUG:
            raise 
        if not options.report:
            print('Something went wrong! You can sent report to us with "--report" option')
        report(traceback.format_exc(e))
        print('Thanks you for reporting...')


def display(out, stdout=sys.stdout):
    stdout.write(out)


def _exit(status=0):
    sys.exit(status)


def get_version():
    return __VERSION__


def get_notes_list():
    return do_request(_URLS_MAP['get_notes'])


def get_note(number):
    return do_request(_URLS_MAP['get_note'].format(i=number))


def get_last_note():
    return do_request(_URLS_MAP['get_note'].format(i=0))


def create_note(note):
    return do_request(_URLS_MAP['get_notes'], method=POST, data={'data': note})


def report(traceback):
    return do_request(_URLS_MAP['report'], method=POST, data={'data': traceback})


def drop_tokens():
    return do_request(_URLS_MAP['drop_tokens'], method=POST)


def _get_credentions():
    password = get_options().password or getpass.getpass('Input you personal password: ')
    return get_options().user, password
        

def _get_user_agent():
    if get_options().anonymous:
        return _ANONYMOUS_USER_AGENT
    return _generate_user_agent_with_info() 


def _generate_user_agent_with_info():
    return ' '.join([
        platform.platform(),
        platform.python_implementation(),
        platform.python_version(),
        platform.python_compiler(),
    ])


def _get_token_from_system():
    if os.path.isfile(_TOKEN_PATH):
        with open(_TOKEN_PATH) as file:
            return file.read().strip()


def _save_token(token):
    if not os.path.exists(os.path.dirname(_TOKEN_PATH)):
        os.makedirs(os.path.dirname(_TOKEN_PATH))
    with open(_TOKEN_PATH, 'a') as token_file:
        token_file.write(token)
    return True


def _get_encoding_basic_credentions():
    return b'basic ' + base64.b64encode(':'.join(_get_credentions()).encode('ascii'))

def _get_headers():
    headers = {
        _USER_AGENT_HEADER: _get_user_agent(),
    }
    token = _get_token_from_system()
    if token:
        headers[_TOKEN_HEADER] = token
    else:
        headers[_AUTH_HEADER] = _get_encoding_basic_credentions()
    return headers


def do_request(path, *args, **kwargs):
    url = '/'.join([get_options().host, path])
    kwargs.setdefault('headers', {}).update(_get_headers())
    responce = _make_request(url, *args, **kwargs)
    return _response_hendler(responce)


def _response_hendler(responce):
    # TODO: check responce and raise raice custom exseption 
    if _TOKEN_HEADER_IN_RESPONSE in responce.headers and get_options().save:
        _save_token(responce.headers[_TOKEN_HEADER_IN_RESPONSE])
    return responce.read()


def _make_request(url, method=GET, data=None, headers=None):
    method = method.upper()
    if data:
        data = urlencode(data)
    if method == GET:
        req = request.Request('?'.join([url, data or '']))
    elif method in [POST, PUT]:
        req = request.Request(url, data=data)
    req.get_method = lambda *a, **k: method
    if headers:
        for name, value in headers.items():
            req.add_header(name, value)
    return request.urlopen(req)


if __name__ == '__main__':
    main()

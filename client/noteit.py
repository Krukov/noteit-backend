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
    from httplib import HTTPConnection  # Py<=3
    from urllib import urlencode
except ImportError:
    from http.client import HTTPConnection  # Py>=3
    from urllib.parse import urlencode

#TODO: add logging and put it in report 

__DEBUG = False
__VERSION__ = '0.5.0'
_ANONYMOUS_USER_AGENT = 'anonymous'
_USER_AGENT = '{}'
_HOST = '127.0.0.1:8000'
_TOKEN_PATH = os.path.expanduser('~/.noteit/noteit.tkn')

_USER_AGENT_HEADER = 'User-Agent'
_AUTH_HEADER = 'Authorization'
_TOKEN_HEADER = 'Authorization'
_TOKEN_HEADER_IN_RESPONSE = ''
GET, POST, PUT = 'GET', 'POST', 'PUT'
_URLS_MAP = {
    'create_note': '/',
    'drop_tokens': '/drop_tokens',
    'get_token': '/get_token',
    'get_notes': '/',
    'get_note': '/{i}',
    'report': '/report',
}


class AuthenticationError(Exception):
    pass


class ServerError(Exception):
    pass


def display(out, stdout=sys.stdout):
    stdout.write(out + '\n')


def get_version():
    return __VERSION__


def get_notes_list():
    notes, status = do_request(_URLS_MAP['get_notes'])
    if status == 200:
        return notes
    raise Exception('Error at get_notes method: {} {}'.format(status, _))


def get_note(number):
    note, status = do_request(_URLS_MAP['get_note'].format(i=number))
    if status == 200:
        return note
    raise Exception('Error at get_note method: {} {}'.format(status, note))


def get_last_note():
    return get_note(0)


def create_note(note):
    _, status = do_request(_URLS_MAP['get_notes'], method=POST, data={'note': note})
    if status == 201:
        return 'Note saved'
    raise Exception('Error at create_note method: {} {}'.format(status, _))


def report(traceback):
    _, status = do_request(_URLS_MAP['report'], method=POST, data={'traceback': traceback})
    if status == 201:
        return 'Thanks you for reporting...'
    return 'Error: can not report error'


def drop_tokens():
    _, status = do_request(_URLS_MAP['drop_tokens'], method=POST)
    if status == 202:
        return 'Tokens are droped'
    raise Exception('Error at drop_token method: {} {}'.format(status, _))


def _get_token():
    token, status = do_request(_URLS_MAP['get_token'], method=POST)
    if status == 201:
        return token


def registration(question_location):
    promt = "If you are not registered yet, answer the question '{0}': ".format(do_request(question_location)[0])
    answer = input(promt)
    responce, status = do_request(question_location, POST, {'answer': answer})    
    if status == 202:
        return True
    display(responce)
    raise AuthenticationError


def retry(responce):
    return do_request(responce._attrs[0], *responce._attrs[1], **responce._attrs[2])


def _get_credentions():
    password = get_options().password or getpass.getpass('Input your password: ')
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
        'VERSION: {}'.format(get_version()),
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


def _delete_token():
    if os.path.exists(_TOKEN_PATH):
        os.remove(_TOKEN_PATH)


def _get_encoding_basic_credentions():
    return b'basic ' + base64.b64encode(':'.join(_get_credentions()).encode('ascii'))


def _get_headers():
    headers = {
        _USER_AGENT_HEADER: _get_user_agent(),
    }
    token = _get_token_from_system()
    if token:
        headers[_TOKEN_HEADER] = b'token ' + token.encode('ascii')
    else:
        headers[_AUTH_HEADER] = _get_encoding_basic_credentions()
    return headers


def do_request(path, *args, **kwargs):
    kwargs.setdefault('headers', {}).update(_get_headers())
    responce = _make_request(path, *args, **kwargs)
    responce._attrs = path, args, kwargs
    return _response_hendler(responce)


def _response_hendler(responce):
    if responce.status in [401, ]:
        raise AuthenticationError
    elif responce.status > 500:
        raise ServerError 
    elif responce.status in [301, 302, 303, 307]:
        if registration(responce.headers['Location']):
            return retry(responce)
    if _TOKEN_HEADER_IN_RESPONSE in responce.headers and get_options().save:
        _save_token(responce.headers[_TOKEN_HEADER_IN_RESPONSE])
    return responce.read().decode('ascii'), responce.status


def _get_connection():
    return HTTPConnection(get_options().host)


def _make_request(url, method=GET, data=None, headers=None):
    headers = headers or {}
    method = method.upper()
    conn = _get_connection()
    if data:
        data = urlencode(data).encode('ascii')
        if method == GET:
            url = '?'.join([url, data or ''])

    if method in [POST]:
        headers.update({"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"})
    conn.request(method, url, body=data, headers=headers)
    return conn.getresponse()


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
            return
        if not _get_token_from_system():
            if not options.user:
                display('You mast set "--user" option to use service')
                get_options_parser().print_help()
                return

        if options.num_note:
            display(get_note(options.num_note))
        elif options.last:
            display(get_last_note())
        elif options.note:
            display(create_note(' '.join(options.note)))
        else:
            display(get_notes_list())
        
        if options.drop_tokens:
            display(drop_tokens())
            _delete_token()

        if options.save:
            token = _get_token()
            if token:
                _save_token(token)                
    except KeyboardInterrupt:
        display('\n')
    except AuthenticationError:
        display('Error at authentication')
    except ServerError:
        display('Sorry we have got server error. Please, try again later')
    except Exception as e:
        if __DEBUG:
            raise 
        if not options.report:
            print('Something went wrong! You can sent report to us with "--report" option')
            return
        display(report(traceback.format_exc()))
        

if __name__ == '__main__':
    main()

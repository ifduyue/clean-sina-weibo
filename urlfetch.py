#coding: utf8

'''
urlfetch
~~~~~~~~~~

An easy to use HTTP client based on httplib.

:copyright: (c) 2011-2012  Elyes Du.
:license: BSD 2-clause License, see LICENSE for details.
'''

__version__ = '0.4.1'
__author__ = 'Elyes Du <lyxint@gmail.com>'
__url__ = 'https://github.com/lyxint/urlfetch'

import os
import sys

if sys.version_info >= (3, 0):
    py3k = True
    unicode = str
else:
    py3k = False

if py3k:
    from http.client import HTTPConnection, HTTPSConnection
    from urllib.parse import urlencode
    import urllib.parse as urlparse
    import http.cookies as Cookie
    basestring = (str, bytes)

    def b(s):
        return s.encode('latin-1')

    def u(s):
        return s
else:
    from httplib import HTTPConnection, HTTPSConnection
    from urllib import urlencode
    import urlparse
    import Cookie

    def b(s):
        return s

    def u(s):
        return unicode(s, "unicode_escape")

import socket
import base64
from functools import partial
from io import BytesIO
import codecs
writer = codecs.lookup('utf-8')[3]

try:
    import simplejson as json
except ImportError:
    import json


__all__ = [
    'fetch', 'request',
    'get', 'head', 'put', 'post', 'delete', 'options',
    'UrlfetchException',
    'sc2cs', 'random_useragent', 'mb_code',
]

_allowed_methods = ("GET", "DELETE", "HEAD", "OPTIONS",
                    "PUT", "POST", "TRACE", "PATCH")


class UrlfetchException(Exception):
    pass

_boundary_prefix = None


def choose_boundary():
    '''Generate a multipart boundry.

    :rtype: string
    '''

    global _boundary_prefix
    if _boundary_prefix is None:
        _boundary_prefix = "urlfetch"
        import os
        try:
            uid = repr(os.getuid())
            _boundary_prefix += "." + uid
        except AttributeError:
            pass
        try:
            pid = repr(os.getpid())
            _boundary_prefix += "." + pid
        except AttributeError:
            pass
    import uuid
    return "(*^__^*)%s.%s" % (_boundary_prefix, uuid.uuid4().hex)


def _encode_multipart(data, files):
    '''Encode multipart.

    :param data: data to be encoded
    :type data: dict
    :param files: files to be encoded
    :type files: dict
    :rtype: encoded binary string
    '''

    body = BytesIO()
    boundary = choose_boundary()
    part_boundary = b('--%s\r\n' % boundary)

    if isinstance(data, dict):
        for name, value in data.items():
            body.write(part_boundary)
            writer(body).write('Content-Disposition: form-data; '
                               'name="%s"\r\n' % name)
            body.write(b'Content-Type: text/plain\r\n\r\n')
            if py3k and isinstance(value, str):
                writer(body).write(value)
            else:
                body.write(value)
            body.write(b'\r\n')

    for fieldname, f in files.items():
        if isinstance(f, tuple):
            filename, f = f
        elif hasattr(f, 'name'):
            filename = os.path.basename(f.name)
        else:
            filename = None
            raise UrlfetchException("file must has filename")

        if hasattr(f, 'read'):
            value = f.read()
        elif isinstance(f, basestring):
            value = f
        else:
            value = str(f)

        body.write(part_boundary)
        if filename:
            writer(body).write('Content-Disposition: form-data; name="%s"; '
                               'filename="%s"\r\n' % (fieldname, filename))
            body.write(b'Content-Type: application/octet-stream\r\n\r\n')
        else:
            writer(body).write('Content-Disposition: form-data; name="%s"'
                               '\r\n' % name)
            body.write(b'Content-Type: text/plain\r\n\r\n')

        if py3k and isinstance(value, str):
            writer(body).write(value)
        else:
            body.write(value)
        body.write(b'\r\n')

    body.write(b('--' + boundary + '--\r\n'))

    content_type = 'multipart/form-data; boundary=%s' % boundary
    #body.write(b(content_type))

    return content_type, body.getvalue()

## classes ##
class Response(object):
    '''A Response object.

    >>> import urlfetch
    >>> response = urlfetch.get("http://docs.python.org/")
    >>>
    >>> response.status, response.reason, response.version
    (200, 'OK', 10)
    >>> type(response.body), len(response.body)
    (<type 'str'>, 8719)
    >>> type(response.text), len(response.text)
    (<type 'unicode'>, 8719)
    >>> response.getheader('server')
    'Apache/2.2.16 (Debian)'
    >>> response.getheaders()
    [
        ('content-length', '8719'),
        ('x-cache', 'MISS from localhost'),
        ('accept-ranges', 'bytes'),
        ('vary', 'Accept-Encoding'),
        ('server', 'Apache/2.2.16 (Debian)'),
        ('last-modified', 'Tue, 26 Jun 2012 19:23:18 GMT'),
        ('connection', 'close'),
        ('etag', '"13cc5e4-220f-4c36507ded580"'),
        ('date', 'Wed, 27 Jun 2012 06:50:30 GMT'),
        ('content-type', 'text/html'),
        ('x-cache-lookup', 'MISS from localhost:8080')
    ]
    >>> response.headers
    {
        'content-length': '8719',
        'x-cache': 'MISS from localhost',
        'accept-ranges': 'bytes',
        'vary': 'Accept-Encoding',
        'server': 'Apache/2.2.16 (Debian)',
        'last-modified': 'Tue, 26 Jun 2012 19:23:18 GMT',
        'connection': 'close',
        'etag': '"13cc5e4-220f-4c36507ded580"',
        'date': 'Wed, 27 Jun 2012 06:50:30 GMT',
        'content-type': 'text/html',
        'x-cache-lookup': 'MISS from localhost:8080'
    }

    '''

    def __init__(self, r, **kwargs):
        self._r = r  # httplib.HTTPResponse
        self.msg = r.msg

        #: Status code returned by server.
        self.status = r.status

        #: Reason phrase returned by server.
        self.reason = r.reason

        #: HTTP protocol version used by server.
        #: 10 for HTTP/1.0, 11 for HTTP/1.1.
        self.version = r.version
        self._body = None
        self._headers = None
        self._text = None
        self._json = None

        self.getheader = r.getheader
        self.getheaders = r.getheaders

        for k in kwargs:
            setattr(self, k, kwargs[k])

        # if content (length) size is more than length_limit, skip
        try:
            self.length_limit = int(kwargs.get('length_limit'))
        except:
            self.length_limit = None

        content_length = int(self.getheader('Content-Length', 0))
        if self.length_limit and  content_length > self.length_limit:
            self.close()
            raise UrlfetchException("Content length is more than %d bytes"
                                    % self.length_limit)


    def read(self, chunk_size=8192):
        ''' read content (for streaming and large files)
        
        chunk_size: size of chunk, default: 8192       
        '''
        chunk = self._r.read(chunk_size)
        return chunk
    
    def __iter__(self):
        return self

    def __next__(self):
        chunk = self.read()
        if not chunk:
            raise StopIteration
        return chunk

    next = __next__

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @classmethod
    def from_httplib(cls, r, **kwargs):
        '''Generate a :class:`~urlfetch.Response` object from an httplib
        response object.
        '''
        return cls(r, **kwargs)

    @property
    def body(self):
        '''Response body.'''

        if self._body is None:
            content = b("")
            for chunk in self:
                content += chunk
                if self.length_limit and len(content) > self.length_limit:
                    raise UrlfetchException("Content length is more than %d "
                                            "bytes" % length_limit)  
            self._body = content
        return self._body

    # compatible with requests
    #: An alias for :attr:`body`.
    content = body

    @property
    def text(self):
        '''Response body in unicode.'''
        if self._text is None:
            self._text = mb_code(self.body)
        return self._text

    @property
    def json(self, encoding=None):
        '''Load response body as json'''

        if self._json is None:
            try:
                self._json = json.loads(self.text, encoding=encoding)
            except:
                pass
        return self._json

    @property
    def headers(self):
        '''Response headers.

        Response headers is a dict with all keys in lower case.

        >>> import urlfetch
        >>> response = urlfetch.get("http://docs.python.org/")
        >>> response.headers
        {
            'content-length': '8719',
            'x-cache': 'MISS from localhost',
            'accept-ranges': 'bytes',
            'vary': 'Accept-Encoding',
            'server': 'Apache/2.2.16 (Debian)',
            'last-modified': 'Tue, 26 Jun 2012 19:23:18 GMT',
            'connection': 'close',
            'etag': '"13cc5e4-220f-4c36507ded580"',
            'date': 'Wed, 27 Jun 2012 06:50:30 GMT',
            'content-type': 'text/html',
            'x-cache-lookup': 'MISS from localhost:8080'
        }

        '''

        if self._headers is None:
            self._headers = dict((k.lower(), v) for k, v in self.getheaders())
        return self._headers

    @property
    def cookies(self):
        '''Cookies in dict'''

        c = Cookie.SimpleCookie(self.getheader('set-cookie'))
        sc = [(i.key, i.value) for i in c.values()]
        return dict(sc)

    @property
    def cookiestring(self):
        '''Cookie string'''
        cookies = self.cookies
        return '; '.join(['%s=%s' % (k, v) for k, v in cookies.items()])

    def close(self):
        '''Close the connection'''
        if hasattr(self, 'connection'):
            self.connection.close()
        self._r.close()

    def __del__(self):
        self.close()


class Session(object):
    '''A session object.

    :class:`urlfetch.Session` can hold common headers and cookies.
    Every request issued by a :class:`urlfetch.Session` object will bring u
    these headers and cookies.
                             
    :class:`urlfetch.Session` plays a role in handling cookies, just like a
    cookiejar.

    :param headers: init headers
    :type headers: dict, optional
    :param cookies: init cookies
    :type cookies: dict, optional
    :param auth: (username, password) for basic authentication
    :type auth: tuple, optional
    '''

    def __init__(self, headers={}, cookies={}, auth=None):
        '''init a :class:`~urlfetch.Session` object

        '''
        self._headers = {}
        self._cookies = cookies.copy()

        for k, v in headers.items():
            self._headers[k.title()] = v

        if auth is not None and isinstance(auth, (list, tuple)):
                auth = '%s:%s' % tuple(auth)
                auth = base64.b64encode(auth.encode('utf-8'))
                self._headers['Authorization'] = 'Basic ' + auth.decode('utf-8')

    def putheader(self, header, value):
        '''Add an header to default headers'''
        self._headers[header.title()] = value

    def popheader(self, header):
        '''Remove an header from default headers'''
        return self._headers.pop(header.title())

    def putcookie(self, key, value=""):
        '''Add an cookie to default cookies'''
        self._cookies[key] = value

    def popcookie(self, key):
        '''Remove an cookie from default cookies'''
        return self._cookies.pop(key)

    @property
    def headers(self):
        return dict((k.lower(), v) for k, v in self._headers.items())

    @property
    def cookies(self):
        return self._cookies

    @property
    def cookiestring(self):
        return '; '.join(['%s=%s' % (k, v) for k, v in self.cookies.items()])

    def snapshot(self):
        session = {'headers': self._headers, 'cookies': self._cookies}
        return session

    def dump(self, fileobj, cls='marshal'):
        '''pack a session and write packed bytes to fileobj
        
        >>> s = urlfetch.Session({'User-Agent': 'urlfetch'}, {'foo': 'bar'})
        >>> f = open('session.jar', 'wb')
        >>> s.dump(f)
        >>> f.close()

        :param fileobj: a file(-like) object which have ``write`` method
        :type fileobj: file
        :param cls: use which class to pack the session
        :type cls: string, ``marshal``, ``pickle``, etc...
        '''
        dump = import_object('%s.dump' % cls)
        return dump(self.snapshot(), fileobj)

    def dumps(self, cls='marshal'):
        '''pack a seesion and return packed bytes
        
        >>> s = urlfetch.Session({'User-Agent': 'urlfetch'}, {'foo': 'bar'})
        >>> s.dumps()
        ...
        
        :param cls: use which class to pack the session
        :type cls: string, ``marshal``, ``pickle``, etc...
        :rtype: packed bytes
        '''
        dumps = import_object('%s.dumps' % cls)
        return dumps(self.snapshot())

    def load(self, fileobj, cls='marshal'):
        '''unpack a session from fileobj and load it into current session

        >>> s = urlfetch.Session()
        >>> s = open('session.jar', 'rb')
        >>> s.load(f)
        >>> f.close()
        
        :param fileobj: a file(-like) object which have ``read`` method
        :type fileobj: file
        :param cls: use which class to unpack the session
        :type cls: string, ``marshal``, ``pickle``, etc...
        :rtype: unpacked session 
        '''
        load = import_object('%s.load' % cls)
        session = load(fileobj)
        self._headers.update(session['headers'])
        self._cookies.update(session['cookies'])
        return session

    def loads(self, string, cls='marshal'):
        '''unpack a seesion from string and load it into current session
        
        >>> s = urlfetch.Session({'User-Agent': 'urlfetch'}, {'foo': 'bar'})
        >>> s.loads(s.dumps())
        {'headers': {'User-Agent': 'urlfetch'}, 'cookies': {'foo': 'bar'}}
        
        :param string: the string to be unpacked
        :type string: bytes
        :param cls: use which class to pack the session
        :type cls: string, ``marshal``, ``pickle``, etc...
        :rtype: unpacked session
        '''
        loads = import_object('%s.loads' % cls)
        session = loads(string)
        self._headers.update(session['headers'])
        self._cookies.update(session['cookies'])
        return session

    def request(self, *args, **kwargs):
        '''Issue a request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = request(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def fetch(self, *args, **kwargs):
        '''Fetch an URL'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = fetch(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

 
    def get(self, *args, **kwargs):
        '''Issue a get request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = get(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def post(self, *args, **kwargs):
        '''Issue a post request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = post(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def put(self, *args, **kwargs):
        '''Issue a put request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = put(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def delete(self, *args, **kwargs):
        '''Issue a delete request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = delete(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def head(self, *args, **kwargs):
        '''Issue a head request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = head(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def options(self, *args, **kwargs):
        '''Issue a options request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = options(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def trace(self, *args, **kwargs):
        '''Issue a trace request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = trace(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r

    def patch(self, *args, **kwargs):
        '''Issue a patch request'''
        headers = self.headers.copy()
        if self.cookiestring:
            headers['Cookie'] = self.cookiestring
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        r = patch(*args, **kwargs)

        cookies = r.cookies
        self._cookies.update(cookies)

        return r


## methods ##
def fetch(*args, **kwargs):
    ''' fetch an URL.

    :func:`~urlfetch.fetch` is a wrapper of :func:`~urlfetch.request`.
    It calls :func:`~urlfetch.get` by default. If one of parameter ``data``
    or parameter ``files`` is supplied, :func:`~urlfetch.post` is called.
    '''

    data = kwargs.get('data', None)
    files = kwargs.get('files', {})

    if data is not None and isinstance(data, (basestring, dict)) or files:
        return post(*args, **kwargs)
    return get(*args, **kwargs)


def request(url, method="GET", data=None, headers={},
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT, files={},
            randua=False, auth=None, length_limit=None, **kwargs):

    ''' request an URL

    :param url: URL to be fetched.
    :type url: string
    :param method: HTTP method, one of ``GET``, ``DELETE``, ``HEAD``,
                   ``OPTIONS``, ``PUT``, ``POST``, ``TRACE``, ``PATCH``.
                   ``GET`` by default.
    :type method: string, optional
    :param headers: HTTP request headers
    :type headers: dict, optional
    :param timeout: timeout in seconds, socket._GLOBAL_DEFAULT_TIMEOUT
                    by default
    :type timeout: integer or float, optional
    :param files: files to be sended
    :type files: dict, optional
    :param randua: if ``True`` or ``path string``, use a random user-agent in
                    headers, instead of ``'urlfetch/' + __version__``
    :type randua: bool or string, default is ``False``
    :param auth: (username, password) for basic authentication
    :type auth: tuple, optional
    :param length_limit: if ``None``, no limits on content length, if the limit
                         reached raised exception 'Content length is more
                         than ...'
    :type length_limit: integer or None, default is ``none``
    :rtype: A :class:`~urlfetch.Response` object
    '''

    method = method.upper()
    if method not in _allowed_methods:
        raise UrlfetchException("Method should be one of " +
                                ", ".join(_allowed_methods))

    parsed_url = parse_url(url)

    if parsed_url['scheme'] == 'https':
        h = HTTPSConnection(parsed_url['host'], port=parsed_url['port'],
                            timeout=timeout)
    elif parsed_url['scheme'] == 'http':
        h = HTTPConnection(parsed_url['host'], port=parsed_url['port'],
                           timeout=timeout)
    else:
        raise UrlfetchException('Unsupported protocol %s' % scheme)

    # is randua bool or path
    if randua and isinstance(randua, basestring) and \
        os.path.isfile(path):
        randua = True
        randua_file = randua
    else:
        randua = bool(randua)
        randua_file = None

    # default request headers
    reqheaders = {
        'Accept': '*/*',
        'User-Agent': random_useragent(randua_file) if randua else \
                        'urlfetch/' + __version__,
        'Host': parsed_url['host'],
    }

    if parsed_url['username'] is not None and parsed_url['password'] is not \
            None and auth is None:
        auth = (parsed_url['username'], parsed_url['password'])
    if auth is not None:
        if isinstance(auth, (list, tuple)):
            auth = '%s:%s' % tuple(auth)
        auth = base64.b64encode(auth.encode('utf-8'))
        reqheaders['Authorization'] = 'Basic ' + auth.decode('utf-8')

    if files:
        content_type, data = _encode_multipart(data, files)
        reqheaders['Content-Type'] = content_type
    elif isinstance(data, dict):
        data = urlencode(data, 1)

    if isinstance(data, basestring) and not files:
        # httplib will set 'Content-Length', also you can set it by yourself
        reqheaders["Content-Type"] = "application/x-www-form-urlencoded"
        # what if the method is GET, HEAD or DELETE
        # just do not make so much decisions for users

    for k, v in headers.items():
        reqheaders[k.title()] = v

    h.request(method, parsed_url['uri'], data, reqheaders)
    response = h.getresponse()
    return Response.from_httplib(response, reqheaders=reqheaders,
                                 connection=h, length_limit=length_limit)

# some shortcuts
get = partial(request, method="GET")
post = partial(request, method="POST")
put = partial(request, method="PUT")
delete = partial(request, method="DELETE")
head = partial(request, method="HEAD")
options = partial(request, method="OPTIONS")
# No entity body can be sent with a TRACE request.
trace = partial(request, method="TRACE", files={}, data=None)
patch = partial(request, method="PATCH")



## helpers ##
def parse_url(url):
    '''returns dictionary of parsed url:
    scheme, netloc, path, params, query, fragment, uri, username, password,
    host and port
    '''
    result = dict()
    parsed = urlparse.urlparse(url)
    
    result['scheme'] = parsed.scheme
    result['netloc'] = parsed.netloc
    result['path'] = parsed.path
    result['params'] = parsed.params
    result['query'] = parsed.query
    result['fragment'] = parsed.fragment
    result['uri'] = parsed.path
    if parsed.query:
        result['uri'] += '?' + parsed.query
    result['username'] = parsed.username
    result['password'] = parsed.password
    result['host'] = result['hostname'] = parsed.hostname
    result['port'] = parsed.port

    return result

def mb_code(s, coding=None):
    '''encoding/decoding helper'''

    if isinstance(s, unicode):
        return s if coding is None else s.encode(coding)
    for c in ('utf-8', 'gb2312', 'gbk', 'gb18030', 'big5'):
        try:
            s = s.decode(c, errors='replace')
            return s if coding is None else s.encode(coding, errors='replace')
        except:
            pass
    return s


def sc2cs(sc):
    '''Convert Set-Cookie header to cookie string.

    Set-Cookie can be retrieved from a :class:`~urlfetch.Response` instance::

        sc = response.getheader('Set-Cookie')

    :param sc: Set-Cookie
    :type sc: string
    :rtype: cookie string, which is name=value pairs joined by ``\;``.
    '''
    c = Cookie.SimpleCookie(sc)
    sc = ['%s=%s' % (i.key, i.value) for i in c.values()]
    return '; '.join(sc)

def random_useragent(filename=None):
    '''Returns a User-Agent string randomly from file.

    :param filename: path to the file from which a random useragent
                     is generated
    :type filename: string, optional
    '''
    import os
    import random
    from time import time

    if filename is None:
        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'share', 'urlfetch', 'urlfetch.useragents.list')
        if not os.path.isfile(filename):
            filename = os.path.join(sys.prefix, 'share', 'urlfetch', 
                                'urlfetch.useragents.list')

    if os.path.isfile(filename):
        f = open(filename)
        filesize = os.stat(filename)[6]
        r = random.Random(time())

        while True:
            pos = f.tell() + r.randint(0, filesize)
            pos %= filesize
            f.seek(pos)

            # in case we are in middle of a line
            f.readline()

            line = f.readline().strip()
            if line and not line.startswith('#'):
                break

        f.close()
        return line

    return 'urlfetch/%s' % __version__

def import_object(name):
    """Imports an object by name.

    import_object('x.y.z') is equivalent to 'from x.y import z'.
    
    >>> import tornado.escape
    >>> import_object('os.path') is os.path
    True
    >>> import_object('os.path.dirname') is os.path.dirname
    True
    """
    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1])

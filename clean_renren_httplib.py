#coding: utf8

from urlfetch import *
import re
from urlparse import parse_qsl, urljoin

class Renren(object):
    
    def __init__(self, username, password):
        self.cookies = None
        self.username = username
        self.password = password
    
    def login(self):
        post = {
            'email': self.username,
            'password': self.password
        }
        response = fetch(
            'http://3g.renren.com/login.do?fx=0&autoLogin=true',
            data = post
        )
        
        set_cookie = response.msg.getheaders('set-cookie')
        self.cookies = setcookielist2cookiestring(set_cookie)
        return self.cookies
    
    
    def del_minifeed(self):
        while True:
            response = fetch(
                'http://3g.renren.com/profile.do',
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'''/delminifeed.do\?id=(\d+)''', response.body)
            if not data:
                break
            for i in data:
                post = {
                    'id': i,
                    'referer': 'http://3g.renren.com/profile.do',
                }
                try:
                    fetch(
                        'http://3g.renren.com/delminifeed.do',
                        data = post, 
                        headers = {'Cookie': self.cookies}
                    )
                    print i
                except:pass
                
    def del_statuses(self):
        while True:
            response = fetch(
                'http://3g.renren.com/status/getdoing.do',
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'''href="([^"]*?wdelstatus.do[^"]*?id=(\d+)[^"]*?sid=([^&;]+)[^"]*?)"''', response.body)
            if not data:
                break
            for url, id, sid in data:
                url = url.replace('&amp;', '&')
                a, b = url.split('?', 1)
                qs = dict(parse_qsl(b))
                del qs['curpage']
                del qs['sid']
                action = a + '?' + '&'.join(['='.join(k) for k in qs.items()])
                
                try:
                    fetch(
                        action,
                        data = {
                            'sid': sid,
                            'referer': url,
                            'cr': 0
                        },
                        headers = {
                            'Cookie': self.cookies,
                            'referer': url
                        }
                    )
                    print id
                except:pass
                
if __name__ == '__main__':
    def sigint():
        def _sigint(a,b):
            print a, b
            import os, sys
            os.kill(0, signal.SIGTERM)
            sys.exit()
        import signal
        signal.signal(signal.SIGINT, _sigint)
    sigint()
    import sys
    username, password = sys.argv[1:]
    renren = Renren(username, password)
    renren.login()
    renren.del_minifeed()
    renren.del_statuses()
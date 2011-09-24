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
                
    def unfollow(self):
        while True:
            response = fetch(
                'http://weibo.cn/dpool/ttt/attention.php?cat=0',
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'href="attnDeal\.php\?([^"]+?act=del[^"]+)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'delc'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/dpool/ttt/attnDeal.php?' + qs
                
                try:
                    fetch(
                        url,
                        headers = {'Cookie': self.cookies}
                    )
                    print url
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
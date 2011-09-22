#coding: utf8

from urlfetch import *
import re
from urlparse import parse_qsl, urljoin

class Sina(object):
    
    def __init__(self, username, password):
        self.cookies = None
        self.username = username
        self.password = password
    
    def login(self):
        
        response = fetch('http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php')
        data = response.body
        vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
        pname = re.search(r'''name="password_(\d+)"''', data).group(1)
        
        post = {
            'mobile': self.username,
            'password_'+pname: self.password,
            'vk': vk,
            'remember': 'on',
            'submit': '1'
        }
        response = fetch(
            'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php',
            data = post
        )
        
        set_cookie = response.msg.getheaders('set-cookie')
        self.cookies = setcookielist2cookiestring(set_cookie)
        return self.cookies
    
    
    def del_tweets(self):
        while True:
            response = fetch(
                'http://weibo.cn/dpool/ttt/home.php?cat=1',
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'href="mblogDeal\.php\?([^"]+?act=del[^"]+)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'dodel'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/dpool/ttt/mblogDeal.php?' + qs
                
                try:
                    fetch(
                        url,
                        headers = {'Cookie': self.cookies}
                    )
                    print url
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
                
    def remove_followers(self, black=False):
        while True:
            response = fetch(
                'http://weibo.cn/dpool/ttt/attention.php?cat=1',
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'href="attnDeal\.php\?([^"]+?act=remove[^"]+)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'removec'
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
    username, password = sys.argv[1:]
    sina = Sina(username, password)
    sina.login()
    sina.del_tweets()
    #sina.unfollow()
    #sina.remove_followers()
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
        response = fetch('http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php', headers={'User-Agent': 'android'})
        data = response.body
        vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
        pname = re.search(r'''name="password_(\d+)"''', data).group(1)
        
        post = {
            'mobile': self.username,
            'password_'+pname: self.password,
            #'capId': capid,
            'vk': vk,
            'remember': 'on',
            'submit': '1'
        }
        response = fetch(
            'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php',
            data = post,
            headers = {'User-Agent': 'android'},
        )
        data = response.body
        captcha = re.search(r'''captcha/show.php\?cpt=(\w+)''', data)
        if captcha:
            url = '''http://weibo.cn/interface/f/ttt/captcha/show.php?cpt=''' + captcha.group(1)
            print url
            captcha = raw_input("open the url and input the captcha:")
            vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
            pname = re.search(r'''name="password_(\d+)"''', data).group(1)
            capid = re.search(r'''name="capId"\s+?value="(.*?)"''', data).group(1)
            post = {
                'mobile': self.username,
                'password_'+pname: self.password,
                'capId': capid,
                'vk': vk,
                'remember': 'on',
                'submit': '1',
                'code': captcha.strip(),
            }
            response = fetch(
                'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php',
                data = post,
                headers = {'User-Agent': 'android'},
            )
        set_cookie = response.msg.getheaders('set-cookie')
        self.cookies = setcookielist2cookiestring(set_cookie)
        print self.cookies
        response = fetch(
            'http://weibo.cn/',
            headers = {'Cookie': self.cookies, 'User-Agent': 'android'},
        )
        self.uid = re.search(r'''uid=(\d+)''', response.body).group(1)
        return self.cookies
    
    
    def del_tweets(self):
        while True:
            response = fetch(
                'http://weibo.cn/%s/profile' % self.uid,
                headers={'Cookie': self.cookies}
            )
            data = re.findall(r'href="/mblog/del\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'delc'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/mblog/del?' + qs
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
                'http://weibo.cn/%s/follow' % self.uid,
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'href="/attention/del\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'delc'
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/attention/del?' + qs
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
                'http://weibo.cn/%s/fans' % self.uid,
                headers={'Cookie': self.cookies}
            )
            
            data = re.findall(r'href="/attention/remove\?(.*?)"', response.body)
            if not data:
                break
            for i in data:
                j = parse_qsl(i)
                qs = dict(j)
                qs['act'] = 'removec'
                if black:
                    qs['black'] = 1
                qs = '&'.join(['='.join(k) for k in qs.items()])
                url = 'http://weibo.cn/attention/remove?' + qs
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
    import sys
    sigint()
    username, password = sys.argv[1:]
    sina = Sina(username, password)
    sina.login()
    sina.del_tweets()
    #sina.unfollow()
    #sina.remove_followers()

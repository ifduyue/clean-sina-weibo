from urllib import urlencode
from StringIO import StringIO
from sys import argv
from urlparse import parse_qsl
import pycurl
import re
 
b = StringIO()
c = pycurl.Curl()
 
def fake_write(x):pass

def sigint(signum, frame):
    global b, c
    del b, c
    import sys
    print '\n\nsigint received, exiting...'
    sys.exit()

import signal
signal.signal(signal.SIGINT, sigint)
 
def reset():
    b.truncate(0)
    c.reset()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.COOKIEJAR, 't.sina.cn')
    c.setopt(pycurl.FOLLOWLOCATION, True)
    return b, c
 
def login(username, password):
    reset()
    c.setopt(pycurl.URL, 'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php')
    c.perform()
    
    data = b.getvalue()
    vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
    pname = re.search(r'''name="password_(\d+)"''', data).group(1)

    reset()
    c.setopt(pycurl.POST, True)
    c.setopt(pycurl.URL, 'http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php')
    c.setopt(pycurl.POSTFIELDS, urlencode({
        'mobile': username,
        'password_'+pname: password,
        'vk': vk,
        'remember': 'on',
        'submit': '1'
    }))
    c.perform()
    return b.getvalue()
 
def del_tweets():
    while True:
        reset()
        c.setopt(pycurl.URL, 'http://t.sina.cn/dpool/ttt/home.php?cat=1')
        c.perform()
        data = b.getvalue()
        data =  re.findall(r'href="mblogDeal\.php\?([^"]+?act=del[^"]+)"', data)
        if not data:
            break
        for i in data:
            j = parse_qsl(i)
            qs = dict(j)
            qs['act'] = 'dodel'
            qs = '&'.join(['='.join(k) for k in qs.items()])
            url = 'http://t.sina.cn/dpool/ttt/mblogDeal.php?' + qs
 
            reset()
            c.setopt(pycurl.WRITEFUNCTION, fake_write)
            c.setopt(pycurl.URL, url)
            try:
                c.perform()
                print url
            except:pass
 
def unfollow():
    while True:
        reset()
        c.setopt(pycurl.URL, 'http://t.sina.cn/dpool/ttt/attention.php?cat=0')
        c.perform()
        data = b.getvalue()
        data =  re.findall(r'href="attnDeal\.php\?([^"]+?act=del[^"]+)"', data)
        if not data:
            break
        for i in data:
            j = parse_qsl(i)
            qs = dict(j)
            qs['act'] = 'delc'
            qs = '&'.join(['='.join(k) for k in qs.items()])
            url = 'http://t.sina.cn/dpool/ttt/attnDeal.php?' + qs
 
            reset()
            c.setopt(pycurl.WRITEFUNCTION, fake_write)
            c.setopt(pycurl.URL, url)
            try:
                c.perform()
                print url
            except:pass
 
def remove_followers(black=False):
    while True:
        reset()
        c.setopt(pycurl.URL, 'http://t.sina.cn/dpool/ttt/attention.php?cat=1')
        c.perform()
        data = b.getvalue()
        data =  re.findall(r'href="attnDeal\.php\?([^"]+?act=remove[^"]+)"', data)
        if not data:
            break
        for i in data:
            j = parse_qsl(i)
            qs = dict(j)
            qs['act'] = 'removec'
            if black:
                qs['black'] = '1'
            qs = '&'.join(['='.join(k) for k in qs.items()])
            url = 'http://t.sina.cn/dpool/ttt/attnDeal.php?' + qs
 
            reset()
            c.setopt(pycurl.WRITEFUNCTION, fake_write)
            c.setopt(pycurl.URL, url)
            try:
                c.perform()
                print url
            except:pass
 
if __name__ == '__main__':
    username, password = argv[1:]
    login(username, password)
    del_tweets()
    #unfollow()
    #remove_followers()

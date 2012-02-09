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
        response = fetch(
            'http://3g.renren.com/login.do?fx=0&autoLogin=true',
            data = {
                'email': self.username,
                'password': self.password
            },
        )
        
        set_cookie = response.msg.getheaders('set-cookie')
        self.cookies = setcookielist2cookiestring(set_cookie)
        self.qs = dict(parse_qsl(response.getheader('Location').split('?', 1)[-1]))
        self.qs['uid'] = self.qs['bm'].split('_', 1)[0]
        print self.qs
        return response

    def hide_log(self):
        prefix = 'http://3g.renren.com/blog/wmyblog.do?id=%s&sid=%s&curpage=%d'
        logs = []
        
        r = fetch(prefix % (self.qs['uid'], self.qs['sid'], 0))
        logs.extend(re.findall(r'''weditentry.do\?id=(\d+)''', r.body))
        
        try: pagetotal = int(re.search(r'''\(第\d+/(\d+)页\)''', r.body).group(1))
        except: pagetotal = 0
        
        for i in xrange(1, pagetotal):
            r = fetch(prefix % (self.qs['uid'], self.qs['sid'], i))
            logs.extend(re.findall(r'''weditentry.do\?id=(\d+)''', r.body))

        print 'you got', len(logs), 'logs'

        for log in logs:
            url = '''http://3g.renren.com/blog/weditentry.do?id=%s&sid=%s''' % (log, self.qs['sid'])

            r = fetch(url)
            try: 
                title = re.search(r'''<input name="title".*?value="(.*?)"''', r.body).group(1)
                body = re.search(r'''<textarea name="body".*?>(.*?)<''', r.body, re.S).group(1)
                tsc = re.search(r'''<input type="hidden" name="tsc".*?value="(.*?)"''', r.body).group(1)
                print log, title
                print tsc
                r = fetch(
                    'http://3g.renren.com/blog/weditentry.do?',
                    data = {
                        'body': body,
                        'control': -1,
                        'id': log,
                        'passwd': '',
                        'publish': '发布',
                        'sid': self.qs['sid'],
                        'title': title,
                        'tsc': tsc,
                    },
                )
            except: pass
            
    
    
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
    renren.hide_log()
    #renren.del_minifeed()
    #renren.del_statuses()


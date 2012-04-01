#!/usr/bin/env python
#-*- coding: utf8 -*-


import gtk
import pygtk
pygtk.require(u"2.0")
import gobject

#coding: utf8

from urlfetch import *
import re
from urlparse import parse_qsl, urljoin

class Sina(object):
    
    def __init__(self, username, password):
        self.cookies = None
        self.username = username
        self.password = password
    
    def login(self, post=None):
        
        response = fetch('http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php')
        data = response.body
        vk = re.search(r'''name="vk"\s+?value="(.*?)"''', data).group(1)
        pname = re.search(r'''name="password_(\d+)"''', data).group(1)
        
        
        
        open('test.html', 'wb').write(data)
        if post is None:
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
        
        data = response.body
        captcha = re.search(r'''captcha/show.php\?cpt=(\w+)''', data)
        if captcha:
            url = '''http://weibo.cn/interface/f/ttt/captcha/show.php?cpt=''' + captcha.group(1)
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
            }
            return {
                'code': 1,
                'msg': 'captcha required',
                'url': url,
                'post': post,
            }
        
        set_cookie = response.msg.getheaders('set-cookie')
        self.cookies = setcookielist2cookiestring(set_cookie)
        
        
        response = fetch(
            'http://weibo.cn/',
            headers = {'Cookie': self.cookies},
        )
        self.uid = re.search(r'''uid=(\d+)''', response.body).group(1)
        return {
            'code': 0,
            'msg': 'OK',
            'cookies': self.cookies,
            'uid': self.uid,
        }
    
    
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
                    yield url
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
                    yield url
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
                    yield url
                except:pass
        
class CleanSinaWeiboGUI(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_size_request(600, 480)
        self.set_title(u"新浪微博清理器")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(True)
        self.connect(u"destroy", gtk.main_quit)
        
        self.running = False
        
        self.vbox = gtk.VBox()
        
        self.label_username = gtk.Label(u"帐号")
        self.entry_username = gtk.Entry()
        self.entry_username.connect("changed", self.toggle_button_active_cb)
        self.hbox_username = gtk.HBox()
        self.hbox_username.pack_start(self.label_username, False)
        self.hbox_username.pack_start(self.entry_username, True, True, 5)
        
        
        self.label_password = gtk.Label(u"密码")
        self.entry_password = gtk.Entry()
        self.entry_password.set_visibility(False)
        self.entry_password.connect("changed", self.toggle_button_active_cb)
        self.hbox_password = gtk.HBox()
        self.hbox_password.pack_start(self.label_password, False)
        self.hbox_password.pack_start(self.entry_password, True, True, 5)
        
        self.checkbutton_del_tweets = gtk.CheckButton(u"删除微博")
        self.checkbutton_unfollow = gtk.CheckButton(u"删除关注")
        self.checkbutton_remove_followers = gtk.CheckButton(u"删除粉丝")
        self.hbox_checkbutton = gtk.HBox()
        self.hbox_checkbutton.pack_start(self.checkbutton_del_tweets)
        self.hbox_checkbutton.pack_start(self.checkbutton_unfollow)
        self.hbox_checkbutton.pack_start(self.checkbutton_remove_followers)
        
        self.button = gtk.Button(u"开始清理")
        self.button.connect("clicked", self.button_cb)
        
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw.set_shadow_type(gtk.SHADOW_IN)
        self.textview = gtk.TextView()
        self.sw.add(self.textview)
        
        self.buffer = gtk.TextBuffer(None)
        self.textview.set_buffer(self.buffer)
        self.textview.set_editable(False)
        
        # setup textview auto-scrolling
        itr = self.buffer.get_end_iter()
        self.buffer.create_mark("bottom", itr, False)
        gobject.timeout_add(500, self.auto_scrolling_cb)
        
        self.vbox.pack_start(self.hbox_username, False, False, 5)
        self.vbox.pack_start(self.hbox_password, False, False, 5)
        self.vbox.pack_start(self.hbox_checkbutton, False, False, 5)
        self.vbox.pack_start(self.button, False, False, 5)
        self.vbox.pack_start(self.sw, True, True, 5)
        
        self.add(self.vbox)
        self.show_all()
        
    def button_cb(self, button):
        if self.running:
            return
        
        self.buffer.set_text(u"")
        
        username = self.entry_username.get_text()
        password = self.entry_password.get_text()
        
        if not (username and password):
            dialog = gtk.Dialog(u"错误", self, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
            dialog.set_default_response(gtk.RESPONSE_OK)
            dialog_label = gtk.Label(u"您必须填入帐号和密码")
            dialog.vbox.add(dialog_label)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            return
        
        del_tweets = self.checkbutton_del_tweets.get_active()
        unfollow = self.checkbutton_unfollow.get_active()
        remove_follower = self.checkbutton_remove_followers.get_active()
        
        if not (del_tweets or unfollow or remove_follower):
            dialog = gtk.Dialog(u"错误", self, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
            dialog.set_default_response(gtk.RESPONSE_OK)
            dialog_label = gtk.Label(u"[删除微博, 删除关注, 删除粉丝], 必须至少选择一项")
            dialog.vbox.add(dialog_label)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            return
        
        def job():
             
            def append_info(text):
                iter = self.buffer.get_end_iter()
                self.buffer.insert(iter, "\n"+text)
                
            self.running = True 
            sina = Sina(username, password)
            append_info(u"登录中...")
            yield True
            try:
                ret = sina.login()
                while ret['code'] == 1:
                        dialog = gtk.Dialog(u"需要输入验证码", self, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK, "Cancel", gtk.RESPONSE_CANCEL))
                        dialog.set_default_response(gtk.RESPONSE_OK)
                        dialog_label = gtk.Label(u"请填入下图验证码, 如果没有显示图片请打开链接查看图片")
                        url = ret['url']
                        url = '''<a href="%s">%s</a>''' % (url, url)
                        url_label = gtk.Label()
                        url_label.set_markup(url)
                        dialog.vbox.pack_start(dialog_label, False, False, 5)
                        dialog.vbox.pack_start(url_label, False, False, 5)
                        
                        try:
                            image = gtk.Image()
                            loader=gtk.gdk.PixbufLoader()
                            resp = fetch(ret['url'])
                            loader.write(resp.body)
                            loader.close()        
                            image.set_from_pixbuf(loader.get_pixbuf())
                            dialog.vbox.pack_start(image, False, False, 5)
                        except: pass
                        
                        entry = gtk.Entry()
                        dialog.vbox.pack_start(entry, False, False, 5)
                        
                        dialog.show_all()
                        response = dialog.run()
                        if response == gtk.RESPONSE_OK:
                            captcha = entry.get_text()
                            captcha = captcha.strip()
                            dialog.destroy()
                            post = ret['post']
                            post['code'] = captcha
                            ret = sina.login(post)
                        else:
                            append_info(u"取消任务")
                            dialog.destroy()
                            yield False
                
                if ret['code'] != 0:
                    append_inf(u"登录失败")
                    yield False
                    
                if del_tweets:
                    append_info(u"开始删除微博...")
                    for url in sina.del_tweets():
                        append_info(u"%s" % url)
                        yield True
                    append_info(u"\n")
                    yield True
                
                if unfollow:
                    append_info(u"开始删除关注...")
                    for url in sina.unfollow():
                        append_info(u"%s" % url)
                        yield True
                    append_info(u"\n")
                    yield True
                    
                if unfollow:
                    append_info(u"开始删除粉丝...")
                    for url in sina.remove_followers():
                        append_info(u"%s" % url)
                        yield True
                    append_info(u"\n")
                    yield True
                    
                append_info(u"完成.")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                append_info(u"[Error] %s" % str(e))
                append_info(tb+"\n\n")
                yield True
            finally:
                self.running = False
                yield False
        
        # see http://faq.pygtk.org/index.py?req=show&file=faq23.020.htp
        task = job()
        gobject.idle_add(task.next)
        
        
    def toggle_button_active_cb(self, entry):
        pass
    
    def auto_scrolling_cb(self):
        itr = self.buffer.get_end_iter()
        mark = self.buffer.get_mark("bottom")
        self.buffer.move_mark(mark, itr)
        self.textview.scroll_mark_onscreen(mark)
        return True
        
    def main(self):
        gtk.main()
        
if __name__ == '__main__':
    import sys
    from StringIO import StringIO
    #sys.stdout = sys.stderr = StringIO()
    gui = CleanSinaWeiboGUI()
    gui.main()

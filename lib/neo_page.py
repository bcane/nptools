# NeoPage: Wrapper around pycurl that simulates a browser.
# TODO: Maybe eventually replace this with Selenium.

import io
import os
import pycurl
import re
import sqlite3
import time
import pickle
from urllib.parse import urlsplit, urlencode, quote_plus, quote
from selenium import webdriver
from . import util

class NotLoggedInError(Exception):
    pass

cookies_db = None
COOKIE_FILE = 'nptools.cookies'

class NeoPage:
    def __init__(self, path=None, base_url=None, save_pages=False):
        self.byte_content = b''
        self.content = ''
        self.last_file_path = ''
        self.referer = ''
        self.base_url = base_url or 'http://www.neopets.com'
        self.driver = webdriver.Firefox()
        self.save_pages = save_pages
        if path:
            self.driver.get(path)

    def save_to_file(self, filename=None):
        open(filename or self.last_file_path, 'wb').write(self.byte_content)

    def load_file(self, filename):
        self.content = open(filename, 'r').read()

    def perform(self, url, opts=[]):
        storage = io.BytesIO()

        done_request = False
        for _ in range(5):
            try:
                storage.seek(0)
                storage.truncate(0)
                curl = pycurl.Curl()
                curl.setopt(pycurl.TIMEOUT_MS, 8000)
                curl.setopt(pycurl.FOLLOWLOCATION, True)
                curl.setopt(pycurl.REFERER, self.referer)
                curl.setopt(pycurl.WRITEFUNCTION, storage.write)
                if cookies_db:
                    host = '.'.join(self.base_url.rsplit('/', 1)[-1].split('.')[-2:])
                    c = cookies_db.cursor()
                    c.execute('''
                    SELECT name, value FROM moz_cookies
                    WHERE baseDomain = ?
                    AND expiry >= strftime('%s', 'now')
                    ''', (host,))
                    results = list(c.fetchall())
                    cookie_string = ';'.join(f'{name}={value}' for name, value in results)
                    curl.setopt(pycurl.COOKIE, cookie_string)
                else:
                    curl.setopt(pycurl.COOKIEFILE, COOKIE_FILE)
                curl.setopt(pycurl.COOKIEJAR, COOKIE_FILE)
                curl.setopt(pycurl.USERAGENT, USER_AGENT)
                curl.setopt(pycurl.URL, url)
                for k, v in opts:
                    curl.setopt(k, v)
                curl.perform()
                done_request = True
            except pycurl.error as e:
                print(f'pycurl error {e}')
                time.sleep(1)
            if done_request: break

        # Forces cookies to be flushed to COOKIE_FILE, I hope.
        del curl

        self.referer = url
        self.byte_content = storage.getvalue()
        try:
            self.content = storage.getvalue().decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            self.content = ''

        if cookies_db:
            c = cookies_db.cursor()
            for line in open(COOKIE_FILE).readlines():
                if line.startswith('#'): continue
                tokens = line.split()
                if len(tokens) == 7:
                    host = tokens[0]
                    path = tokens[2]
                    expiry = int(tokens[4])
                    name = tokens[5]
                    value = tokens[6]
                    c.execute('''
                    INSERT INTO moz_cookies (baseDomain, host, path, name, value, expiry)
                    VALUES ('neopets.com', ?, ?, ?, ?, ?)
                    ON CONFLICT (name, host, path, originAttributes)
                    DO UPDATE SET value=?, expiry=?
                    ''', (host, path, name, value, expiry
                        , value, expiry))
            cookies_db.commit()

        if type(self.content) == str:
            if 'templateLoginPopupIntercept' in self.content:
                print('Warning: Not logged in?')
            if 'randomEventDiv' in self.content:
                event = self.search(r'<div class="copy">(.*?)\t</div>')
                if event:
                    event = util.strip_tags(event[1])
                    print(f'[Random event: {event}]')
                else:
                    print('[Random event]')

    def make_arg_string(self, params, kwargs, quoter):
        arg_string_parts = []
        for p in params:
            k, v = p.split('=')
            arg_string_parts.append(f'{k}={quoter(v)}')
        if kwargs:
            arg_string_parts.append(urlencode(kwargs))
        return '&'.join(arg_string_parts)

    def get_base(self, url, *params, **kwargs):
        if params or kwargs:
            if '?' not in url:
                url += '&' if '?' in url else '?'
            url += self.make_arg_string(params, kwargs, quote_plus)
        self.perform(url, [(pycurl.POST, 0)])

    def save_page(self, url, tag):
        parts = [x for x in url.split('/') if x]
        if not parts: parts = ['_']
        path_parts, filename = parts[:-1], parts[-1]
        path = '/'.join(['pages'] + path_parts)
        os.makedirs(path, exist_ok=True)
        time_ms = int(time.time() * 1000)
        self.last_file_path = f'{path}/{filename}_{tag}@{time_ms}'
        if self.save_pages:
            self.save_to_file(self.last_file_path)

    def get_url(self, url, *params, **kwargs):
        self.get_base(url, *params, **kwargs)
        self.save_page(url, 'get_url')

    def get(self, path, *params, **kwargs):
        self.get_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'get')

    def post_base(self, url, *params, **kwargs):
        postfields = self.make_arg_string(params, kwargs, quote)
        self.perform(url, [(pycurl.POST, 1), (pycurl.POSTFIELDS, postfields)])

    def post_url(self, url, *params, **kwargs):
        self.post_base(url, *params, **kwargs)
        self.save_page(url, 'post_url')

    def post(self, path, *params, **kwargs):
        self.post_base(self.base_url + path, *params, **kwargs)
        self.save_page(path, 'post')

    def find(self, *strings):
        loc = 0
        for string in strings:
            loc = self.content.find(string, loc)
        return loc

    def contains(self, string):
        return self.driver.find_element(By.ID, string) 
    
    def search(self, regex):
        r = re.compile(regex, re.DOTALL)
        result = r.search(self.content)
        if not result:
            print(f'Warning: Search {regex} failed for page {self.last_file_path}')
        return result
    
    def findall(self, regex):
        r = re.compile(regex, re.DOTALL)
        return r.findall(self.content)

    def active_pet_name(self):
        return self.driver.find_element(By.CLASS_NAME, "profile-dropdown-link").text

    def current_np(self):
        return self.driver.find_element(By.ID, 'npanchor').text    

    def set_referer_path(self, path):
        self.referer = self.base_url + path

    def set_referer(self, url):
        self.referer = url
    
    def login(self, user, pwd):
        self.post('/login.phtml', f'username={user}', f'password={pwd}')

#!/usr/bin/env python

from __future__ import print_function

import os, sys

sys.path.insert(0, '/mnt/sda3/PROJECTS/configset')

import requests

from bs4 import BeautifulSoup as bs
from make_colors import make_colors
from pydebugger.debug import debug
from configset import configset
import configset as configme
import progressbar
import traceback
import time
import re
import math
import inspect
from pprint import pprint
try:
    from pause import pause
except:
    def pause(*args, **kwargs):
        return None
from unidecode import unidecode
import psutil
import clipboard
import argparse
import get_version
import json, ast

if sys.version_info.major == 3:
    raw_input = input
    from urllib.parse import unquote, quote
else:
    from urllib import unquote, quote

def convert_size(size_bytes):
    if (size_bytes == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])

class TorrentDownloads(object):

    PID = os.getpid()

    if 'linux' in sys.platform:
        MEM = convert_size(psutil.Process(int(PID)).memory_info().shared)
    elif 'win32' in sys.platform:
        MEM = convert_size(psutil.Process(int(PID)).memory_info().private)
    else:
        MEM = psutil.Process(int(PID)).memory_info()

    CONFIG = configset()

    URL = CONFIG.get_config('setting', 'url', "https://www.torrentdownloads.pro") # don't use slash end of !
    SESS = requests.Session()

    prefix = '{variables.task} >> {variables.subtask} '
    variables =  {'task': '--', 'subtask': '--'}

    BAR = progressbar.ProgressBar(prefix = prefix, variables = variables, max_value = 100, max_error = False)
    MAX_ERROR = CONFIG.get_config('error', 'max_try', '10')
    FEATURES = 'html.parser'

    HEADERS = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate',
            'sec-ch-ua-platform': "Linux",
                'sec-fetch-mode': 'navigate',
                'upgrade-insecure-requests': '1',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

    SESS.headers.update(HEADERS)

    def __init__(self, url = None):
        self.URL = url or self.URL

    @classmethod
    def get_width(self):
        try:
            import click
            return click.terminal_size()[0]
        except:
            import cmdw
            return cmdw.getWidth()

    @classmethod
    def valid(self, soup, func, args, severity = 'info'):
        debug(args = args)
        if isinstance(args, str):
            args = (args, {})
        else:
            if len(args) == 1:
                args = (args[0], {})

        n_try = 0
        debug(args = args)
        debug(func = func)
        try:
            data = getattr(soup, func)(*args)
            if not data:
                # print(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to get:", 'lr') + " " + make_colors("`" + " ".join([str(i) for i in args]) + "`", 'ly'))
                # sys.exit(0)
                if severity == 'debug':
                    raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to get:", 'lr') + " " + make_colors("`" + " ".join([str(i) for i in args]) + "`", 'ly'))
                else: return False
            debug(data = data)
            return data
        except Exception as e:
            debug(inspect_stack = inspect.stack())
            # print(make_colors("error:", 'lw', 'r') + " " + make_colors(e, 'ly'))
            if os.getenv('TRACEBACK'):
                print(make_colors("error full:", 'lw', 'r') + " " + make_colors(str(traceback.format_exc()), 'ly'))
            # sys.exit()
            if severity == 'debug':
                raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors(str(e), 'ly'))
            else: return False

    @classmethod
    def connect(self, url = None, method='get', n_try = 10, encoding = False, **kwargs):
        n_try = self.MAX_ERROR or n_try
        url = url or self.URL
        debug(url = url)
        req = False
        n = 0
        while 1:
            try:
                # content = self.SESS.get(self.URL).content
                req = getattr(self.SESS, method)(url, **kwargs)
                # if encoding:
                req.encoding = req.apparent_encoding
                break
            except Exception as e:
                task = make_colors("error", 'lw', 'r')
                subtask = make_colors(e, 'ly') + " "
                debug(n_try = n_try)
                debug(n = n)
                if not n == n_try:
                    n+=1
                    self.BAR.update(n, task = task, subtask = subtask)
                    time.sleep(1)
                else:
                    self.BAR.finish()
                    print(make_colors("error:", 'lw', 'r') + " " + make_colors(e, 'ly'))
                    sys.exit(make_colors(traceback.format_exc(), 'r', 'lw'))
        self.BAR.finish()
        return req

    @classmethod
    def write(self, name, content):
        if os.getenv('DEBUG') or os.getenv('DEBUG_SERVER') or os.getenv('DEBUGGER_SERVER'):
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), name + '.html'), 'w') as cf:
                if hasattr(content, 'decode'):
                    try:
                        cf.write(content.decode('utf-8', errors = 'replace'))
                    except:
                        pass
                else:
                    try:
                        cf.write(content)
                    except:
                        try:
                            cf.write(unidecode(content))
                        except:
                            pass

    @classmethod
    def makeList(self, alist, ncols, vertically=True, file=None):
        debug(alist = alist)
        # pause()
        from distutils.version import StrictVersion  # pep 386
        import prettytable as ptt  # pip install prettytable
        assert StrictVersion(ptt.__version__) >= StrictVersion(
            '0.7')  # for PrettyTable.vrules property
        #debug(len_L = len(alist))
        #debug(ncols = ncols)
        L = alist
        nrows = - ((-len(L)) // ncols)
        ncols = - ((-len(L)) // nrows)
        t = ptt.PrettyTable([str(x) for x in range(ncols)])
        t.header = False
        t.align = 'l'
        t.hrules = ptt.NONE
        t.vrules = ptt.NONE
        r = nrows if vertically else ncols
        chunks = [L[i:i + r] for i in range(0, len(L), r)]
        chunks[-1].extend('' for i in range(r - len(chunks[-1])))
        if vertically:
            chunks = zip(*chunks)
        for c in chunks:
            t.add_row(c)
        print(make_colors(t, 'green'))

    @classmethod
    def home(self, content = ''):
        debug(len_content = len(content))
        title, _title, title_url, title_rss = '', '', '', ''
        is_search = False
        if content:
            is_search = True
        debug(is_search = is_search)
        data = []
        data_list = []
        page = ""
        debug(self_URL = self.URL)
        content = content or self.connect(timeout=10, headers = self.HEADERS).content
        self.write('result', content)
        # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'result.html'), 'r') as cf:
        # 	content = cf.read()

        if not content:
            print(make_colors("Failed to get data !", 'lw', 'r'))
            sys.exit()

        b = bs(content, features=self.FEATURES)

        left_cards = self.valid(b, 'find_all', ('div', {'class':'inner_container'}))
        debug(left_cards = left_cards)
        if not left_cards:
            print(make_colors("No Home", 'lw', 'r') + " " + make_colors("maybe connection error !", 'b', 'y'))
            return [], [], page
        self.write('left_cards', "\n".join([str(x) for x in left_cards]))

        for i in left_cards:
            add = {}
            if not is_search:
                title = self.valid(i, 'find', ('h1', {'class':'movies'}))
                _title = self.valid(title, 'find', ('img')).get('alt').replace(' icon', '')
                debug(title = _title)

                title_url = self.valid(title, 'find', ('a')).get('href')
                debug(title_url = title_url)

                title_rss = self.valid(title, 'find', ('a', {'title':re.compile('RSS')})).get('href')
                debug(title_rss = title_rss)

            else:
                title = self.valid(i, 'find', ('h1', {'class':'titl_3'}))
                debug(title = title)
                # pause()
                if title:
                    title = title.text
                    _title = title
                    debug(title = title)
                    debug(_title = _title)
                    # pause()
                else:
                    title = self.valid(i, 'find', ('div', {'class':'title_bar1'}))
                    if title:
                        title = self.valid(title, 'find', ('h1'))
                        if title:
                            title = self.valid(title, 'find', 'img')
                            if title: title = title.text
                # pause()

            add.update({'title':_title, 'title_url': title_url, 'title_rss': title_rss})

            self.write('left_card', str(i))

            grey_bar3 = self.valid(i, 'find_all', ('div', {'class':(re.compile('grey_bar3'))}))
            debug(grey_bar3 = grey_bar3)

            self.write('grey_bar3', "\n".join([str(x) for x in grey_bar3]))

            greys = []

            if not is_search:
                grey_bar3 = grey_bar3[1:]
            else:
                grey_bar3 = grey_bar3[4:]

            for grey in grey_bar3:
                if len(grey.text) > 10 and not grey.text == "No torrents":
                    debug(grey = grey)
                    leech, seed, size = '', '', ''
                    name, link, link2 = '', '', ''
                    grey_data = {}
                    debug(grey = grey)
                    p = self.valid(grey, 'find', ('p'))
                    debug(p = p)
                    # pause()
                    info = self.valid(grey, 'find', ('a', {'title': re.compile('View torrent info')}))
                    link2 = self.valid(grey, 'find', ('a', {'class':'cloud'}))
                    debug(link2 = link2)
                    leech_info = self.valid(grey, 'find_all', ('span'))
                    debug(leech_info = leech_info)
                    # pause()

                    check = False

                    if leech_info: check = self.valid(leech_info[0], 'find', ('b'))
                    debug(check = check)
                    if not check:
                        debug(leech_info = leech_info)
                        leech = leech_info[1].text
                        seed = leech_info[2].text
                        size = leech_info[3].text.encode('ascii', errors='ignore')
                        # if not is_search:
                        # 	size = leech_info[3].text.encode('ascii', errors='ignore')
                        # else:
                        # 	if not list(filter(lambda k: k in leech_info[2].text.encode('ascii', errors='ignore').lower(), [' gb', ' mb', " kb"])):
                        # 		size = leech_info[3].text.encode('ascii', errors='ignore')
                        # 	else:
                        # 		try:
                        # 			size = leech_info[2].text.encode('ascii', errors='ignore')
                        # 		except:
                        # 			size = leech_info[3].text.encode('ascii', errors='ignore')

                        debug(leech = leech)
                        debug(seed = seed)
                        debug(size = size)
                        debug(info = info)
                        # pause()

                        if info:
                            name = info.text
                            debug(name = name)
                            link = info.get('href')
                            debug(link = link)
                        # pause()
                        # if not info:
                        # 	debug(grey = grey)
                        # 	info = self.valid(grey, 'find', 'img', {'src':'/templates/new/images/movie_icon.jpg'})
                        # 	debug(info = info)
                        # 	if info:
                        # 		info = self.valid(info, 'find', 'a')
                        # 		debug(info = info)
                        # 		if info:
                        # 			name = info.text
                        # 			debug(name = name)
                        # 			link = info.get('href')
                        # 			debug(link = link)
                        # # pause()
                        debug(link2 = link2)
                        if link2:
                            link2 = link2.get('href')
                            debug(link2 = link2)
                        debug(p = p)
                        # pause()
                        grey_data.update(
                            {
                                'name': name,
                                                        'link': link,
                                                            'link2': link2,
                                                                'leech': leech,
                                                                'seed': seed,
                                                                'size': size
                            })
                        greys.append(grey_data)
                        data_list.append(grey_data)
            if greys:
                add.update({'data': greys})
                data.append(add)

        if os.getenv('DEBUG') or os.getenv('DEBUG_SERVER') or os.getenv('DEBUGGER_SERVER'):
            pprint(data)
        return data, data_list, page

    @classmethod
    def create_list(self, data, n=1, color = 'yellow', len_data = 100):
        result_search_list = []
        if not data:
            return result_search_list
        for i in data:
            debug(i = i)
            result_search_list.append(str(str(n).zfill(len(str(len_data)))) + ". " + make_colors(i.get('name'), color) +
                                      make_colors(" [", 'red') +
                                      make_colors("{0}".format(i.get('size').strip()), 'white', 'on_red') +
                                                  "|" +
                                                                                make_colors("{0}".format(i.get('leech')), 'black', 'on_yellow') +
                                                                                "|" +
                                                                                make_colors("{0}".format(i.get('seed')), 'black', 'on_cyan') +
                                                                                make_colors("]", 'red'))  #.format(
            n += 1
        return result_search_list, n

    @classmethod
    def search(self, query, category = None):
        data_result, page = [], []

        debug(query = query)
        content = self.connect(self.URL + '/search/', params = {'search':query}).content
        self.write('search', content)

        data_result, data_result_list, page = self.home(content)

        return data_result, data_result_list, page

    @classmethod
    def detail(self, url):
        debug(url = url)
        magnet, hash_secret, category, name, added, last_update_date, update_link, alternative, trackers, file_list = '', '', '', '', '', '', '', '', [], []
        content = self.connect(url, timeout=10, headers = self.HEADERS).content
        b = bs(content, 'lxml')
        self.write('detail', content)
        left_container = self.valid(b, 'find', ('div', {'class':'left_container'}))
        if not left_container:
            return {}
        torrent_download_box = self.valid(left_container, 'find', ('div', {'class':'torrent_download_box'}))

        category_data = self.valid(torrent_download_box, 'find_all', ('a'))

        category = category_data[1].text
        debug(category = category)
        name = category_data[2].text
        debug(name = name)

        inner_container = self.valid(left_container, 'find', ('div', {'class':'inner_container'}))
        debug(inner_container = inner_container)
        self.write('inner_container', str(inner_container))
        itorrent = self.valid(inner_container, 'find', ('a', {'rel':'nofollow', 'href':re.compile('itorrents.org/')}))
        if itorrent: itorrent = itorrent.get('href')
        debug(itorrent = itorrent)
        grey_bar1 = self.valid(inner_container, 'find_all', ('div', {'class':'grey_bar1'}))
        grey_bar2 = self.valid(inner_container, 'find_all', ('div', {'class':re.compile('grey_bar2')}))
        debug(grey_bar1 = grey_bar1)
        self.write('grey_bar1', "\n".join([str(x) for x in grey_bar1]))
        if not grey_bar1:
            print(make_colors("No Data Details !", 'lw', 'r'))
            return {}
        hash_data = self.valid(grey_bar1[1], 'find', ('p'), 'debug')
        debug(hash_data = hash_data)
        if hash_data:
            hash_secret = re.split("Infohash:", hash_data.text, re.I)[1].strip()
        debug(hash_secret = hash_secret)

        magnet_data = self.valid(grey_bar1[3], 'find', ('p'), 'debug')

        if magnet_data:
            magnet = self.valid(magnet_data, 'find', ('a'))
            if magnet: magnet = magnet.get('href')
        debug(magnet = magnet)

        added_data = self.valid(grey_bar1[6], 'find', 'p')
        debug(added_data = added_data)
        if added_data:
            added = re.split("Torrent added:", added_data.text, re.I)[1].strip()


        for t in grey_bar2:
            debug(t = t)
            tracker = self.valid(t, 'find', 'a', {'text': re.compile('udp://|tracker')})
            debug(tracker = tracker)
            if tracker:
                trackers.append(tracker.text)
        debug(trackers = trackers)

        for t in grey_bar2:
            if self.valid(t, 'find', ('p', {'class':'sub_file'})):
                file_list_parent = self.valid(t, 'find', ('p', {'class':'sub_file'})).parent.parent
                debug(file_list_parent = file_list_parent)
                # pause()
                file_list_data = self.valid(file_list_parent, 'find_all', ('div', {'class':'grey_bar2'}))
                debug(file_list_data = file_list_data)
                # pause()
                for f in file_list_data:
                    debug(f = f)
                    file_list_add = {}
                    file_list_name = self.valid(f, 'find', ('p', {'class':'sub_file'}))
                    debug(file_list_name = file_list_name)
                    if file_list_name: file_list_name = file_list_name.text.encode('ascii', errors='ignore')
                    debug(file_list_name = file_list_name)
                    file_list_size = self.valid(f, 'find', ('span', {'class':'size'}))
                    debug(file_list_size = file_list_size)
                    if file_list_size: file_list_size = file_list_size.text.encode('ascii', errors='ignore')
                    debug(file_list_size = file_list_size)
                    file_list_add.update({file_list_name: file_list_size})
                    file_list.append(file_list_add)
                debug(file_list = file_list)
                break
        # pause()

        grey_bara1 = self.valid(inner_container, 'find_all', ('div', {'class':'grey_bara1 back_none'}))
        debug(grey_bara1 = grey_bara1)
        last_update_data = self.valid(grey_bara1[1], 'find', 'p')
        if last_update_data:
            last_update_date = re.findall("\d{0,4}-\d{0,2}-\d{0,2} \d{0,2}:\d{0,2}:\d{0,2}", last_update_data.text)
            if last_update_date:
                last_update_date = last_update_date[0]
            debug(last_update_date = last_update_date)
            update_link = self.valid(last_update_data, 'find', ('a'))
            if update_link: update_link = update_link.get('href')
            debug(update_link = update_link)

        alternative_data = self.valid(grey_bara1[2], 'find', 'p')
        debug(alternative_data = alternative_data)
        if alternative_data:
            alternative = self.valid(alternative_data, 'find', 'a').get('href')
            debug(alternative = alternative)


        debug(grey_bara1 = grey_bara1)
        self.write("grey_bara1", "\n".join([str(x) for x in grey_bara1]))

        debug(magnet = magnet)
        debug(hash_secret = hash_secret)
        debug(category = category)
        debug(name = name)
        debug(added = added)
        debug(last_update_date = last_update_date)
        debug(update_link = update_link)
        debug(alternative = alternative)
        debug(trackers = trackers)
        debug(itorrent = itorrent)

        return {
            'magnet': magnet, 'hash': hash_secret, 'category': category, 'name': name, 'added': added, 'last_update_date': last_update_date, 'update_link': update_link, 'alternative': alternative, 'trackers': trackers, 'files': file_list, 'itorrent': itorrent
        }

    @classmethod
    def navigator(self, query_search = None, stype = None, url_query = None, downloadPath = ".", overwrite = None, home = False, nlist = 3, page_return = None, proxies=None):
        q = None
        data_result, data_result_list, page = [], [], []
        if self.get_width() < 115 and nlist == 3:
            nlist = 1
        n = 1
        if proxies and isinstance(proxies, dict):
            if proxies.get('http') or proxies.get('https'):
                self.SESS.update({'proxies': proxies})
        if downloadPath == ".": downloadPath = os.getcwd()
        if not home:
            if not stype:
                stype = 'all'
        if query_search:
            data_result, data_result_list, page = self.search(query_search, stype)
            debug(data_result1 = data_result)
            debug(page = page)
        else:
            data_result, data_result_list, page = self.home()

        colors = ['ly', 'lc', 'lg', 'white', 'blue', 'lm', 'lg', 'lr']
        for i in data_result:
            data_list, n = self.create_list(i.get('data'), n, colors[data_result.index(i)])
            print(make_colors(i.get('title'), 'b', colors[data_result.index(i)]))
            self.makeList(data_list, nlist)

        qnote = "[" + make_colors(str(self.PID), 'b', 'lc') + ":" + make_colors(str(self.MEM), 'b', 'ly') + "] " + make_colors("Select N[n]umber to Download", 'lg') + " [" + make_colors('[m]n[m] = get magnet then copy to clipboard', 'ly') + ", " + make_colors('s = search', 'lg') + ", " + make_colors('[N]n[N] = length list, default = 3', 'lm') + ", " + make_colors('h = back to home page', 'lc') + ", " + make_colors("[q]uit | e[x]it", 'lr') + "]: "
        q = raw_input(qnote)
        while 1:
            if not q:
                print("\b")
            else:
                break
        if q: q = q.strip()
        if q.isdigit():
            if int(q) <= len(data_result_list) + 1:
                url = self.URL + data_result_list[int(q) - 1].get('link')
                debug(url = url)
                # print(make_colors("URL: " + url, 'ly'))
                data_details = self.detail(url)
                debug(magnet = data_details.get('magnet'))
                debug(itorrent = data_details.get('itorrent'))
                if data_details.get('itorrent'):
                    download_path = self.CONFIG.get_config('download', 'path') or os.path.join(os.path.dirname(os.path.realpath(__file__)), 'downloads')
                    if not os.path.isdir(download_path):
                        try:
                            os.makedirs(download_path)
                        except Exception as e:
                            if os.getenv('TRACEBACK'):
                                print(make_colors("ERROR:", 'lw', 'r'))
                                print(make_colors(traceback.format_exc(), 'ly'))
                            else:
                                print(make_colors("ERROR:", 'lw', 'r'))
                                print(make_colors(str(e), 'lc'))

                    with open(os.path.join(download_path, name + '.torrent'), 'w') as cf:
                        for chunk in self.SESS.get(itorrent, stream = True, headers = self.HEADERS):
                            cf.write(chunk)
        elif q[-1] == 'm' and q[:-1].isdigit():
            url = self.URL + data_result_list[int(q[:-1]) - 1].get('link')
            debug(url = url)
            # clipboard.copy(url)
            # pause()
            # print(make_colors("URL: " + url, 'ly'))
            data_details = self.detail(url)
            debug(magnet = data_details.get('magnet'))
            debug(itorrent = data_details.get('itorrent'))
            if data_details.get('magnet'):
                clipboard.copy(data_details.get('magnet'))
        elif q[0] == 'm' and q[1:].isdigit():
            url = self.URL + data_result_list[int(q[1:]) - 1].get('link')
            debug(url = url)
            # print(make_colors("URL: " + url, 'ly'))
            data_details = self.detail(url)
            debug(magnet = data_details.get('magnet'))
            debug(itorrent = data_details.get('itorrent'))
            if data_details.get('magnet'):
                clipboard.copy(data_details.get('magnet'))
        elif q[-1] == 'm' and q[:-1].isdigit():
            nlist = int(q[:-1])
            return self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
        elif q[0] == 'm' and q[1:].isdigit():
            nlist = int(q[1:])
            return self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
        elif q == 's':
            qs = raw_input(make_colors("search:", 'ly') + " ")
            if qs:
                return self.navigator(qs)
        elif q.lower() in ('q', 'quit', 'exit', 'x'):
            sys.exit(make_colors('System Exit ....', 'b', 'ly'))
        elif  q.lower() == 'h':
            self.navigator(proxies = proxies, nlist = nlist, downloadPath = downloadPath, home = home)
            #return self.navigator(query_search, stype,
                                  #url_query,
                                 #downloadPath,
                                 #overwrite,
                                 #home,
                                 #nlist,
                                 #page_return,
                                 #proxies)
        else:
            if q: query_search = q
            return self.navigator(query_search, downloadPath = downloadPath, overwrite = overwrite, nlist = nlist, page_return = page_return, proxies = proxies)
        return q

    @classmethod
    def run(self, query_search = None, stype = None, url_query = None, downloadPath = ".", overwrite = None, home = False, nlist = 3, page_return = None, proxies = None):
        q = self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
        if q:
            if q.lower() in ('exit', 'quit', 'x', 'q'):
                sys.exit()
        return self.run(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)

    @classmethod
    def usage(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--search', action = 'store', help = 'Direct Search for')
        parser.add_argument('-n', '--nlist', action = 'store', help = 'Show with list length', type = int)
        parser.add_argument('-d', '--download-path', action = 'store', help = 'Save download to dir')
        parser.add_argument('-x', '--proxies', action = 'store', help = 'use proxies, format: {"http":http://"host:ip", "https":https://"host:ip"}')
        parser.add_argument('-v', '--version', action = 'store_true', help = 'Show this app version number')
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            if args.version:
                print(make_colors("VERSION:", 'ly') + " " + make_colors(get_version.get(), 'b', 'lc'))
                sys.exit()
            proxies = {}
            if args.proxies:
                try:
                    proxies = json.loads(args.proxies)
                except:
                    proxies = ast.literal_eval(args.proxies)
            if proxies:
                if not isinstance(args.proxies, dict): proxies = {}

            self.run(args.search, nlist = args.nlist, downloadPath = args.download_path, proxies = args.proxies)

def usage():
    return TorrentDownloads.usage()

if __name__ == '__main__':

    TorrentDownloads.usage()
    # TorrentDownloads.home()
    # TorrentDownloads.navigator()
    # TorrentDownloads.run()
    # url = "https://www.torrentdownloads.pro/torrent/1703817039/Mona-Lisa-And-The-Blood-Moon-%282021%29-%5B720p%5D-%5BWEBRip%5D-%5BYTS-MX%5D"
    # url1 = "https://www.torrentdownloads.pro/torrent/1703815335/The-Munsters-%282022%29-%5B720p%5D-%5BBluRay%5D-%5BYTS-MX%5D"
    # data = TorrentDownloads.detail(url)
    # pprint(data)
    # TorrentDownloads.search('House of dragon S01E05')

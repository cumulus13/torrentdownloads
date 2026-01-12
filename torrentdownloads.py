#!/usr/bin/env python3

# File: torrentdownloads.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-24
# Description: Torrent Search and Magnet downloader 
# License: MIT

from __future__ import print_function

import os, sys
import traceback

exceptions = ['pika', 'kafka', 'zmq', 'urllib4', 'requests', 'chardet', 'idna', 'httpcore', 'httpx', 'hpack', 'hyperframe', 'websockets', 'aiohttp', 'aiokafka', 'pika', 'pydantic', 'fastapi', 'uvicorn']
LOG_LEVEL = "NO"
SHOW_LOG = False
tprint = None  # type: ignore

if len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv):
    print("🐞 Debug mode enabled")
    os.environ["DEBUG"] = "1"
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    LOG_LEVEL = "DEBUG"
    SHOW_LOG = True
else:
    os.environ['NO_LOGGING'] = "1"

try:
    from richcolorlog import setup_logging, print_exception as tprint  # type: ignore
    setup_logging(exceptions = exceptions) 
    logger = setup_logging(__name__, level=LOG_LEVEL, exceptions=exceptions, show=SHOW_LOG)  # type: ignore
except:
    import logging
    logging.basicConfig(  # type: ignore
        level=getattr(logging, LOG_LEVEL, "DEBUG"),  # type: ignore
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    for i in exceptions:
        logging.getLogger(i).setLevel(1000)

    logger = logging.getLogger(__name__)

if not tprint:
    def tprint(*args, **kwargs):
        traceback.print_exc(*args, **kwargs)

import argparse
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawTextHelpFormatter
# import ctraceback
# sys.excepthook = ctraceback.CTraceback

# if 'linux' in sys.platform:
    # sys.path.insert(0, '/mnt/sda3/PROJECTS/configset')

# import requests
from progress_session import ProgressSession  # type: ignore

from bs4 import BeautifulSoup as bs
from make_colors import make_colors  # type: ignore
# if any('debug' in i.lower() for i in  os.environ):
from pydebugger.debug import debug
# else:
    # def debug(*args, **kwargs):
        # return
from configset import configset
#import configset as configme
# import progressbar
# import traceback
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
import get_version
import json, ast

from rich import traceback as rich_traceback
from rich.console import Console
# console = console.Console()
console = Console(width=os.get_terminal_size().columns)  # type: ignore

# from rich.progress import Progress, SpinnerColumn, TextColumn#, BarColumn, DownloadColumn, TransferSpeedColumn, TaskID
import shutil
rich_traceback.install(theme = 'fruity', max_frames = 30, width = shutil.get_terminal_size()[0])

if sys.version_info.major == 3:
    raw_input = input
    # from urllib.parse import unquote, quote
# else:
#     from urllib import unquote, quote

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
        MEM = convert_size(psutil.Process(int(PID)).memory_info().shared)  # type: ignore
    elif 'win32' in sys.platform:
        MEM = convert_size(psutil.Process(int(PID)).memory_info().private)
    else:
        MEM = psutil.Process(int(PID)).memory_info()

    CONFIG = configset()

    URL = CONFIG.get_config('setting', 'url', "https://www.torrentdownloads.pro") # don't use slash end of !  # type: ignore
    # SESS = requests.Session()
    SESS = ProgressSession()

    prefix = '{variables.task} >> {variables.subtask} '
    variables =  {'task': '--', 'subtask': '--'}

    # BAR = progressbar.ProgressBar(prefix = prefix, variables = variables, max_value = 100, max_error = False)
    # BAR = Progress(
    #         SpinnerColumn(),
    #         TextColumn("[progress.description]{task.description}"),
    #         console=console
    #     )
    MAX_ERROR = CONFIG.get_config('error', 'max_try', '10')  # type: ignore
    FEATURES = CONFIG.get_config('bs', 'features') or 'html.parser'  # type: ignore

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
    def get_width(self):  # type: ignore
        try:
            import click
            return click.terminal_size()[0]  # type: ignore
        except:
            import cmdw
            return cmdw.getWidth()

    @classmethod
    def valid(self, soup, func, args, severity = 'info'):  # type: ignore
        debug(args = args)
        if isinstance(args, str):
            args = (args, {})
        else:
            if len(args) == 1:
                args = (args[0], {})

        # n_try = 0
        debug(args = args)
        debug(func = func)
        try:
            data = getattr(soup, func)(*args)
            debug(data = data)
            if not data:
                # print(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to get:", 'lr') + " " + make_colors("`" + " ".join([str(i) for i in args]) + "`", 'ly'))
                # sys.exit(0)
                if severity == 'debug':
                    raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to get:", 'lr') + " " + make_colors("`" + " ".join([str(i) for i in args]) + "`", 'ly'))
                else: return False
            debug(data = data)
            return data
        except Exception as e:
            # ctraceback.CTraceback(*sys.exc_info())
            debug(inspect_stack = inspect.stack())
            if str(os.getenv('TRACEBACK', '0')).lower() in ['1', 'true', 'yes', 'ok']:
                # print(make_colors("error full:", 'lw', 'r') + " " + make_colors(str(traceback.format_exc()), 'ly'))
                tprint(e)
            elif severity == 'debug':
                raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors(str(e), 'ly'))
            else:
                print(make_colors("error [validation]:", 'lw', 'r') + " " + make_colors(e, 'ly'))
                return False

    @classmethod
    def connect(self, url = None, method='get', n_try = 10, encoding = False, **kwargs):  # type: ignore
        n_try = self.MAX_ERROR or n_try
        url = url or self.URL
        debug(url = url)
        req = False
        n = 0
        
        # with Progress(
        #     SpinnerColumn(),
        #     TextColumn("[progress.description]{task.description}"),
        #     console=console
        # ) as progress:
        #     task = progress.add_task("Connect ...", total=None)
        #     progress.update(task, description=f"Connect ...")
        while 1:
            try:
                # content = self.SESS.get(self.URL).content
                req = getattr(self.SESS, method)(url, **kwargs)
                # if encoding:
                req.encoding = req.apparent_encoding
                break
            except Exception as e:
                # ctraceback.CTraceback(*sys.exc_info(), print_it = False)
                tprint(e)
                # task = make_colors("error", 'lw', 'r')
                # subtask = make_colors(e, 'ly') + " "
                # task = progress.add_task(f"error: [white on red]{e}[/]. [#FFFF00]re-connecting...[/]", total = None)
                # progress.update(task, description=task)
                debug(n_try = n_try)
                debug(n = n)
                if not n == n_try:
                    n+=1
                    # task = progress.add_task(f"error: [white on red]{e}[/]. [#FFFF00]re-connecting...[/] [#00FFFF]({n}/{n_try})[/]", total = None)
                    # progress.update(task, description=task)
                    # self.BAR.update(n, task = task, subtask = subtask)
                    time.sleep(1)
                else:
                    # task = progress.add_task(f"error: [white on red]{e}[/]. [#FFFF00]re-connecting...[/] [#FF0000]failed after {n_try} tries![/]", total = None)
                    # progress.update(task, description=f"error: [white on red]{e}[/]. [#FFFF00]re-connecting...[/] [#FF0000]failed after {n_try} tries![/]")
                    # progress.stop()
                    # self.BAR.finish()
                    # print(make_colors("error:", 'lw', 'r') + " " + make_colors(e, 'ly'))
                    # sys.exit(make_colors(traceback.format_exc(), 'r', 'lw'))
                    raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors(e, 'ly'))
        # self.BAR.finish()
        debug(req = req)
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('connect_req_result', req.content)  # type: ignore
        if not req or not req.status_code == 200:
            # task = progress.add_task(f"error: [white on red]Failed to connect to {url}[/]. [#FF0000]status code: {req.status_code if req else 'None'}[/]", total = None)
            # progress.update(task, description=task)
            # progress.stop()
            # print(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to connect to " + url, 'ly') + " " + make_colors("status code: " + str(req.status_code) if req else 'None', 'b', 'r'))
            raise Exception(make_colors("error:", 'lw', 'r') + " " + make_colors("Failed to connect to " + url, 'ly') + " " + make_colors("status code: " + str(req.status_code) if req else 'None', 'b', 'r'))
        return req

    @classmethod
    def write(self, name, content):
        if os.getenv('DEBUG') or os.getenv('DEBUG_SERVER') or os.getenv('DEBUGGER_SERVER') or os.getenv('VERBOSE') == '1':
            file_out = os.path.join(os.path.dirname(os.path.realpath(__file__)), name + '.html')
            debug(file_out = file_out)
            with open(file_out, 'wb') as cf:
                # if hasattr(content, 'decode'):
                try:
                    cf.write(content)
                except:
                    # ctraceback.CTraceback(*sys.exc_info())
                    try:
                        cf.write(bytes(content, encoding='utf-8', errors = 'replace'))
                    except Exception as e:
                        # ctraceback.CTraceback(*sys.exc_info())
                        tprint(e)
                # else:
                #     try:
                #         cf.write(content)
                #     except:
                #         ctraceback.CTraceback(*sys.exc_info())
                #         try:
                #             cf.write(unidecode(content))
                #         except:
                #             ctraceback.CTraceback(*sys.exc_info())

    @classmethod
    def makeList(self, alist, ncols, vertically=True, file=None):  # type: ignore
        debug(alist = alist)
        # pause()
        from packaging.version import Version  # Use packaging instead of distutils
        import prettytable as ptt  # pip install prettytable
        assert Version(ptt.__version__) >= Version(
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
    def home(self, content = ''):  # type: ignore
        debug(len_content = len(content))
        title, _title, title_url, title_rss = '', '', '', ''
        is_search = False
        if content: is_search = True
        debug(is_search = is_search)
        data = []
        data_list = []
        page = ""
        debug(self_URL = self.URL)
        content = content or self.connect(timeout=10, headers = self.HEADERS).content
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('result', content)
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
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('left_cards', "\n".join([str(x) for x in left_cards]))

        for i in left_cards:
            add = {}
            if not is_search:
                title = self.valid(i, 'find', ('h1', {'class':'movies'}))
                _title = self.valid(title, 'find', ('img')).get('alt').replace(' icon', '')  # type: ignore
                debug(title = _title)

                title_url = self.valid(title, 'find', ('a')).get('href')  # type: ignore
                debug(title_url = title_url)

                title_rss = self.valid(title, 'find', ('a', {'title':re.compile('RSS')})).get('href')  # type: ignore
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

            if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('left_card', str(i))

            grey_bar3 = self.valid(i, 'find_all', ('div', {'class':(re.compile('grey_bar3'))}))
            debug(grey_bar3 = grey_bar3)
            grey_bar3_0 = grey_bar3
            if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('grey_bar3', "\n".join([str(x) for x in grey_bar3]))  # type: ignore

            greys = []

            debug(is_search = is_search)
            if not is_search:
                grey_bar3 = grey_bar3[1:]  # type: ignore
                debug(grey_bar3 = grey_bar3)
            else:
                grey_bar3 = grey_bar3[4:]  # type: ignore
                debug(grey_bar3 = grey_bar3)
                if len(grey_bar3) == 1 and len(grey_bar3[0].text.strip()) < 1:
                    grey_bar3 = grey_bar3_0[1:]  # type: ignore
                    debug(grey_bar3 = grey_bar3)

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
                        leech = leech_info[1].text if len(leech_info) > 0 else ''  # type: ignore
                        seed = leech_info[2].text if len(leech_info) > 1 else ''  # type: ignore
                        size = leech_info[3].text.encode('ascii', errors='ignore') if len(leech_info) > 2 else '' # type: ignore
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
            debug(greys = greys)
            if greys:
                add.update({'data': greys})
                data.append(add)

        if os.getenv('DEBUG') or os.getenv('DEBUG_SERVER') or os.getenv('DEBUGGER_SERVER'):
            pprint(data)
        return data, data_list, page

    @classmethod
    def create_list(self, data, n=1, color = 'yellow', len_data = 100):  # type: ignore
        result_search_list = []
        if not data:
            return result_search_list
        for i in data:
            debug(i = i)
            result_search_list.append(
                str(str(n).zfill(len(str(len_data)))) + ". " + \
                make_colors(i.get('name'), color) + \
                make_colors(" [", 'red') + \
                make_colors("{0}".format(i.get('size').strip()), 'white', 'on_red') + "|" + \
                make_colors("{0}".format(i.get('leech')), 'black', 'on_yellow') + "|" + \
                make_colors("{0}".format(i.get('seed')), 'black', 'on_cyan') + \
                make_colors("]", 'red')
            )
            
            n += 1
        return result_search_list, n

    @classmethod
    def search(self, query, category = None):  # type: ignore
        data_result, page = [], []

        debug(query = query)
        content = self.connect(self.URL + '/search/', params = {'search':query}).content
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('search', content)

        data_result, data_result_list, page = self.home(content)

        return data_result, data_result_list, page

    @classmethod
    def detail(self, url):  # type: ignore
        debug(url = url)
        magnet, hash_secret, category, name, added, last_update_date, update_link, alternative, trackers, file_list = '', '', '', '', '', '', '', '', [], []
        content = self.connect(url, timeout=10, headers = self.HEADERS).content
        debug(content = content)
        if not content:
            content = self.SESS.get(url).content
            debug(content = content)
            if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write("detail", content)
        b = bs(content, self.FEATURES)
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('detail', content)
        left_container = self.valid(b, 'find', ('div', {'class':'left_container'}))
        debug(left_container = left_container)
        if not left_container: left_container = b.find('div', class_='left_container')
        debug(left_container = left_container)
        if not left_container:
            left_container = b.find('div', {'class':'left_container'})
            debug(left_container = left_container)
            if not left_container:
                return {}
        torrent_download_box = self.valid(left_container, 'find', ('div', {'class':'torrent_download_box'}))

        category_data = self.valid(torrent_download_box, 'find_all', ('a'))

        category = category_data[1].text  # type: ignore
        debug(category = category)
        name = category_data[2].text  # type: ignore
        debug(name = name)

        inner_container = self.valid(left_container, 'find', ('div', {'class':'inner_container'}))
        debug(inner_container = inner_container)
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('inner_container', str(inner_container))
        itorrent = self.valid(inner_container, 'find', ('a', {'rel':'nofollow', 'href':re.compile('itorrents.org/')}))
        if itorrent: itorrent = itorrent.get('href')
        debug(itorrent = itorrent)
        grey_bar1 = self.valid(inner_container, 'find_all', ('div', {'class':'grey_bar1'}))
        grey_bar2 = self.valid(inner_container, 'find_all', ('div', {'class':re.compile('grey_bar2')}))
        debug(grey_bar1 = grey_bar1)
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write('grey_bar1', "\n".join([str(x) for x in grey_bar1]))  # type: ignore
        if not grey_bar1:
            print(make_colors("No Data Details !", 'lw', 'r'))
            return {}
        hash_data = self.valid(grey_bar1[1], 'find', ('p'), 'debug')
        debug(hash_data = hash_data)
        if hash_data:
            hash_secret = re.split("Infohash:", hash_data.text, re.I)[1].strip()
        debug(hash_secret = hash_secret)

        magnet_data = self.valid(grey_bar1[3], 'find', ('p'), 'debug')
        
        debug(magnet_data = magnet_data)

        if magnet_data:
            magnet = self.valid(magnet_data, 'find', ('a'))
            if magnet:
                magnet = magnet.get('href')
                print(f"magnet: {magnet}")
        debug(magnet = magnet)

        added_data = self.valid(grey_bar1[6], 'find', 'p')
        debug(added_data = added_data)
        if added_data:
            added = re.split("Torrent added:", added_data.text, re.I)[1].strip()


        for t in grey_bar2:  # type: ignore
            debug(t = t)
            tracker = self.valid(t, 'find', 'a', {'text': re.compile('udp://|tracker')})  # type: ignore
            debug(tracker = tracker)
            if tracker:
                trackers.append(tracker.text)
        debug(trackers = trackers)

        for t in grey_bar2:  # type: ignore
            if self.valid(t, 'find', ('p', {'class':'sub_file'})):
                file_list_parent = self.valid(t, 'find', ('p', {'class':'sub_file'})).parent.parent  # type: ignore
                debug(file_list_parent = file_list_parent)
                # pause()
                file_list_data = self.valid(file_list_parent, 'find_all', ('div', {'class':'grey_bar2'}))
                debug(file_list_data = file_list_data)
                # pause()
                for f in file_list_data:  # type: ignore
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
        last_update_data = self.valid(grey_bara1[1], 'find', 'p')  # type: ignore
        if last_update_data:
            last_update_date = re.findall(r"\d{0,4}-\d{0,2}-\d{0,2} \d{0,2}:\d{0,2}:\d{0,2}", last_update_data.text)  # type: ignore
            if last_update_date:
                last_update_date = last_update_date[0]
            debug(last_update_date = last_update_date)
            update_link = self.valid(last_update_data, 'find', ('a'))
            if update_link: update_link = update_link.get('href')
            debug(update_link = update_link)

        alternative_data = self.valid(grey_bara1[2], 'find', 'p')  # type: ignore
        debug(alternative_data = alternative_data)
        if alternative_data:
            alternative = self.valid(alternative_data, 'find', 'a').get('href')  # type: ignore
            debug(alternative = alternative)


        debug(grey_bara1 = grey_bara1)
        if str(os.getenv('DEBUG', '0')).lower() in ['1', 'yes', 'ok', 'true']: self.write("grey_bara1", "\n".join([str(x) for x in grey_bara1]))  # type: ignore

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
    def navigator(self, query_search = None, stype = None, url_query = None, downloadPath = ".", overwrite = None, home = False, nlist = 3, page_return = None, proxies=None):  # type: ignore
        q = None
        data_result, data_result_list, page = [], [], []
        if self.get_width() < 115 and nlist == 3: nlist = 1
        n = 1
        if proxies and isinstance(proxies, dict):
            if proxies.get('http') or proxies.get('https'): self.SESS.update({'proxies': proxies})
        if downloadPath == ".": downloadPath = os.getcwd()
        if not home:
            if not stype: stype = 'all'
        #console.log(f"query_search: {query_search}")
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
        #while 1:
            #if not q:
                #print("\b")
            #else:
                #break
        if q:
            q = q.strip()
            if q.isdigit():
                if int(q) <= len(data_result_list) + 1:
                    url = self.URL + data_result_list[int(q) - 1].get('link')
                    debug(url = url)
                    # print(make_colors("URL: " + url, 'ly'))
                    data_details = self.detail(url)
                    debug(data_details = data_details)
                    debug(magnet = data_details.get('magnet'))
                    debug(itorrent = data_details.get('itorrent'))
                    if data_details.get('itorrent'):
                        download_path = self.CONFIG.get_config('download', 'path') or os.path.join(os.path.dirname(os.path.realpath(__file__)), 'downloads')  # type: ignore
                        if not os.path.isdir(download_path):
                            try:
                                os.makedirs(download_path)
                            except Exception as e:
                                # ctraceback.CTraceback(*sys.exc_info())
                                tprint(e)
                                if os.getenv('TRACEBACK'):
                                    print(make_colors("ERROR:", 'lw', 'r'))
                                    print(make_colors(traceback.format_exc(), 'ly'))
                                else:
                                    print(make_colors("ERROR:", 'lw', 'r'))
                                    print(make_colors(str(e), 'lc'))
    
                        with open(os.path.join(download_path, data_details.get('name') + '.torrent'), 'w') as cf:  # type: ignore
                            for chunk in self.SESS.get(data_details.get('itorrent'), stream = True, headers = self.HEADERS):
                                cf.write(chunk.decode())
            elif q[-1] == 'm' and q[:-1].isdigit():
                url = self.URL + data_result_list[int(q[:-1]) - 1].get('link')
                debug(url = url)
                # clipboard.copy(url)
                # pause()
                # print(make_colors("URL: " + url, 'ly'))
                data_details = self.detail(url)
                debug(data_details = data_details)
                debug(magnet = data_details.get('magnet'))
                debug(itorrent = data_details.get('itorrent'))
                if data_details.get('magnet'): clipboard.copy(data_details.get('magnet'))  # type: ignore
            elif q[0] == 'm' and q[1:].isdigit():
                url = self.URL + data_result_list[int(q[1:]) - 1].get('link')
                debug(url = url)
                # print(make_colors("URL: " + url, 'ly'))
                data_details = self.detail(url)
                debug(data_details = data_details)
                debug(magnet = data_details.get('magnet'))
                debug(itorrent = data_details.get('itorrent'))
                if data_details.get('magnet'):
                    clipboard.copy(data_details.get('magnet'))  # type: ignore
            elif q[-1] == 'N' and q[:-1].isdigit():
                nlist = int(q[:-1])
                return self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
            elif q[0] == 'N' and q[1:].isdigit():
                nlist = int(q[1:])
                return self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
            elif q == 's':
                qs = raw_input(make_colors("search:", 'ly') + " ")
                if qs:
                    return self.navigator(qs)
            elif q.lower() in ('q', 'quit', 'exit', 'x'):
                sys.exit(make_colors('System Exit ....', 'lw', 'r'))
            elif  q.lower() == 'h':
                self.navigator(proxies = proxies, nlist = nlist, downloadPath = downloadPath, home = home)
            else:
                return self.navigator(q, downloadPath = downloadPath, overwrite = overwrite, nlist = nlist, page_return = page_return, proxies = proxies)
        return self.navigator(None, downloadPath = downloadPath, overwrite = overwrite, nlist = nlist, page_return = page_return, proxies = proxies)

    @classmethod
    def run(self, query_search = None, stype = None, url_query = None, downloadPath = ".", overwrite = None, home = False, nlist = 3, page_return = None, proxies = None):  # type: ignore
        q = self.navigator(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)
        if q and q.lower() in ('exit', 'quit', 'x', 'q'): sys.exit()
        return self.run(query_search, stype, url_query, downloadPath, overwrite, home, nlist, page_return, proxies)

    @classmethod
    def usage(self):  # type: ignore
        parser = argparse.ArgumentParser(prog='torrentdownloads', formatter_class=CustomRichHelpFormatter)
        parser.add_argument('-s', '--search', action = 'store', help = 'Direct Search for')
        parser.add_argument('-n', '--nlist', action = 'store', help = 'Show with list length', type = int)
        parser.add_argument('-d', '--download-path', action = 'store', help = 'Save download to dir')
        parser.add_argument('-x', '--proxies', action = 'store', help = 'use proxies, format: {"http":http://"host:ip", "https":https://"host:ip"}')
        parser.add_argument('-v', '--version', action = 'store_true', help = 'Show this app version number')
        parser.add_argument('--debug', help='Debugging process', action='store_true')

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

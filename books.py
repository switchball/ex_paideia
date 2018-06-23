#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File books.py created on 19:17 2018/5/4

@author: Yichi Xiao
@version: 1.0
"""

import git
import spider  # get PSpider from https://github.com/xianhu/PSpider
import logging
import requests
from lxml import html


uid = '564841'  # yezitao
start_url = f"https://shaishufang.com/index.php/site/main/uid/{uid}/friend/false/category/statusAll/status//type//page/1"
prefix_url = "https://shaishufang.com"


class MyFetcher(spider.Fetcher):
    """
    fetcher module, only rewrite url_fetch()
    """
    def url_fetch(self, priority: int, url: str, keys: dict, deep: int, repeat: int, proxies=None):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,de;q=0.4",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
        }
        cookies = {
            "PHPSESSID": "v2o4136cc9usronkjlepidge41",
            "shaishufang": "NzEzOTUwfGY3MmEwZjE5YWE4ZWM4MTY3YWQ2ZjQ2MGMxMDFkZjk0"
        }
        logging.debug(f'url_fetch {keys} {url}')
        response = requests.get(url, params=None, headers={}, cookies=cookies, data=None, proxies=proxies, timeout=(3.05, 10))
        content = (response.status_code, response.url, response.text)
        return 1, True, content


class MyParser(spider.Parser):
    """
    parser module, only rewrite htm_parse()
    """
    def htm_parse(self, priority: int, url: str, keys: dict, deep: int, content: object):
        status_code, url_now, html_text = content

        logging.debug(f'html_parse {keys} {url}')
        root = html.fromstring(html_text)
        url_list = []
        save_list = []

        if keys['type'] is None:
            book_lis = root.xpath('//ul[@id="booksList"]/li')
            for book_li in book_lis:
                bid = book_li.attrib['id']
                link = book_li.xpath('a/@href')[0]
                url_list.append((prefix_url + link, {"type": 'detail', 'id': str(bid)}, priority))
            print(f'Finding {len(book_lis)} books')

            next_page = root.xpath('//a[@id="pageNext"]/@href')
            next_page = prefix_url + next_page[0] if next_page else None
            if next_page is not None:
                url_list.append((next_page, keys, priority+1))
                print('Finding page ' + next_page)

        elif keys['type'] == 'detail':
            book_title = root.xpath('//div[@id="bookDetail"]//div[@id="attr"]/h2')[0].text
            book_author = ""
            book_press = ""
            book_time = ""
            for li in root.xpath('//div[@id="bookDetail"]//div[@id="attr"]/ul/li'):
                li_text = li.text  # type: str
                if li_text.startswith("作者:"):
                    book_author = li_text[3:]
                elif li_text.startswith("出版社:"):
                    book_press = li_text[4:]
                elif li_text.startswith("出版时间:"):
                    book_time = li_text[5:]
            save_list.append((keys['id'], book_title, "/".join([book_author, book_time, book_press])))

        return 1, url_list, save_list


class MySaver(spider.Saver):
    """
    parser module, only rewrite item_save()
    """
    def item_save(self, url: str, keys: dict, item: (list, tuple)) -> int:
        if keys['type'] == 'detail':
            self._save_pipe.write("|".join([str(col) for col in item]) + "\n")
            self._save_pipe.flush()
            return 1

        logging.warning('FAIL at item_save')
        return -1


def go_spider():
    """
    test spider
    """
    # initial fetcher / parser / saver
    fetcher = MyFetcher(max_repeat=3, sleep_time=5)
    parser = MyParser(max_deep=2)
    saver = MySaver(save_pipe=open("book_info_list.txt", "w", encoding='utf8'))

    # initial web_spider
    web_spider = spider.WebSpider(fetcher, parser, saver, proxieser=None, url_filter=None, monitor_sleep_time=5)

    # add start url
    web_spider.set_start_url(start_url, priority=0, keys={"type": None}, deep=0)

    # start web_spider
    web_spider.start_working(fetcher_num=10)

    # stop web_spider
    # time.sleep(10)
    # web_spider.stop_working()

    # wait for finished
    web_spider.wait_for_finished(is_over=True)
    return


def is_workspace_clean():
    from git import Repo
    r = Repo.init(path)
    return not r.is_dirty()


def first():
    mp = {}
    with open('book_info_list.txt', 'r', encoding='utf8') as f:
        for line in f:
            bid, title, author = line[:-1].split('|')
            mp[bid] = (title, author)
    return mp


def second():
    repo = git.Repo.init(path) 
    print('Pulling from repo ...')
    print(repo.remotes.origin.pull())

    info = []
    pre_table = []
    dur_table = []
    post_table = []
    c = pre_table
    print('Reading file books.md')
    with open(path + '\\books.md', 'r', encoding='utf8') as f:

        for line in f:
            _line = line[:-1].strip()  # type: str
            if _line.startswith("| 编号 |"):
                c = dur_table
            if id(c) == id(dur_table) and (not _line.startswith('|')):
                c = post_table
            if _line.startswith('1:'):
                for kv in _line.split(','):
                    k, v = kv.split(':')
                    info.append(v)
                continue  # bypass append

            c.append(line[:-1])

    return info, (pre_table, dur_table, post_table)


def third(mp, info, file_content):
    # scan entries in m
    print(info)
    print(len(info))
    pre_table, dur_table, post_table = file_content
    n = len(info)
    for bid, entry in mp.items():
        if str(bid) in info:
            pass
        else:
            info.append(bid)
            n += 1
            dur_table.append(f'| {n} | {entry[0]} | {entry[1]} |    |')

    lines = pre_table + dur_table + post_table
    lines.append('    ' + ','.join(f'{k+1}:{v}' for k,v in enumerate(info)))

    with open(path + '\\books.md', 'w', encoding='utf8') as f:
        f.writelines(line + '\n' for line in lines)

    return lines

def read_repo_dir():
    d = "."
    try:
        with open('repo_dir.txt', 'r') as f:
            d = f.read()
    except FileNotFoundError as e:
        d = '.'

    return d.strip()

if __name__ == "__main__":
    path = read_repo_dir()
    second()
    exit(-1)

    if not is_workspace_clean():
        print('You should make sure git workspace clean before you go ahead!')
        exit(-1)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s\t%(levelname)s\t%(message)s")
    print('Crawling ...')
    go_spider()

    m = first()
    print(f'Get {len(m)} entries: {m}')
    a, b = second()
    print(f'Repo has {len(a)} entries: {a}')
    file_content = third(m, a, b)
    print('\n'.join(file_content))

    repo = git.Repo(path)
    index = repo.index
    index.add(['books.md'])
    d = index.diff()
    if len(d) > 0:
        repo.git.commit('-m', 'auto update')
    else:
        print('clean, nothing to commit')

    print('Pushing to repo ...')
    origin = repo.remote('origin')
    origin.push()
    exit()

# You don't know. I don't know.
# What is the παίξειν?

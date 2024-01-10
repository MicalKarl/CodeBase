import sys
import requests
from bs4 import BeautifulSoup
import os
from dllinks import get_html_soup, join_href
from myheaders import headers
import re
from concurrent.futures import ThreadPoolExecutor


g_dl_executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=100)


def dl_image(url, try_time=1):
    img_data = None
    try:
        img_data = requests.get(url, headers=headers).content
    except Exception as e:
        print("[", try_time, "] err download ", url, e)
        img_data = None
    return img_data

def dl_file(url, fp, retry=5):
    if os.path.exists(fp):
        return
    print("dl", url, "->", fp)
    img_data = None
    for t in range(retry):
        img_data = dl_image(url, t)
        if img_data: break
    if not img_data:
        print("failed to download image", url)
        return
    with open(fp, 'wb') as f:
        f.write(img_data)

def th_dl_file(task):
    dl_file(task[0], task[1])

def parse_and_dl(url, dest):
    soup = get_html_soup(url, headers)
    title = soup.find('span', {"id": "thread_subject"}).text
    tasks =[]
    for img in soup.findAll("img"):
        src = img.get('zoomfile', None)
        if src:
            ctile = re.sub(r"[\\\\/:*?\"<>|]", "", title)
            fp = os.path.join(dest, ctile + "-" + os.path.basename(src))
            if not os.path.exists(fp):
                tasks.append((join_href(url, src), fp))
    print("parse", len(tasks), "task(s) for", url)
    if tasks:
       for task in tasks:
           g_dl_executor.submit(dl_file, task[0], task[1])


def parse(fp, dest):
    with open(fp, "r") as f:
        lines = f.readlines()
        urls = set(lines)
        n = len(lines)
        i = 0
        for url in urls:
            i += 1
            print("dl url", i, "/", n, url)
            parse_and_dl(url.strip(), dest)


import time
if __name__ == "__main__":
    fp_urls = sys.argv[1]
    fp_dest = sys.argv[2]
    parse(fp_urls, fp_dest)
    g_dl_executor.shutdown()
    print("all completed for", fp_urls, "->", fp_dest)

import sys
import requests
from bs4 import BeautifulSoup
from myheaders import headers
import time


def get_html_soup(url, in_headers, retry=3):
    r = None
    for  _ in range(retry):
        try:
            r = requests.get(url, allow_redirects=True, headers= headers)
        except Exception as e:
            print("err get soup for", url, e)
            r = None
            time.sleep(0.1)
        if r:   break
    content = "<html><head></head><body>failed</body></html>"
    if r: 
        content = r.text
    return BeautifulSoup(content, 'html.parser')

def join_href(url, href):
    if href.startswith('http'):
        return href
    ix = url.rfind('/')
    pre_url = url[:ix+1]
    return pre_url + href


def parse_model(url):
    print("parse", url, "...")
    soup = get_html_soup(url, headers)
    f = open(sys.argv[4], "a")
    for th in soup.findAll("tbody"):
        alinks = th.findAll('a', {"class": "s xst"})
        if alinks:
            for alink in alinks:
                href = alink['href']
                if href:
                    f.write(join_href(url, href) + '\n')
    f.close()


if __name__ == "__main__":
    url = sys.argv[1]
    s = int(sys.argv[2])
    e = int(sys.argv[3])
    # print(url, s, e)
    for i in range(s, e + 1):
        parse_model(url % i)

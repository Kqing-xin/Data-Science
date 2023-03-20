

from proxypool.schemas.proxy import Proxy
from proxypool.crawlers.base import BaseCrawler
import json
import requests


BASE_URL = 'http://www.goubanjia.com/'


class GoubanjiaCrawler(BaseCrawler):

    def crawl(self):

        content = []

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }

        try:
            response = requests.get("http://proxylist.fatezero.org/proxy.list", headers=header)
            html = response.text
        except requests.exceptions.ConnectionError as e:
            print('Error', e.args)

        lines = html.split("\n")
        # print(lines)
        for line in lines:
            if line.replace(" ", "") != "":
                content.append(json.loads(line))
        # print(content)

        for proxy_info in content:
            host = proxy_info['host']
            port = proxy_info['port']
            print(f"{host}:{port}")
            yield Proxy(host=host, port=port)


    def parse(self, html):

        content = []

        # with open(html, 'r', encoding="utf-8") as f:
        #     lines = f.readlines()
        #     for line in lines:
        #         content.append(json.loads(line))

        lines = html.split("\n")
        # print(lines)
        for line in lines:
            if line.replace(" ","") != "":
                content.append(json.loads(line))
        # print(content)

        for proxy_info in content:
            host = proxy_info['host']
            port = proxy_info['port']
            print(f"{host}:{port}")


if __name__ == '__main__':
    crawler = GoubanjiaCrawler()

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get("http://proxylist.fatezero.org/proxy.list", headers=header)
        html = response.text
    except requests.exceptions.ConnectionError as e:
        print('Error', e.args)

    crawler.parse(html)
    for proxy in crawler.parse(html):
        print(proxy)


    # crawler = GoubanjiaCrawler()
    # crawler.parse(html)



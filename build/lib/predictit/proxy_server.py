"""Run a local proxy server that distributes
   incoming requests to external proxies."""

import asyncio
import aiohttp
from proxybroker import Broker


async def get_pages(urls, proxy_url):
    tasks = [fetch(url, proxy_url) for url in urls]
    for task in asyncio.as_completed(tasks):
        url, content = await task
        print('Done! url: %s; content: %.100s' % (url, content))


async def fetch(url, proxy_url):
    resp = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy_url) as response:
                resp = await response.read()
    except (aiohttp.errors.ClientOSError, aiohttp.errors.ClientResponseError,
            aiohttp.errors.ServerDisconnectedError) as e:
        print('Error. url: %s; error: %r' % (url, e))
    finally:
        return (url, resp)


async def show(proxies,ip_list):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        print('Found proxy: %s' % proxy)
        ip_list.append((proxy.host,proxy.port))
        # tasks.result()[1].host.port

def get_proxy_ips():
    host, port = '127.0.0.1', 8888  # by default
    types = [('HTTP', 'High'), 'HTTPS', 'CONNECT:80']
    codes = [200, 301, 302]

    broker = Broker(max_tries=1)

    proxies = asyncio.Queue()
    broker = Broker(proxies)
    new_list = []
    tasks = asyncio.gather(
        broker.find(types=['HTTP', 'HTTPS'], limit=10),
        show(proxies,new_list))

    # Broker.serve() also supports all arguments that are accepted
    # # Broker.find() method: data, countries, post, strict, dnsbl.
    # broker.serve(host=host, port=port, types=types, limit=100, max_tries=3,
    #              prefer_connect=True, min_req_proxy=5, max_error_rate=0.5,
    #              max_resp_time=8, http_allowed_codes=codes, backlog=100)
    #
    #
    # print(broker.find())
    #
    # # urls = ['http://httpbin.org/get', 'https://httpbin.org/get',
    # #         'http://httpbin.org/redirect/1', 'http://httpbin.org/status/404']
    # #
    # # proxy_url = 'http://%s:%d' % (host, port)
    # # loop.run_until_complete(get_pages(urls, proxy_url))
    #
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    broker.stop()
    return new_list

def start_proxy_server():
    host, port = '127.0.0.1', 8888  # by default
    types = [('HTTP', 'High'), 'HTTPS', 'CONNECT:80']
    codes = [200, 301, 302]

    broker = Broker(max_tries=1)

    # Broker.serve() also supports all arguments that are accepted
    # # Broker.find() method: data, countries, post, strict, dnsbl.
    broker.serve(host=host, port=port, types=types, limit=100, max_tries=3,
                 prefer_connect=True, min_req_proxy=5, max_error_rate=0.5,
                 max_resp_time=8, http_allowed_codes=codes, backlog=100)

    #
    # print(broker.find())
    #
    # # urls = ['http://httpbin.org/get', 'https://httpbin.org/get',
    # #         'http://httpbin.org/redirect/1', 'http://httpbin.org/status/404']
    # #
    # # proxy_url = 'http://%s:%d' % (host, port)
    # # loop.run_until_complete(get_pages(urls, proxy_url))
    #

if __name__ == '__main__':
    start_proxy_server()

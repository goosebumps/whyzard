#!/usr/bin/env python3
# areq.py

"""Asynchronously get links embedded in multiple pages' HMTL."""

import asyncio
from bs4 import BeautifulSoup
import logging
import re
import sys
from typing import IO
import urllib.error
import urllib.parse
import shops
from requests_futures.sessions import FuturesSession

import aiofiles
import aiohttp

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

HREF_RE = re.compile(r'href="(.*?)"')

async def fetch_html(url: str, session: FuturesSession, cookies, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """
    headers = {"User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0)'}
    future = session.get(url, cookies=cookies, headers=headers)
    resp = future.result()
    return resp.text

async def update_products(queue_in: asyncio.Queue, queue_out: asyncio.Queue):
    session = FuturesSession()
    while True:
        product = await queue_in.get()
        if product is None:
            queue_in.task_done()
            await queue_out.put(None)
            break
        queue_in.task_done()
        soup = await get_soup(product.update_url, session, product.shop.cookies)  #     soup = await get_soup(url, session, shop.cookies)
        try:
            updated_product = await product.shop.product_parser(product, soup)
        except Exception as e:
            logger.exception("Exception occured:  %s", getattr(e, "__dict__", {}))
        await queue_out.put(product)
        print(f'updated {product.shop.name} {product.name}')

async def get_soup(url: str, session: FuturesSession, cookies):
    try:
        html = await fetch_html(url=url, session=session, cookies=cookies)
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s | %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
            getattr(e, "args", None),
        )
        return None
    except Exception as e:
        logger.exception("Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {}))
        return None
    else:
        return BeautifulSoup(html, "html.parser")

async def add_one_shop(queue: asyncio.Queue, shop: shops.Shop, search_term: str, session: FuturesSession, **kwargs) -> set:
    """Find HREFs in the HTML of `url`."""
    url = shop.search_url%(search_term)
    soup = await get_soup(url, session, shop.cookies)
    await shop.parser(shop, soup, queue)

async def bulk_crawl_and_write(queue: asyncio.Queue, shoplist: list, search_term: str, **kwargs) -> None:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    session =  FuturesSession()
    tasks = []
    for shop in shoplist:
        tasks.append(
            add_one_shop(queue, shop, search_term, session=session, **kwargs)
        )
    await asyncio.gather(*tasks)
    await queue.put(None)


async def queue_to_list(queue: asyncio.Queue):
    l = []
    while True:
        token = await queue.get()
        if token is None:
            queue.task_done()
            break
        queue.task_done()
        l.append( token)
        print(f'unqueued {token.shop.name} {token.name} {token.abv} {token.volume}')
    return l

async def test_search_and_print():
    search_term  = "deanston"
    queue = asyncio.Queue()
    queue_updated = asyncio.Queue()

    list_task = asyncio.create_task(queue_to_list(queue_updated))
    await bulk_crawl_and_write(queue, shops.shoplist, search_term)
    await update_products(queue, queue_updated)
    print('---- done producing')
    l = await list_task
    print('---- c awaited')
    await queue.join()
    print(f'---- queue joined. Found {len(l)} entries')
    await asyncio.sleep(0.1) #sigh.... this shouldn't be neccessary



if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_search_and_print())



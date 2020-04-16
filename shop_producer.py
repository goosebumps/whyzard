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

import aiofiles
import aiohttp
from aiohttp import ClientSession

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

HREF_RE = re.compile(r'href="(.*?)"')

async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """

    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)
    html = await resp.text()
    return html

async def add_one_shop(queue: asyncio.Queue, shop: shops.Shop, search_term: str, session: ClientSession, **kwargs) -> set:
    """Find HREFs in the HTML of `url`."""
    found = set()
    try:
        url = shop.search_url%(search_term)
        html = await fetch_html(url=url, session=session, **kwargs)
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )
        return found
    except Exception as e:
        logger.exception(
            "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        )
        return found
    else:
        soup = BeautifulSoup(html, "html.parser")
        await shop.parser(soup, queue)

async def bulk_crawl_and_write(queue: asyncio.Queue, shoplist: list, search_term: str, **kwargs) -> None:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    async with ClientSession() as session:
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
        print(f'added {token.name}')
    return l

async def test_search_and_print():
    search_term  = "deanston"
    queue = asyncio.Queue()

    list_task = asyncio.create_task(queue_to_list(queue))
    await bulk_crawl_and_write(queue, shops.shoplist, search_term)
    print('---- done producing')
    l = await list_task
    print('---- c awaited')
    await queue.join()
    print(f'---- queue joined. Found {len(l)} entries')
    await asyncio.sleep(0.1) #sigh.... this shouldn't be neccessary



if __name__ == "__main__":
    asyncio.run(test_search_and_print())



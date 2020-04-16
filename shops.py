import asyncio
from bs4 import BeautifulSoup
import requests
import re
from currency import StringToCurrency
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
from collections import namedtuple

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

Shop = namedtuple("Shop", ["name", "cookies", "search_url", "parser"])
ShopResults = namedtuple("ShopResults", ["name", "url", "image", "price", "abv"])

def remove_whitespace(s):
    return re.sub(r"\s\s+", " ", s)


async def parse_d12(soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("a", class_="product_top")
    # results = []
    for prod in all_products_soup:
        price = prod.find("span", class_="product_aanbieding_prijs").get_text()
        price = StringToCurrency(price)
        name = prod.find("div", class_="product_title").get_text()
        print(f"d12 {name}")
        url = "https://drankdozijn.nl" + prod.get("href")
        image = prod.find("div", class_="product_image").find("img").get("src")
        abv = None
        await queue.put(ShopResults(name, url, image, price, abv))



async def parse_passie_voor_whisky(soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("div", class_="product-container")

    for prod in all_products_soup:
        price = (
            prod.find("div", class_="pro_second_box")
            .find("meta", itemprop="price")
            .get("content")
        )
        name = prod.find("div", class_="pro_second_box").find(
            "h5").find("a").get_text()
        url = prod.find("div", class_="pro_second_box").find(
            "h5").find("a").get("href")
        image = (
            prod.find("div", class_="pro_first_box").find(
                "a").find("img").get("src")
        )
        price = StringToCurrency(price)
        abv = None
        await queue.put(ShopResults(name, url, image, price, abv))


# async def get_d12_results(shopname, searchterm):
#     page = requests.get(
#         "https://drankdozijn.nl/zoeken?zoekterm=" + searchterm,
#         cookies=dict(validatie_cookie="true"), headers=headers
#     )
#     soup = BeautifulSoup(page.content, "html.parser")
#     all_products_soup = soup.find_all("a", class_="product_top")
#     results = []
#     for prod in all_products_soup:
#         price = prod.find("span", class_="product_aanbieding_prijs").get_text()
#         price = StringToCurrency(price)
#         name = prod.find("div", class_="product_title").get_text()
#         url = "https://drankdozijn.nl" + prod.get("href")
#         image = prod.find("div", class_="product_image").find("img").get("src")
#         result = [
#             {"name": name, "price": price, "url": url,
#                 "shop": shopname, "img": image}
#         ]
#         await queue.put(result)
#         print(f"{shopname} produced {name}")


# async def get_theoldpipe_results(shopname, searchterm):
#     page = requests.get(
#         "https://www.theoldpipe.com/nl/search/" + searchterm, headers=headers)
#     soup = BeautifulSoup(page.content, "html.parser")
#     all_products_soup = soup.find_all("div", class_="product-block-inner")

#     results = []
#     for prod in all_products_soup:
#         price = prod.find("span", class_="price-new").get_text()
#         price = StringToCurrency(price)
#         name = prod.find("h3").find("a").get_text()
#         url = prod.find("h3").find("a").get("href")
#         image = prod.find("div", class_="image noborder").find(
#             "img").get("src")
#         result = [
#             {"name": name, "price": price, "url": url,
#                 "shop": shopname, "img": image}
#         ]
#         await queue.put(result)
#         print(f"{shopname} produced {name}")


# async def get_whiskysite_results(shopname, searchterm):
#     page = requests.get(
#         "https://www.whiskysite.nl/nl/search/" + searchterm,
#         cookies=dict(age_check="done"), headers=headers
#     )
#     soup = BeautifulSoup(page.content, "html.parser")
#     all_products_soup = soup.find_all("div", class_="product-block")
#     results = []
#     for prod in all_products_soup:
#         name = prod.find("a", class_="title").get_text()
#         price = prod.find("div", class_="product-block-price").get_text()
#         price = StringToCurrency(price)
#         url = prod.find("a", class_="title").get("href")
#         name = remove_whitespace(name)
#         image = prod.find(
#             "div", class_="product-block-image").find("img").get("src")
#         result = [
#             {"name": name, "price": price, "url": url,
#                 "shop": shopname, "img": image}
#         ]
#         await queue.put(result)
#         print(f"{shopname} produced {name}")


# async def get_whiskybase_shop_results(queue, shopname, searchterm):
#     page = requests.get(
#         "https://shop.whiskybase.com/nl/search/" + searchterm,
#         cookies=dict(age_check="done"), headers=headers
#     )
#     soup = BeautifulSoup(page.content, "html.parser")
#     all_products_soup = soup.find_all(
#         "div", class_="product-block")
#     results = []
#     for prod in all_products_soup:
#         name = prod.find("a", class_="title").get_text()
#         price = prod.find("div", class_="product-block-price").get_text()
#         price = StringToCurrency(price)
#         url = prod.find("a", class_="title").get("href")
#         name = remove_whitespace(name)
#         image = prod.find(
#             "div", class_="product-block-image").find("img").get("src")
#         result = [
#             {"name": name, "price": price, "url": url,
#                 "shop": shopname, "img": image}
#         ]
#         await queue.put(result)
#         print(f"{shopname} produced {name}")

# async def get_product_vinabc(queue, prod, shopname):
#     name = prod['title']
#     url = prod['href']
#     image = BeautifulSoup(prod['product_img']).find("img").get("src")
#     name = prod['title']
#     #now open product page to obtain price
#     prodpage = requests.get(url)
#     prodsoup = BeautifulSoup(prodpage.content, "html.parser")
#     price = prodsoup.find('span', itemprop='price').get("content")
#     abv = remove_whitespace(prodsoup.find('span', id='hikashop_product_custom_value_31').get_text())
#     result = [
#         {"name": name, "price": price, "url": url,
#             "shop": shopname, "img": image}
#     ]
#     await queue.put(result)
#     print(f"{shopname} produced {name}")


# async def get_vinabc_shop_results(queue, shopname, searchterm):
#     page = requests.get(
#         r"https://vinabc.nl/nl/?option=com_universal_ajax_live_search&lang=nl-NL&module_id=177&search_exp=" + searchterm + r"&dojo_preventCache=1",
#         cookies=dict(age_check="done"), headers=headers
#     )
#     decoded_string = page.content.decode("utf8")
#     decoded_string = decoded_string[decoded_string.index('['):] # strip the header text
#     decoded_string = decoded_string[:decoded_string.rindex(']')+1] # strip the header text
#     products = json.loads(decoded_string)
#     results = []
#     prod_producers = [asyncio.create_task(get_product_vinabc(queue, prod, shopname)) for prod in products]
#     await asyncio.gather(*prod_producers)


# async def get_drankgigant_results(queue, shopname, searchterm):
#     page = requests.get(
#         "https://www.drankgigant.nl/catalogsearch/result/?q=" + searchterm,
#         cookies=dict(age_check="done"), headers=headers
#     )
#     soup = BeautifulSoup(page.content, "html.parser")
#     all_products_soup = soup.find_all(
#         "div", class_="item product product-item")
#     results = []
#     for prod in all_products_soup:
#         name = prod.find("a", class_="product-item-link").get_text()
#         price = prod.find("span", class_="price").get_text()
#         price = StringToCurrency(price)
#         url = prod.find(
#             "a", class_="product-item-link").get("href")
#         name = remove_whitespace(name)
#         image = prod.find(
#             "img", class_="photo image").get("src")
#         result = [
#             {"name": name, "price": price, "url": url,
#                 "shop": shopname, "img": image}
#         ]
#         await queue.put(result)
#         print(f"{shopname} produced {name}")


# async def get_shop_results(searchterm, shopname=None, minPrice=None, maxPrice=None):
#     queue = asyncio.Queue()

#     if not searchterm or searchterm == "None":
#         return

#     shopnames = (
#         shoplist.keys() if shopname == "all" or shopname == "None" or shopname is None else [
#             shopname]
#     )

#     producers = [asyncio.create_task(get_drankgigant_results(queue, shop, searchterm)) for shop in shopnames]

#     consumers = [asyncio.create_task(consumer(queue))
#                  for _ in range(10)]

#     # with both producers and consumers running, wait for
#     # the producers to finish
#     await asyncio.gather(*producers)
#     print('---- done producing')

#     # wait for the remaining tasks to be processed
#     # await queue.join()

#     # cancel the consumers, which are now idle
#     for c in consumers:
#         c.cancel()

shoplist = [
    Shop(
        "d12", 
        dict(validatie_cookie="true"),
        "https://drankdozijn.nl/zoeken?zoekterm=%s",
        parse_d12
        ),
    # Shop(
    #     "the_old_pipe", 
    #     None,
    #     "https://www.theoldpipe.com/nl/search/%s",
    #     parse_the_old_pipe
    #     ),
    # Shop(
    #     "whiskysite", 
    #     dict(age_check="done"),
    #     "https://www.whiskysite.nl/nl/search/%s",
    #     parse_whiskysite
    #     ),
    Shop(
        "passie_voor_whisky", 
        dict(age_check="done"),
        "https://www.passievoorwhisky.nl/nl/zoeken?controller=search&orderby=position&orderway=desc&search_query=%s",
        parse_passie_voor_whisky #probably same as whiskysite
        ),
    # Shop(
    #     "whiskybase_shop", 
    #     None,
    #     "https://shop.whiskybase.com/nl/search/%s",
    #     parse_whiskybase_shop
    #     ),
    # Shop(
    #     "drankgigant", 
    #     None,
    #     "https://www.drankgigant.nl/catalogsearch/result/?q=%s",
    #     parse_drankgigant
    #     ),
    # Shop(
    #     "vinabc", 
    #     None,
    #     "https://shop.whiskybase.com/nl/search/%s",
    #     parse_vinabc
    #     )
]

if __name__ == "__main__":
    asyncio.run(get_shop_results("Linkwood", shopname="vinabc"))
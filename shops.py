import asyncio
from bs4 import BeautifulSoup
import requests
import re
from currency import StringToCurrency
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
from recordtype import recordtype

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

Shop = recordtype("Shop", ["name", "cookies", "search_url", "parser", "product_parser"])
Product = recordtype("Product", ["shop", "name", "url", "update_url", "image", "price", "abv", "volume", "wb_link", "wb_rating"], default=None)

def find_abv(text):
    try:
        regex = r"\b(\d+[.,]?\d+)\s?(?:%|percent\b)"
        matches = re.search(regex, text)
        return matches.group(0)
    except:
        return None 

def find_vol_cl(text):
    try:
        regex = r"\b(\d+[.,]?\d+)\s?(?:cl|CL|Cl\b)"
        matches = re.search(regex, text)
        return matches.group(0)
    except:
        return None

def find_vol_liter(text):
    try:
        regex = r"\b(\d+[.,]?\d+)\s?(?:ltr|liter|Liter\b)"
        matches = re.search(regex, text)
        return matches.group(0)
    except:
        return None

def remove_whitespace(s):
    return re.sub(r"\s\s+", " ", s)


async def parse_d12_product(product: Product, soup: BeautifulSoup):
    data = json.loads(str(soup))
    try:
        abv_object = next(item for item in data['features'] if item ["description"] == "Alcoholpercentage")
        product.abv = abv_object["value"]["description"]
    except:
        pass
    try:
        vol_object = next(item for item in data['features'] if item ["description"] == "Inhoud")
        product.volume = vol_object["value"]["description"]
    except:
        pass


async def parse_the_old_pipe_product(product: Product, soup: BeautifulSoup):
    prod_text = soup.find("div", class_="page information active").find("p").get_text()
    product.abv = find_abv(prod_text)
    product.volume = find_vol_cl(prod_text)

async def parse_whiskysite_product(product: Product, soup: BeautifulSoup):
    try: 
        prod_text = soup.find("p", class_="producttext").get_text()
    except:
        prod_text = soup.find("div", class_="product-content").find("p").get_text()

    product.abv = find_abv(prod_text)
    product.volume = find_vol_liter(prod_text)

async def parse_whiskybase_product(product: Product, soup: BeautifulSoup):
    try: 
        prod_text = soup.find("p", class_="producttext").get_text()
    except:
        prod_text = soup.find("div", class_="product-content").find("p").get_text()

    product.abv = find_abv(prod_text)
    product.volume = find_vol_liter(prod_text)

async def parse_passie_voor_whisky_product(product: Product, soup: BeautifulSoup):
    abv_text = soup.find("div", class_="s_spec_title_block", text="Alcoholpercentage").find_next("div").get_text()
    product.abv = find_abv(abv_text)

    vol_text = soup.find("div", class_="s_spec_title_block", text="Inhoudsmaat").find_next("div").get_text()
    product.volume = find_vol_liter(vol_text)

async def parse_whiskybase_shop_product(product: Product, soup: BeautifulSoup):
    raise NotImplementedError()

async def parse_drankgigant_product(product: Product, soup: BeautifulSoup):
    raise NotImplementedError()

async def parse_vinabc_product(product: Product, soup: BeautifulSoup):
    raise NotImplementedError()

async def parse_d12(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("a", class_="product_top")
    for prod in all_products_soup:
        p = Product(shop=shop)
        p.price = prod.find("span", class_="product_aanbieding_prijs").get_text()
        p.price = StringToCurrency(p.price)
        p.name = prod.find("div", class_="product_title").get_text()
        alias =  prod.get("href")
        p.url = "https://drankdozijn.nl" + alias
        p.update_url = "https://es-api.drankdozijn.nl/product?country=NL&language=nl&page_template=artikel&alias=%s" % alias.split('/')[-1]
        p.image = prod.find("div", class_="product_image").find("img").get("src")
        await queue.put(p)

async def parse_passie_voor_whisky(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("div", class_="product-container")

    for prod in all_products_soup:
        p = Product(shop=shop)
        p.price = (
            prod.find("div", class_="pro_second_box")
            .find("meta", itemprop="price")
            .get("content")
        )
        p.name = prod.find("div", class_="pro_second_box").find(
            "h5").find("a").get_text()
        p.url = prod.find("div", class_="pro_second_box").find(
            "h5").find("a").get("href")
        p.image = (
            prod.find("div", class_="pro_first_box").find(
                "a").find("img").get("src")
        )
        p.price = StringToCurrency(p.price)
        await queue.put(p)


async def parse_the_old_pipe(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("div", class_="product-block-inner")

    for prod in all_products_soup:
        p = Product(shop=shop)
        p.price = prod.find("span", class_="price-new").get_text()
        p.price = StringToCurrency(p.price)
        p.name = prod.find("h3").find("a").get_text()
        p.url = prod.find("h3").find("a").get("href")
        p.image = prod.find("div", class_="image noborder").find(
            "img").get("src")
        await queue.put(p)


async def parse_whiskysite(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all("div", class_="product-block")
    for prod in all_products_soup:
        p = Product(shop=shop)
        p.name = prod.find("a", class_="title").get_text()
        p.price = prod.find("div", class_="product-block-price").get_text()
        p.price = StringToCurrency(p.price)
        p.url = prod.find("a", class_="title").get("href")
        p.name = remove_whitespace(p.name)
        p.image = prod.find(
            "div", class_="product-block-image").find("img").get("src")
        await queue.put(p)



async def parse_whiskybase_shop(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all(
        "div", class_="product-block")
    for prod in all_products_soup:
        p = Product(shop=shop)
        p.name = prod.find("a", class_="title").get_text()
        p.price = prod.find("div", class_="product-block-price").get_text()
        p.price = StringToCurrency(p.price)
        p.url = prod.find("a", class_="title").get("href")
        p.name = remove_whitespace(p.name)
        p.image = prod.find(
            "div", class_="product-block-image").find("img").get("src")
        await queue.put(p)


async def parse_vinabc_product(queue, prod, shop: Shop):
    name = prod['title']
    url = prod['href']
    image = BeautifulSoup(prod['product_img']).find("img").get("src")
    name = prod['title']
    #now open product page to obtain price
    prodpage = requests.get(url)
    prodsoup = BeautifulSoup(prodpage.content, "html.parser")
    price = prodsoup.find('span', itemprop='price').get("content")
    abv = remove_whitespace(prodsoup.find('span', id='hikashop_product_custom_value_31').get_text())
    await queue.put(p)

async def parse_vinabc(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    # decoded_string = page.content.decode("utf8")
    decoded_string = soup.text.encode().decode("unicode_escape").replace("\n","")
    decoded_string = decoded_string[decoded_string.index('['):] # strip the header text
    decoded_string = decoded_string[:decoded_string.rindex(']')+1] # strip the header text
    products = json.loads(decoded_string)
#     prod_producers = [asyncio.create_task(parse_vinabc_product(queue, prod, shop)) for prod in products]
    await asyncio.gather(*prod_producers)


async def parse_drankgigant(shop: Shop, soup: BeautifulSoup, queue: asyncio.Queue):
    all_products_soup = soup.find_all(
        "div", class_="item product product-item")
    for prod in all_products_soup:
        p = Product(shop=shop)
        name = prod.find("a", class_="product-item-link").get_text()
        p.price = prod.find("span", class_="price").get_text()
        p.price = StringToCurrency(p.price)
        p.url = prod.find(
            "a", class_="product-item-link").get("href")
        p.name = remove_whitespace(name)
        p.image = prod.find(
            "img", class_="photo image").get("src")
        await queue.put(p)


shoplist = [
    Shop(
        "d12", 
        dict(validatie_cookie="true"),
        "https://drankdozijn.nl/zoeken?zoekterm=%s",
        parse_d12,
        parse_d12_product,
        ),
    Shop(
        "the_old_pipe", 
        None,
        "https://www.theoldpipe.com/nl/search/%s",
        parse_the_old_pipe,
        parse_the_old_pipe_product
        ),
    Shop(
        "whiskysite",
        dict(age_check="done"),
        "https://www.whiskysite.nl/nl/search/%s",
        parse_whiskysite,
        parse_whiskysite_product
        ),
    Shop(
        "passie_voor_whisky",   # werkt nog niet
        dict(age_check="done"),
        "https://www.passievoorwhisky.nl/nl/zoeken?controller=search&orderby=position&orderway=desc&search_query=%s",
        parse_passie_voor_whisky,
        parse_passie_voor_whisky_product
        ),
    Shop(
        "whiskybase_shop", 
        None,
        "https://shop.whiskybase.com/nl/search/%s",
        parse_whiskysite,
        parse_whiskybase_product
        ),
    Shop(
        "drankgigant", 
        None,
        "https://www.drankgigant.nl/catalogsearch/result/?q=%s",
        parse_drankgigant,
        parse_drankgigant_product
        ),
    # Shop(
    #     "vinabc", 
    #     None,
    #     "https://shop.whiskybase.com/nl/search/%s",
    #     parse_vinabc,
    #     parse_vinabc_product
    #     )
]

if __name__ == "__main__":
    asyncio.run(get_shop_results("Linkwood", shopname="vinabc"))
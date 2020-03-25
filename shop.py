from bs4 import BeautifulSoup
import requests
import re
from currency import StringToCurrency
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def remove_whitespace(s):
    return re.sub(r"\s\s+", " ", s)

#     "bol":
#     {"url": "https://www.bol.com/nl/s/algemeen/zoekresultaten/Ntt/",
#      "title": "//a[@class='product-title px_list_page_product_click']/text()",
#      "price": "//span[@class='promo-price']/text()",


def get_passie_voor_whisky_results(shopname, searchterm):
    page = requests.get(
        "https://www.passievoorwhisky.nl/nl/zoeken?controller=search&orderby=position&orderway=desc&search_query="
        + searchterm, headers=headers
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("div", class_="product-container")
    results = []
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
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results


def get_d12_results(shopname, searchterm):
    page = requests.get(
        "https://drankdozijn.nl/zoeken?zoekterm=" + searchterm,
        cookies=dict(validatie_cookie="true"), headers=headers
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("a", class_="product_top")
    results = []
    for prod in all_products_soup:
        price = prod.find("span", class_="product_aanbieding_prijs").get_text()
        price = StringToCurrency(price)
        name = prod.find("div", class_="product_title").get_text()
        url = "https://drankdozijn.nl" + prod.get("href")
        image = prod.find("div", class_="product_image").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results


def get_theoldpipe_results(shopname, searchterm):
    page = requests.get(
        "https://www.theoldpipe.com/nl/search/" + searchterm, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("div", class_="product-block-inner")

    results = []
    for prod in all_products_soup:
        price = prod.find("span", class_="price-new").get_text()
        price = StringToCurrency(price)
        name = prod.find("h3").find("a").get_text()
        url = prod.find("h3").find("a").get("href")
        image = prod.find("div", class_="image noborder").find(
            "img").get("src")
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results


def get_whiskysite_results(shopname, searchterm):
    page = requests.get(
        "https://www.whiskysite.nl/nl/search/" + searchterm,
        cookies=dict(age_check="done"), headers=headers
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("div", class_="product-block")
    results = []
    for prod in all_products_soup:
        name = prod.find("a", class_="title").get_text()
        price = prod.find("div", class_="product-block-price").get_text()
        price = StringToCurrency(price)
        url = prod.find("a", class_="title").get("href")
        name = remove_whitespace(name)
        image = prod.find(
            "div", class_="product-block-image").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results


def get_whiskybase_shop_results(shopname, searchterm):
    page = requests.get(
        "https://shop.whiskybase.com/nl/search/" + searchterm,
        cookies=dict(age_check="done"), headers=headers
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all(
        "div", class_="product-block")
    results = []
    for prod in all_products_soup:
        name = prod.find("a", class_="title").get_text()
        price = prod.find("div", class_="product-block-price").get_text()
        price = StringToCurrency(price)
        url = prod.find("a", class_="title").get("href")
        name = remove_whitespace(name)
        image = prod.find(
            "div", class_="product-block-image").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results

def get_vinabc_shop_results(shopname, searchterm):
    page = requests.get(
        r"https://vinabc.nl/nl/?option=com_universal_ajax_live_search&lang=nl-NL&module_id=177&search_exp=" + searchterm + r"&dojo_preventCache=1",
        cookies=dict(age_check="done"), headers=headers
    )
    decoded_string = page.content.decode("utf8")
    decoded_string = decoded_string[decoded_string.index('['):] # strip the header text
    decoded_string = decoded_string[:decoded_string.rindex(']')+1] # strip the header text
    products = json.loads(decoded_string)
    results = []
    for prod in products:
        name = prod['title']
        url = prod['href']
        image = BeautifulSoup(prod['product_img']).find("img").get("src")
        name = prod['title']
        #now open product page to obtain price
        prodpage = requests.get(url)
        prodsoup = BeautifulSoup(prodpage.content, "html.parser")
        price = prodsoup.find('span', itemprop='price').get("content")
        abv = remove_whitespace(prodsoup.find('span', id='hikashop_product_custom_value_31').get_text())
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image, "abv": abv}
        ]
    return results

def get_drankgigant_results(shopname, searchterm):
    page = requests.get(
        "https://www.drankgigant.nl/catalogsearch/result/?q=" + searchterm,
        cookies=dict(age_check="done"), headers=headers
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all(
        "div", class_="item product product-item")
    results = []
    for prod in all_products_soup:
        name = prod.find("a", class_="product-item-link").get_text()
        price = prod.find("span", class_="price").get_text()
        price = StringToCurrency(price)
        url = prod.find(
            "a", class_="product-item-link").get("href")
        name = remove_whitespace(name)
        image = prod.find(
            "img", class_="photo image").get("src")
        results += [
            {"name": name, "price": price, "url": url,
                "shop": shopname, "img": image}
        ]
    return results


shoplist = {
    "d12": get_d12_results,
    "the_old_pipe": get_theoldpipe_results,
    "whiskysite": get_whiskysite_results,
    "passie_voor_whisky": get_passie_voor_whisky_results,
    "whiskybase_shop": get_whiskybase_shop_results,
    "drankgigant": get_drankgigant_results,
    "vinabc": get_vinabc_shop_results,
}


def get_shop_results(searchterm, shopname=None, minPrice=None, maxPrice=None):
    results = []

    if not searchterm or searchterm == "None":
        return results

    shopnames = (
        shoplist.keys() if shopname == "all" or shopname == "None" or shopname is None else [
            shopname]
    )

    with ThreadPoolExecutor(max_workers=len(shoplist)) as e:
        futures = {
            e.submit(shoplist[sn], sn, searchterm): sn for sn in shopnames}

        for future in as_completed(futures):
            sn = futures[future]
            try:
                res = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (sn, exc))
            else:
                print('%r page is %d entries' % (sn, len(res)))
                results += res

    # filter prices
    if (minPrice):
        results = [r for r in results if r["price"] >= minPrice]
    if (maxPrice):
        results = [r for r in results if r["price"] <= maxPrice]
    return results


if __name__ == "__main__":
    searchterm = "deanston"
    results = []
    # results = get_shop_results("d12", searchterm)
    # results += get_shop_results("the_old_pipe", searchterm)
    # results = get_shop_results("whiskysite", searchterm)
    # results = get_shop_results("passie_voor_whisky", searchterm)
    # results = get_whiskybase_shop_results("whiskybas_shop", searchterm)
    # results = get_drankgigant_results("drankgigant", searchterm)
    results = get_vinabc_shop_results("vinabc", searchterm)

    # results = get_shop_results()
    [print(r) for r in results]

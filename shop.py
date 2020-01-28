from bs4 import BeautifulSoup
import requests
import re


#     "bol":
#     {"url": "https://www.bol.com/nl/s/algemeen/zoekresultaten/Ntt/",
#      "title": "//a[@class='product-title px_list_page_product_click']/text()",
#      "price": "//span[@class='promo-price']/text()",


def remove_whitespace(s):
    return re.sub(r"\s\s+", " ", s)


def get_passie_voor_whisky_results(shopname, search_term):
    page = requests.get(
        "https://www.passievoorwhisky.nl/nl/zoeken?controller=search&orderby=position&orderway=desc&search_query="
        + search_term
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
        name = prod.find("div", class_="pro_second_box").find("h5").find("a").get_text()
        url = prod.find("div", class_="pro_second_box").find("h5").find("a").get("href")
        image = (
            prod.find("div", class_="pro_first_box").find("a").find("img").get("src")
        )
        price = remove_whitespace(price)
        results += [
            {"name": name, "price": price, "url": url, "shop": shopname, "img": image}
        ]
    return results


def get_d12_results(shopname, search_term):
    page = requests.get(
        "https://drankdozijn.nl/zoeken?zoekterm=" + search_term,
        cookies=dict(validatie_cookie="true"),
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("a", class_="product_top")
    results = []
    for prod in all_products_soup:
        price = prod.find("span", class_="product_aanbieding_prijs").get_text()
        name = prod.find("div", class_="product_title").get_text()
        url = "https://drankdozijn.nl" + prod.get("href")
        image = prod.find("div", class_="product_image").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url, "shop": shopname, "img": image}
        ]
    return results


def get_theoldpipe_results(shopname, search_term):
    page = requests.get("https://www.theoldpipe.com/nl/search/" + search_term)
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("div", class_="product-block-inner")

    results = []
    for prod in all_products_soup:
        price = prod.find("span", class_="price-new").get_text()
        name = prod.find("h3").find("a").get_text()
        url = prod.find("h3").find("a").get("href")
        image = prod.find("div", class_="image noborder").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url, "shop": shopname, "img": image}
        ]
    return results


def get_whiskysite_results(shopname, search_term):
    page = requests.get(
        "https://www.whiskysite.nl/nl/search/" + search_term,
        cookies=dict(age_check="done"),
    )
    soup = BeautifulSoup(page.content, "html.parser")
    all_products_soup = soup.find_all("div", class_="product-block")
    results = []
    for prod in all_products_soup:
        name = prod.find("a", class_="title").get_text()
        price = prod.find("div", class_="product-block-price").get_text()
        url = prod.find("a", class_="title").get("href")
        price = remove_whitespace(price)
        name = remove_whitespace(name)
        image = prod.find("div", class_="product-block-image").find("img").get("src")
        results += [
            {"name": name, "price": price, "url": url, "shop": shopname, "img": image}
        ]
    return results


shop_list = {
    "d12": get_d12_results,
    "the_old_pipe": get_theoldpipe_results,
    "whiskysite": get_whiskysite_results,
    "passie_voor_whisky": get_passie_voor_whisky_results,
}


def get_shop_results(shopname, search_term):
    reslt = []
    if not search_term or search_term == "None":
        return reslt

    shopnames = (
        shop_list.keys() if shopname == "all" or shopname == "None" else [shopname]
    )
    for sn in shopnames:
        reslt += shop_list[sn](sn, search_term)
    return reslt


if __name__ == "__main__":
    search_term = "deanston"
    results = []
    # results = get_shop_results("d12", search_term)
    # results += get_shop_results("the_old_pipe", search_term)
    # results = get_shop_results("whiskysite", search_term)
    results = get_shop_results("passie_voor_whisky", search_term)
    [print(r) for r in results]

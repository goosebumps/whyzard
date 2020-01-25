from threading import Thread
from flask import Flask, request, escape
# import requests
import dominate as dom
from dominate.tags import *
import shop


def result_to_table(doc, result):
    with doc:
        with div(cls="container"):
            with div(cls="row"):
                div('shop', cls="col-sm")
                div('name', cls="col-lg")
                div('price', cls="col-sm")
            for i in result:
                with div(cls="row"):
                    div(a(i['shop'], href=i['url']), cls="col-sm")
                    div(a(i['name'], href=i['url']), cls="col-sm")
                    div(a(i['price'], href=i['url']), cls="col-sm")
                    div(a(img(src=i['img'], cls="img", width="35"),
                          href=i['url']), cls="col-sm")


app = Flask(__name__, static_folder='.', static_url_path='')


@app.route("/")
def root():
    return searchshoppage("d12", escape("ben nevis"))


@app.route("/<search_term>")
def searchpage(search_term):
    return searchshoppage("all", search_term)


@app.route("/<shopname>/<search_term>")
def searchshoppage(shopname, search_term):
    doc = dom.document(title='Whyzard')

    with doc.head:
        link(rel='stylesheet',
             href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css", integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh", crossorigin="anonymous")
        script(src="https://code.jquery.com/jquery-3.4.1.slim.min.js",
               integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n", crossorigin="anonymous")
        script(src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
               integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo", crossorigin="anonymous")
        script(src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
               integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6", crossorigin="anonymous")

    reslt = shop.get_shop_results(shopname, search_term)

    with doc:
        with nav(cls="navbar navbar-expand-lg navbar-light bg-light"):
            a("all", href=f'/{search_term}',
                cls="av-item nav-link active")
            for i in shop.shop_list.keys():
                a(i.title(), href=f'/{i}/{search_term}',
                  cls="av-item nav-link active")
            # with form(cls="form-inline my-2 my-lg-0"):
            #     input(cls="form-control mr-sm-2", type="search_term", action="/")
            #     button(
            #         "zoek", cls="btn btn-outline-success my-2 my-sm-0", type="submit")
    result_to_table(doc.body, reslt)

    print(doc)
    return doc.render()
    # return doc.tostring()

# Remember from flask import request
# for /request and POST method
@app.route('/request', methods=['GET', 'POST'])
def request():
    payload = request.data
#  data = json.loads(payload)
    data = payload
    return jsonify(data)


# start listening
if __name__ == "__main__":
    # app.run(debug=True, use_reloader=False, port='3000', host='0.0.0.0')
    Thread(target=app.run,args=("0.0.0.0",8080)).start()
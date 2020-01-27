# importing modules
from flask import Flask, render_template, escape
import shop

# declaring app name
app = Flask(__name__)


@app.route("/")
def root():
    return searchshoppage("d12", escape("ben nevis"))


@app.route("/<search_term>")
def searchpage(search_term):
    return searchshoppage("all", search_term)


@app.route("/<shopname>/<search_term>")
def searchshoppage(shopname, search_term):
    shop_result = shop.get_shop_results(shopname, search_term)

    return render_template(
        "index.html",
        shop_list=shop.shop_list,
        shop_result=shop_result,
        search_term=search_term,
    )


# start listening
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port="3000", host="127.0.0.1")


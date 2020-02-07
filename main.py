# importing modules
from flask import Flask, render_template, escape, flash, redirect
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
import shop
import forms

# declaring app name
csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)
Bootstrap(app)
app.config['SECRET_KEY'] = "datraadjenooitpannekoek"

@app.route("/", methods=['GET', 'POST'])
def root():
    form = forms.SearchForm()
    searchterm = form.searchterm.data
    shopname = form.shopname.data
    minPrice = form.minPrice.data
    maxPrice = form.maxPrice.data
    return searchshoppage(searchterm, shopname, minPrice, maxPrice)


@app.route("/<searchterm>", methods=['GET', 'POST'])
@app.route("/<searchterm>/<maxPrice>", methods=['GET', 'POST'])
@app.route("/<searchterm>/<maxPrice>/<minPrice>", methods=['GET', 'POST'])
@app.route("/<searchterm>/<maxPrice>/<minPrice>/<shopname>", methods=['GET', 'POST'])
def searchshoppage(searchterm, shopname=None, minPrice=None, maxPrice=None):
    form = forms.SearchForm()
    shopresult = shop.get_shop_results(
        searchterm, shopname, minPrice, maxPrice)
    return render_template(
        "index.html",
        shoplist=shop.shoplist,
        shopresult=shopresult,
        searchterm=searchterm,
        form=form
    )


# start listening
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port="3000", host="127.0.0.1")

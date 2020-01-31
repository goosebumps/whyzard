# importing modules
from flask import Flask, render_template, escape, flash, redirect
from flask_bootstrap import Bootstrap
import shop
import forms

# declaring app name
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = "datraadjenooitpannekoek"

@app.route("/", methods=['GET', 'POST'])
def searchshoppage():
    form = forms.SearchForm()
    shop_result = shop.get_shop_results(form.shopname.data, form.searchterm.data)
    return render_template(
        "index.html",
        shop_list=shop.shop_list,
        shop_result=shop_result,
        search_term=form.searchterm.data,
        form=form
    )


# start listening
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port="3000", host="127.0.0.1")


from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired
import shop

class SearchForm(FlaskForm):
    searchterm = StringField('Zoekterm', validators=[DataRequired()])
    shopname = RadioField('Shop', choices=[("all", "all")] + list(zip(shop.shop_list, shop.shop_list)))
    submit = SubmitField('Zoek')
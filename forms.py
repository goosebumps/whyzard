from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DecimalField, SubmitField
from wtforms.validators import DataRequired
import shop

class SearchForm(FlaskForm):
    searchterm = StringField('Zoekterm', validators=[DataRequired()])
    shopname = RadioField('Shop', choices=[("all", "all")] + list(zip(shop.shop_list, shop.shop_list)))
    minPrice = DecimalField('Min prijs', places=0)
    maxPrice = DecimalField('Max prijs', places=0)
    submit = SubmitField('Zoek')
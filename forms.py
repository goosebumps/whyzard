from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DecimalField, SubmitField
from wtforms.validators import DataRequired
import shops


class SearchForm(FlaskForm):
    searchterm = StringField('Zoekterm', validators=[DataRequired()])
    shopname = RadioField(
        'Shop', choices=[("all", "all")] + list(zip(shops.shopdict, shops.shopdict)))
    minPrice = DecimalField('Min prijs', places=0)
    maxPrice = DecimalField('Max prijs', places=0)
    submit = SubmitField('Zoek')

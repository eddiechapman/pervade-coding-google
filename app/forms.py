from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField

class CodingForm(FlaskForm):
    pervasive_data = BooleanField('Pervasive data')
    data_science = BooleanField('Data science')
    big_data = BooleanField('Big data')
    case_study = BooleanField('Flag for PRIM&R case study')
    data_synonyms = StringField('Data synonyms')
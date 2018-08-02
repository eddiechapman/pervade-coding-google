from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField

class CodingForm(FlaskForm):
    data_synonyms = StringField('Data synonyms', description='Please seperate values with a semicolon')
    pervasive_data = BooleanField('Pervasive data')
    data_science = BooleanField('Data science')
    big_data = BooleanField('Big data')
    case_study = BooleanField('Flag for PRIM&R case study')
    award_relevance = BooleanField('This award is not relevant to PERVADE')
    user = SelectField('User', choices=[('Default','Please select your name'), ('Eddie','Eddie'), ('Else','Stranger')])
    submit = SubmitField('Submit')
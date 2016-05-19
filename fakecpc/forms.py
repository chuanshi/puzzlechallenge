from flask_wtf import Form
from wtforms import StringField, validators

def check_alphanumeric(form, field):
    if not field.data.isalnum():
        raise validators.ValidationError('Answer must be alphanumeric')

class GuessForm(Form):
    guess = StringField('Guess:', validators=[
        validators.DataRequired(),
        validators.Length(max=79),
        check_alphanumeric,
        ])



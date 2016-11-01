from flask_wtf import Form
from wtforms import StringField, validators

def check_ascii(form, field):
    # stolen from stackoverflow
    isascii = lambda s: len(s) == len(s.encode())
    if not isascii(field.data):
        raise validators.ValidationError('Answer must be ASCII')
    # if not field.data.isalnum():
    #    raise validators.ValidationError('Answer must be alphanumeric')

class GuessForm(Form):
    guess = StringField('Guess:', validators=[
        validators.DataRequired(),
        validators.Length(max=79),
        check_ascii,
        ])



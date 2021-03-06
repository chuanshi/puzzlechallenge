import datetime
from fakecpc import db

class Puzzle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    #answer = db.Column(db.String(80))
    link = db.Column(db.String(768))
    #reply = db.Column(db.String(80))
    # answers = db.relationship("Answers",uselist=False,backref="puzzle")

    def __repr__(self):
        return "<Puzzle '{}'>".format(self.name)

class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puzzle_id = db.Column(db.Integer, db.ForeignKey('puzzle.id'))
    puzzle = db.relationship('Puzzle', backref=db.backref('answers', lazy='dynamic'))
    answer = db.Column(db.String(80))
    correct = db.Column(db.Boolean)
    response = db.Column(db.String(768))

    def __init__(self, puzzle, answer, correctness, response):
        self.puzzle = puzzle
        self.answer = answer
        self.correct = correctness
        self.response = response


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puzzle_id = db.Column(db.Integer, db.ForeignKey('puzzle.id'))
    puzzle = db.relationship('Puzzle', backref=db.backref('guesses', lazy='dynamic'))
    guess = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime)

    def __init__(self, puzzle, guess, timestamp=None):
        self.puzzle = puzzle
        self.guess = guess
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.utcnow()

    def __repr__(self):
        return "<Guess '{}' on '{}'>".format(self.guess, repr(self.puzzle))

class Migration(db.Model):
    ver_num = db.Column(db.Integer, primary_key=True)



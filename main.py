import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)
#db.init_app(app)

class Puzzle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    answer = db.Column(db.String(80))
    link = db.Column(db.String(768))

    def __repr__(self):
        return "<Puzzle '{}'>".format(self.name)

class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puzzle_id = db.Column(db.Integer, db.ForeignKey('puzzle.id'))
    puzzle = db.relationship('Puzzle', backref=db.backref('guesses', lazy='dynamic'))
    timestamp = db.Column(db.DateTime)

    def __init__(self, puzzle, guess, timestamp=None):
        self.puzzle = puzzle
        self.guess = guess
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

    def __repr__(self):
        return "<Guess '{}' on '{}'>".format(self.guess, repr(self.puzzle))

class Migration(db.Model):
    ver_num = db.Column(db.Integer, primary_key=True)

@app.route('/dummy')
def hello_world():
    insert_dummy_data()
    return 'Hello World!'

@app.route('/clear')
def clear_db():
    for p in Puzzle.query.all():
        db.session.delete(p)
    db.session.commit()
    return "DB cleared!"

@app.route('/puzzles/<int:puzzle_id>')
def puzzle_page(puzzle_id):
    puzzle = Puzzle.query.get_or_404(puzzle_id)
    guesses = puzzle.guesses
    for g in guesses:
        g.correct = g.guess == puzzle.answer
    return render_template("puzzle_page.html", puzzle=puzzle, guesses=guesses)

@app.route("/")
def puzzle_list():
    return render_template('puzzles.html', puzzles=Puzzle.query.all())

@app.route("/<path:anystring>")
def anystring(anystring):
    return anystring

def create_puzzle_and_guess_tables():
    db.metadata.create_all(db.engine, tables=[
        Puzzle.__table__,
        Guess.__table__,
    ])

def insert_dummy_data():
    puzzle = Puzzle()
    puzzle.name = "Helloooo"
    puzzle.answer = "THISISANANSWER"
    puzzle.link = "http://www.google.com"
    db.session.add(puzzle)
    db.session.commit()

MIGRATIONS = [
    create_puzzle_and_guess_tables,
]

def prepare_migrations_table():
    try:
        migrations = Migration.query.all()
    except sqlalchemy.exc.OperationalError as e:
        db.metadata.create_all(db.engine, tables=[
            Migration.__table__,
        ])
        initial_state = Migration()
        initial_state.ver_num = 0
        db.session.add(initial_state)
        db.session.commit()

def run_migrations():
    migrations_rows = Migration.query.all()
    if len(migrations_rows) != 1:
        raise ValueError("Migrations table must have exactly one row")
    row = migrations_rows[0]
    applied = row.ver_num
    extent = len(MIGRATIONS)
    if applied == extent:
        return
    if applied > extent:
        raise ValueError("DB version is newer than this code, aborting")
    for func in MIGRATIONS[applied:]:
        func()
        row.ver_num = row.ver_num + 1
        db.session.add(row)
        db.session.commit()


if __name__ == '__main__':
    prepare_migrations_table()
    run_migrations()

    #db.create_all()
    app.run(debug=True)

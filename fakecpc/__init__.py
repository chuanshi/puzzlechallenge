import csv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

app = Flask(__name__)

db = SQLAlchemy(app)
#db.init_app(app)

from .models import Puzzle, Guess, Migration, Answers

def create_puzzle_and_guess_tables():
    db.metadata.create_all(db.engine, tables=[
        Puzzle.__table__,
        Guess.__table__,
    ])

def create_answers_table():
    db.metadata.create_all(db.engine, tables=[
        Answers.__table__,
    ])


MIGRATIONS = [
    create_puzzle_and_guess_tables,
    create_answers_table,
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

def migrate():
    prepare_migrations_table()
    run_migrations()

def populate_puzzles():
    puzzlecsv = "puzzles.csv"
    with open(puzzlecsv, 'rt') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i > 0:
                name, link, correct_answer, luggage = row
                puzzle = Puzzle()
                puzzle.name, puzzle.link = name, link
                answers = Answers(puzzle, correct_answer, True, luggage)
                answers.response = "CORRECT!  Your luggage piece is: " + luggage
                if len(Puzzle.query.filter(Puzzle.name == puzzle.name).all()) < 1:
                    db.session.add(puzzle)
                    db.session.add(answers)
                    db.session.commit()

def populate_answers():
    answercsv = "other_answers.csv"
    with open(answercsv, 'rt') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            puzzle_name, answer, correctness, reply = row
            puzzle = Puzzle.query.filter(Puzzle.name == puzzle_name).all()
            puzzle = puzzle[0]
            if correctness == "True":
                correct = True
            elif correctness == "False":
                correct = False
            else:
                app.logging.error("invalid correctness in answer table" + str(row))
                raise
            if correct:
                reply = "CORRECT!  Your luggage piece is: " + reply
            answers = Answers(puzzle, answer, correct, reply)
            db.session.add(answers)
            db.session.commit()



app.migrate = migrate
app.populate_puzzles = populate_puzzles
app.populate_answers = populate_answers

import fakecpc.views

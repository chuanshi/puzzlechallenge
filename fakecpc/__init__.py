from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

app = Flask(__name__)

db = SQLAlchemy(app)
#db.init_app(app)

from .models import Puzzle, Guess, Migration

def create_puzzle_and_guess_tables():
    db.metadata.create_all(db.engine, tables=[
        Puzzle.__table__,
        Guess.__table__,
    ])

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

def migrate():
    prepare_migrations_table()
    run_migrations()

app.migrate = migrate

import fakecpc.views

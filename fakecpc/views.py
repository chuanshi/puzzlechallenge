import datetime

from flask import render_template, request, redirect

from . import app, db
from .forms import GuessForm
from .models import Puzzle, Guess

def insert_dummy_data():
    puzzle = Puzzle()
    puzzle.name = "Helloooo"
    puzzle.answer = "THISISANANSWER"
    puzzle.link = "http://www.google.com"
    db.session.add(puzzle)
    db.session.commit()

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

@app.route('/puzzles/<int:puzzle_id>', methods=("GET", "POST"))
def puzzle_page(puzzle_id):
    puzzle = Puzzle.query.get_or_404(puzzle_id)
    form = GuessForm()
    if form.validate_on_submit():
        last_allowed_guess_time = datetime.datetime.utcnow()- datetime.timedelta(seconds=15)
        very_recent_guess = Guess.query.filter(Guess.timestamp > last_allowed_guess_time).first()
        if not very_recent_guess:
            guess = Guess(puzzle, form.guess.data.upper())
            db.session.add(guess)
            db.session.commit()
            return redirect(request.path)
        else:
            form.guess.errors.append("slow down there, sonny!")
    guesses = puzzle.guesses.all()
    for g in guesses:
        g.correct = g.guess == puzzle.answer
    return render_template("puzzle_page.html", puzzle=puzzle, guesses=guesses, form=form)

@app.route("/")
def puzzle_list():
    return render_template('puzzles.html', puzzles=Puzzle.query.all())

@app.route("/<path:anystring>")
def anystring(anystring):
    return anystring



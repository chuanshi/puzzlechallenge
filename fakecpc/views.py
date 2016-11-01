import datetime

from flask import render_template, request, redirect

from . import app, db
from .forms import GuessForm
from .models import Puzzle, Guess, Answers

def insert_dummy_data():
    puzzle = Puzzle()
    puzzle.name = "Helloooo"
    puzzle.answer = "THISISANANSWER"
    puzzle.link = "http://www.google.com"
    puzzle.reply = "LUGGAGE"
    db.session.add(puzzle)
    db.session.commit()

#@app.route('/dummy')
def hello_world():
    insert_dummy_data()
    return 'Hello World!'

#@app.route('/clear')
def clear_db():
    for p in Puzzle.query.all():
        db.session.delete(p)
    db.session.commit()
    for a in Answers.query.all():
        db.session.delete(a)
    db.session.commit()
    for g in Guess.query.all():
        db.session.delete(g)
    db.session.commit()
    return "DB cleared!"

@app.route('/puzzles/<int:puzzle_id>', methods=("GET", "POST"))
def puzzle_page(puzzle_id):
    puzzle = Puzzle.query.get_or_404(puzzle_id)
    form = GuessForm()
    if form.validate_on_submit():
        last_allowed_guess_time = datetime.datetime.utcnow()- datetime.timedelta(seconds=5)
        very_recent_guess = Guess.query.filter(Guess.timestamp > last_allowed_guess_time).first()
        if not very_recent_guess:
            guess = Guess(puzzle, form.guess.data.upper().replace(' ',''))
            db.session.add(guess)
            db.session.commit()
            return redirect(request.path)
        else:
            form.guess.errors.append("slow down there, sonny!")
    guesses = puzzle.guesses.all()
    for g in guesses:
        known_answer = Answers.query.filter_by(puzzle_id=puzzle_id,answer=g.guess).first()
        if known_answer is None:
            g.correct = "INCORRECT"
        else:
            g.correct = known_answer.response
        #if g.guess == puzzle.answer:
        #    g.correct = "CORRECT!  Your luggage piece is: " + puzzle.reply
        #else:
        #    g.correct = "INCORRECT"
        # app.logger.error("blah error" + g.guess + g.correct)
    return render_template("puzzle_page.html", puzzle=puzzle, guesses=guesses, form=form)

@app.route("/")
def puzzle_list():
    luggage_recovered = 0
    puzzles = Puzzle.query.all()
    for p in puzzles:
        p.solved = False
        guesses = p.guesses
        for g in guesses:
            known_answer = Answers.query.filter_by(puzzle_id=p.id,answer=g.guess).first()
            if known_answer is None:
                continue
            elif known_answer.correct == True:
                if p.id in [4,27]:
                    luggage_recovered += 5
                else:
                    luggage_recovered += 1
                p.solved = True
                break

    return render_template('puzzles.html', puzzles=Puzzle.query.all(),luggage_recovered=luggage_recovered)

@app.route("/<path:anystring>")
def anystring(anystring):
    return anystring



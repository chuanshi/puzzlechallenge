import os

from fakecpc import app

PWD = os.path.dirname(os.path.abspath(__file__))
RANDOM_FILE = os.path.join(PWD, "secret_key")

if not os.path.exists(RANDOM_FILE):
    with open(RANDOM_FILE, "wb") as f:
        f.write(os.urandom(16))

DB_FILE = os.path.join(PWD, "prod.db")
sqlite_uri = 'sqlite:///{}'.format(DB_FILE)

app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
with open(RANDOM_FILE, "rb") as f:
    app.config["SECRET_KEY"] = f.read()

if __name__ == '__main__':
    app.migrate()
    app.populate_puzzles()
    app.populate_answers()
    app.run(debug=True)

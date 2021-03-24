import re
from hashlib import blake2b

from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'IHS CSC'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    pk = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))
    decks = db.relationship(
        'Deck',
        back_populates='owner',
        cascade='all, delete',
        passive_deletes=True,
    )


class Deck(db.Model):
    __tablename__ = 'decks'

    pk = db.Column(db.Integer, primary_key=True)
    owner_pk = db.Column(db.Integer, db.ForeignKey('users.pk', ondelete='CASCADE'))
    owner = db.relationship('User', back_populates='decks')
    name = db.Column(db.String(100))
    desc = db.Column(db.Text())
    cards = db.relationship(
        'Card',
        back_populates='deck', 
        cascade='all, delete',
        passive_deletes=True,
    )


class Card(db.Model):
    __tablename__ = 'cards'

    pk = db.Column(db.Integer, primary_key=True)
    deck_pk = db.Column(db.Integer, db.ForeignKey('decks.pk', ondelete='CASCADE'))
    deck = db.relationship('Deck', back_populates='cards')
    front = db.Column(db.Text())
    back = db.Column(db.Text())


@app.route('/')
def home():
    pk = session.get('user_pk', None)

    user = None
    if pk is not None:
        user = User.query.filter_by(pk=pk).one()

    return render_template('home.html', user=user)


@app.route('/usercreate', methods=['GET', 'POST'])
def usercreate():
    username_error = None
    email_error = None

    if request.method == 'POST':
        next_page = request.form.get('next', None)

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(username) > 25:
            username_error = 'Username is too long (limit is 25 chars)'        

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, email):
            email_error = 'Not a valid email address'
        
        password_hash = blake2b(password.encode('utf-8')).hexdigest()

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            username_error = 'Username is not unique'
        
        if username_error is not None or email_error is not None:
            return render_template('usercreate.html', username=username, email=email, password=password, username_error=username_error, email_error=email_error, next_page=next_page)

        session['user_pk'] = new_user.pk
        
        if next_page is not None:
            return redirect(next_page)
        
        return redirect(url_for('home'))

    else:
        next_page = request.args.get('next', None)

        username = ''
        email = ''
        password = ''

        return render_template('usercreate.html', username=username, email=email, password=password, username_error=username_error, email_error=email_error, next_page=next_page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username_error = None
    password_error = None

    if request.method == 'POST':
        next_page = request.form.get('next', None)

        username = request.form['username']
        password = request.form['password']

        user = None
        try:
            user = User.query.filter_by(username=username).one()
        except NoResultFound:
            username_error = 'No such user exists.'
        
        if user is not None:
            password_hash = blake2b(password.encode('utf-8')).hexdigest()
            if password_hash != user.password_hash:
                password_error = 'Wrong password.'
        
        if username_error is not None or password_error is not None:
            return render_template('login.html', username=username, password=password, username_error=username_error, password_error=password_error, next_page=next_page)

        session['user_pk'] = user.pk

        if next_page is not None:
            return redirect(next_page)
        
        return redirect(url_for('home'))
    
    else:
        next_page = request.args.get('next', None)

        username = ''
        password = ''

        return render_template('login.html', username=username, password=password, username_error=username_error, password_error=password_error, next_page=next_page)


@app.route('/logout')
def logout():
    next_page = request.args.get('next', None)

    session.pop('user_pk', None)

    if next_page is not None:
        return redirect(next_page)
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()

    app.run(debug=True)
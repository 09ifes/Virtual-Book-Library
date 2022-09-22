from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import os
import sqlite3


app = Flask(__name__)
all_books = []
book_id = 0


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

def create_table():
    db = sqlite3.connect("book-collection.db")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE books(id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE,"
                   " author varchar(250) NOT NULL, rating FLOAT NOT NULL)")


def unique_id():
    """Generates unique id to avoid conflict in db"""
    book_id = 0
    all_ids = []
    db = sqlite3.connect("book-collection.db")
    cursor = db.cursor()
    db_data = cursor.execute("SELECT id FROM books").fetchall()
    for n in db_data:
        all_ids.append(n[0])
    for n in all_ids:
        if n > book_id:
            book_id = n
    book_id += 1
    return book_id


class BookForm(FlaskForm):
    book = StringField(label='Book Name', validators=[DataRequired()])
    author = StringField(label='Book Author', validators=[DataRequired()])
    rating = StringField(label='Rating', validators=[DataRequired()])
    add_book = SubmitField(label='Add Book')
    new_rating = StringField()
    change_rating = SubmitField()

# create_table()

@app.route('/', methods=['GET','POST'])
def home():
    global all_books
    """Retrieves book data from database and displays on the homepage"""
    db = sqlite3.connect("book-collection.db")
    cursor = db.cursor()
    all_books = []
    book_form = BookForm()
    new_rating = book_form.new_rating.data
    if request.method == "POST":
        """Checks for new entries to add to database, and any entries to be updated"""
        if book_form.book.data is None:
            pass
        else:
            try:
                cursor.execute(
                    f"INSERT INTO books VALUES({unique_id()}, '{book_form.book.data}', '{book_form.author.data}', '{book_form.rating.data}')")
                db.commit()
            except sqlite3.IntegrityError:
                pass
        cursor.execute(f"UPDATE books SET rating='{new_rating}' WHERE id={book_id} ")
        db.commit()
    db_data = cursor.execute("SELECT id, title, author, rating FROM books").fetchall()
    n = 0
    for row in db_data:     # Uses data from database to create key:value data structure, to be used in index.html
        n += 1
        book = {
          'number': n,
              'id': row[0],
            'name': row[1],
          'author': row[2],
          'rating': row[3]
        }
        all_books.append(book)
    return render_template("index.html", all_books=all_books, length=len(all_books))

@app.route('/add', methods=["GET","POST"])
def add():
    book_form = BookForm()
    return render_template('add.html', form=book_form)

@app.route('/edit', methods=["GET","POST"])
def edit():
    """Data edited in edit.html gets updated on the homepage"""
    global book_id
    book_form = BookForm()
    book_id = request.args.get('id')
    db = sqlite3.connect("book-collection.db")
    cursor = db.cursor()
    book_data = cursor.execute(f"SELECT title, author, rating FROM books WHERE id={book_id}").fetchone()
    return render_template('edit.html', book=book_data, form=book_form)

@app.route('/delete', methods=["GET"])
def delete():
    book_id = request.args.get('id')
    db = sqlite3.connect("book-collection.db")
    cursor = db.cursor()
    try:
        cursor.execute(f"DELETE FROM books WHERE id={book_id}")
    except sqlite3.OperationalError:
        pass
    db.commit()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)












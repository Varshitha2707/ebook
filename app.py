from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'my_secret_key'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

db = SQLAlchemy(app)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    pdf = db.Column(db.String(100), nullable=False)

# Customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# ADMIN LOGIN AND DASHBOARD
@app.route('/admin_login', methods = ['GET', 'POST'])
def admin_login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        ausername = request.form['ausername']
        apassword = request.form['apassword']

        if ausername == ADMIN_USERNAME and apassword == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('admin_login'))
    
    books = Book.query.all()
    users = Customer.query.all()
    admin_name = ADMIN_USERNAME
    return render_template('admin_dashboard.html', books=books, admin_dashboard=admin_name)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# ADD BOOK
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pdf = request.files['pdf']

        new_book = Book(title=title, author=author, pdf=pdf.filename)
        db.session.add(new_book)
        db.session.commit()

        pdf.save(f'static/pdfs/{pdf.filename}')

        return redirect(url_for('admin_dashboard'))

    return render_template('add_book.html')

# UPDATE/EDIT BOOK
@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get(id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('update_book.html', book=book)

# VIEW/READ BOOK
@app.route('/view_book/<int:id>')
def view_book(id):
    book = Book.query.get(id)
    return render_template('view_book.html', book=book)

# DISPLAY BOOK LIST
@app.route('/display_books')
def display_books():
    books = Book.query.all()
    return render_template('display_books.html', books=books)

# DELETE BOOK
@app.route('/delete_book/<int:id>')
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# CUSTOMER SIGNUP
@app.route('/customer_signup', methods=['GET', 'POST'])
def customer_signup():
    # if 'logged_in' in session and session['logged_in']:
    #     return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not Customer.query.filter_by(username=username).first():
            new_customer = Customer(username=username, password=password)
            db.session.add(new_customer)
            db.session.commit()

            # session['logged_in'] = True
            # session['username'] = username

            return redirect(url_for('customer_login'))

    return render_template('customer_signup.html')

# CUSTOMER LOGIN
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        customer = Customer.query.filter_by(username=username, password=password).first()

        if customer:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('customer_dashboard'))

    return render_template('customer_login.html')

# CUSTOMER DASHBOARD
@app.route('/customer_dashboard')
def customer_dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('customer_login'))
    
    books = Book.query.all()
    return render_template('customer_dashboard.html', books=books)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
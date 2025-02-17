from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    work = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    time = db.Column(db.Time, nullable=False)
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add this line

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)  # Add this line

@app.route("/")
def home():
    if 'user_id' in session:
        todo_list = Todo.query.filter_by(user_id=session['user_id']).all()  # Filter by user_id
        return render_template("base.html", todo_list=todo_list)
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return "Username already exists"
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/add", methods=["POST"])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form.get("title")
    work = request.form.get("work")
    date_str = request.form.get("date")
    time_str = request.form.get("time")
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    time_obj = datetime.strptime(time_str, '%H:%M').time()
    new_todo = Todo(title=title, work=work, date=date_obj, time=time_obj, complete=False, user_id=session['user_id'])  # Add user_id here
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todo = Todo.query.filter_by(id=todo_id, user_id=session['user_id']).first()  # Add user_id filter
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    todo = Todo.query.filter_by(id=todo_id, user_id=session['user_id']).first()  # Add user_id filter
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
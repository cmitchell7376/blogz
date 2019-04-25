from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:chuck@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hi'

class Blog (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,text,owner):
        self.title = title
        self.text = text
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blog = db.relationship('Blog' , backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['main', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def newSignUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '' or password == '' or verify == '':
            flash('Either Username or Password left blank')
            return redirect('/signup')
        elif len(username) < 3 or len(password) < 3:
            flash('Either Username or Password less than 3 characters long')
            return redirect('/signup')
        elif password != verify:
            flash("Passwords don't match")
            return render_template('signup.html', username = username)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            flash('User alreday exist')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Password incorrect')
            return render_template('login.html', username=username)
        elif username == '' or password == '':
            flash('Either username or password left blink')
            return render_template('login.html')
        else:
            flash('Username does not exist')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/main')
def index():
    return render_template('/index.html')

@app.route('/blog', methods=['POST' , 'GET'])
def blog():
    error_title = ''
    error_text = ''


    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_text = request.form['blog_text']

        owner = User.query.filter_by(username=session['username']).first()

        if blog_title == '':
            error_title = " no title"
            return render_template("newpost.html", error_title = error_title , blog_text = blog_text)

        if blog_text == '':
            error_text = " no text"
            return render_template("newpost.html", error_text = error_text , blog_title = blog_title)
        else:

            blog_entry = Blog(blog_title,blog_text, owner)
            db.session.add(blog_entry)
            db.session.commit()
            list_tmp = Blog.query.all()
            id = str(len(list_tmp)) 
            return redirect('/newpage?id={0}'.format(id))

    blog_entry = Blog.query.all()
    return render_template("blog.html", blog_entry = blog_entry) 

@app.route('/newpage')
def newpage():
    id = int(request.args.get('id'))
    blog_id = Blog.query.filter_by(id = id).all()
    return render_template('page.html', titles = blog_id)

@app.route('/newpost')
def entry():
    return render_template("newpost.html")

@app.route('/logout')
def logout():
    del session['username']
    return redirect("/blog")


if __name__ == '__main__':
    app.run()
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

def signup_vaildate(username, password, verify):
    if username == '' and password == '' and verify == '':
        flash('No username and No password','error')
        return redirect('/signup')
    elif username == '':
        flash('No username', 'error')
        return redirect('/signup')
    elif password == '':
        flash('No password', 'error')
        return render_template('signup.html', username = username)
    elif len(username) < 3:
        flash('Username less than 3 characters long', 'error')
        return redirect('/signup')
    elif len(password) < 3:
        flash('Password less than 3 characters long', 'error')
        return render_template('signup.html', username = username)
    elif password != verify:
        flash("Passwords don't match", 'error')
        return render_template('signup.html', username = username)

@app.before_request
def require_login():
    allowed_routes = ['index', 'signup', 'login', 'blog', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    user = User.query.all()
    return render_template('index.html', user = user)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        error = signup_vaildate(username,password,verify)
        if not error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('User alreday exist','error')
                return redirect('/signup')

    return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # error check
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Password incorrect','error')
            return render_template('login.html', username=username)
        elif username == '' and password == '':
            flash('No username and No password', 'error')
            return render_template('login.html')
        elif username == '':
            flash('No username', 'error')
            return render_template('login.html')
        elif password == '':
            flash('No password','error')
            return render_template('login.html', username=username)
        else:
            flash('Username does not exist', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/blog', methods=['POST' , 'GET'])
def blog():
    id_string = request.args.get('id')
    user_name = request.args.get('user')

    if id_string:
        # gets individual object 
        id_num = int(id_string)
        blog_list = Blog.query.filter_by(id = id_num).all()
        blog_object = blog_list[0]

        # pulls id apply them to filters
        user_id = blog_object.owner_id
        user = User.query.filter_by(id = user_id).all()
        blog = Blog.query.filter_by(id = id_num).all()
        return render_template('blogentry.html', blogs = blog, names = user)

    elif user_name:
        #gets individual object
        user_list = User.query.filter_by(username = user_name).all()
        user_object = user_list[0]

        # pulls id apply them to filters
        user_id = user_object.id
        user = User.query.filter_by(id = user_id).all()
        entries = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('userblogs.html', entries = entries, names = user)

    blog_entry = Blog.query.all()
    user = User.query.all()
    return render_template("blog.html", blog_entry = blog_entry, names =user) 

@app.route('/newpost', methods=['GET', 'POST'])
def entry():
    error_title = ''
    error_text = ''

    # error check
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_text = request.form['blog_text']

        owner = User.query.filter_by(username=session['username']).first()
        if blog_title == '' and blog_text ==  '':
            error_title = ' no title'
            error_text = ' no text'
            return render_template("newpost.html", error_title = error_title , error_text = error_text)

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
            return redirect('/blog?id={0}'.format(id))

    return render_template("newpost.html")

@app.route('/logout')
def logout():
    del session['username']
    return redirect("/blog")


@app.before_request
def require_login():
    allowed_routes = ['index', 'signup', 'login', 'blog', 'static']
    if not('username' in session or request.endpoint in allowed_routes):
        return redirect('/login')

if __name__ == '__main__':
    app.run()